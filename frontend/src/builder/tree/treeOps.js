/**
 * Pure helpers for manipulating the builder's JSON node tree.
 *
 * The tree matches the renderer schema exactly:
 *   { type: "...", props: {...}, children?: [...] }
 *
 * Every function here is pure — it returns a new tree, never mutates.
 * Nodes are addressed by a `path` (array of child indices) from the root.
 *
 *   tree = { type: 'section', children: [ {type:'container', children:[A, B]} ] }
 *   path = [0, 1]  →  points at B
 *   path = []      →  points at the root
 */

/** Stable random id for selection tracking. (Not persisted to backend.) */
let _idCounter = 0;
export function newId() { return `n${Date.now().toString(36)}-${_idCounter++}`; }

/** Recursively attach a `_id` to every node so the editor can key/select them.
 *  Leaves the rest of the node (type, props, children) untouched. */
export function hydrateIds(node) {
  if (!node || typeof node !== 'object') return node;
  const out = { ...node, _id: node._id || newId() };
  if (Array.isArray(out.children)) {
    out.children = out.children.map(hydrateIds);
  }
  return out;
}

/** Strip the runtime-only `_id` field before sending the tree to the server. */
export function stripIds(node) {
  if (!node || typeof node !== 'object') return node;
  // eslint-disable-next-line no-unused-vars
  const { _id, ...rest } = node;
  if (Array.isArray(rest.children)) {
    rest.children = rest.children.map(stripIds);
  }
  return rest;
}

/** Return the node at the given path (or null if the path is invalid). */
export function getAt(root, path) {
  let node = root;
  for (const i of path) {
    if (!node || !Array.isArray(node.children) || i >= node.children.length) return null;
    node = node.children[i];
  }
  return node;
}

/** Find the path to the first node matching `_id`. Returns null if not found. */
export function findPathById(root, id, prefix = []) {
  if (!root) return null;
  if (root._id === id) return prefix;
  if (!Array.isArray(root.children)) return null;
  for (let i = 0; i < root.children.length; i++) {
    const p = findPathById(root.children[i], id, [...prefix, i]);
    if (p) return p;
  }
  return null;
}

/** Return a deep-cloned tree with `mutator(node)` applied to the node at path.
 *  `mutator` may return a new node object or mutate in-place — the clone
 *  walker ensures callers don't have to care. */
export function mapAt(root, path, mutator) {
  if (!root) return root;
  if (path.length === 0) {
    const next = { ...root };
    const result = mutator(next);
    return result || next;
  }
  const [idx, ...rest] = path;
  if (!Array.isArray(root.children)) return root;
  const nextChildren = root.children.slice();
  nextChildren[idx] = mapAt(nextChildren[idx], rest, mutator);
  return { ...root, children: nextChildren };
}

/** Insert `child` into the node at `parentPath` at position `index`. */
export function insertAt(root, parentPath, index, child) {
  return mapAt(root, parentPath, (parent) => {
    const children = Array.isArray(parent.children) ? parent.children.slice() : [];
    const clampedIndex = Math.max(0, Math.min(index, children.length));
    children.splice(clampedIndex, 0, child);
    parent.children = children;
  });
}

/** Remove the node at `path` and return { tree, removed }. */
export function removeAt(root, path) {
  if (path.length === 0) return { tree: root, removed: null };
  const parentPath = path.slice(0, -1);
  const index      = path[path.length - 1];
  let removed = null;
  const tree = mapAt(root, parentPath, (parent) => {
    if (!Array.isArray(parent.children)) return;
    const children = parent.children.slice();
    removed = children[index] || null;
    children.splice(index, 1);
    parent.children = children;
  });
  return { tree, removed };
}

/** Move the node at `fromPath` to be a child of `toParentPath` at `toIndex`.
 *  Handles the tricky case where the source path shifts after removal. */
export function moveTo(root, fromPath, toParentPath, toIndex) {
  if (pathStartsWith(toParentPath, fromPath) || pathsEqual(fromPath, toParentPath)) {
    // Can't move a node into itself or one of its own descendants.
    return root;
  }

  const { tree: afterRemove, removed } = removeAt(root, fromPath);
  if (!removed) return root;

  // Adjust target index if removal shifted siblings.
  let adjustedIndex = toIndex;
  if (pathsEqual(fromPath.slice(0, -1), toParentPath)) {
    const fromIdx = fromPath[fromPath.length - 1];
    if (fromIdx < toIndex) adjustedIndex = toIndex - 1;
  }

  return insertAt(afterRemove, toParentPath, adjustedIndex, removed);
}

/** Duplicate the node at `path`: inserts a clone immediately after it. */
export function duplicateAt(root, path) {
  if (path.length === 0) return root;
  const node = getAt(root, path);
  if (!node) return root;
  const clone = hydrateIds(stripIds(node));          // new ids throughout
  const parentPath = path.slice(0, -1);
  const index = path[path.length - 1] + 1;
  return insertAt(root, parentPath, index, clone);
}

/** Shallow-merge `propsPatch` into the node at `path`. */
export function setPropsAt(root, path, propsPatch) {
  return mapAt(root, path, (node) => {
    node.props = { ...(node.props || {}), ...propsPatch };
  });
}

/** Replace the children array at `path` entirely (used by the DnD drop). */
export function setChildrenAt(root, path, children) {
  return mapAt(root, path, (node) => { node.children = children; });
}

// ── path helpers ─────────────────────────────────────────────────────────────

export function pathsEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
  return true;
}

export function pathStartsWith(candidate, prefix) {
  if (candidate.length < prefix.length) return false;
  for (let i = 0; i < prefix.length; i++) {
    if (candidate[i] !== prefix[i]) return false;
  }
  return true;
}

// ── Factories ────────────────────────────────────────────────────────────────

/** Build a fresh node from a catalogue entry, filling default props
 *  and recursively creating any mandatory children. */
export function newNodeFromCatalogue(catalogueEntry) {
  const props = {};
  for (const [name, schema] of Object.entries(catalogueEntry.props || {})) {
    if (schema.default !== undefined) props[name] = schema.default;
  }
  return hydrateIds({
    type:     catalogueEntry.type,
    props,
    children: catalogueEntry.allowsChildren ? [] : undefined,
  });
}

/** The canvas itself is always a root `div` with children. */
export function emptyRoot() {
  return hydrateIds({ type: 'div', props: {}, children: [] });
}
