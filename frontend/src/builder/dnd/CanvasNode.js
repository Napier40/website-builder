/**
 * CanvasNode — recursive view of a single JSON tree node in the editor.
 *
 * Rendering philosophy
 * ────────────────────
 * We don't re-implement Bootstrap in the editor — the authentic, themed
 * preview lives in the <Canvas> iframe next door. Here we show a compact
 * labelled outline of each node so you can see the tree shape, select,
 * drag, and rearrange components.
 *
 * Drop event contract
 * ───────────────────
 * Every drop emits a single call to `onDrop(target, item)` where:
 *   target = { parentPath: number[], index: number }
 *   item   = { kind: 'new', componentType } | { kind: 'move', fromPath }
 * The BuilderShell owns the tree and applies the mutation.
 */
import React from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { ItemTypes } from './ItemTypes';
import DropZone from './DropZone';

export default function CanvasNode({
  node,
  path,
  catalogueByType,
  selectedPath,
  onSelect,
  onDrop,           // (target, item) → shell mutates tree
  onDelete,         // (path)
  onDuplicate,      // (path)
}) {
  const entry = catalogueByType[node.type];
  const label = entry?.label || node.type;
  const icon  = entry?.icon  || 'bi-box';
  const allowsChildren = !!entry?.allowsChildren || path.length === 0; // root is always a container

  const isRoot = path.length === 0;
  const isSelected =
    !isRoot && selectedPath &&
    selectedPath.length === path.length &&
    selectedPath.every((v, i) => v === path[i]);

  // ── Drag: this node can be moved (root excluded) ──
  const [{ isDragging }, dragRef] = useDrag(() => ({
    type: ItemTypes.CANVAS_NODE,
    item: { kind: 'move', fromPath: path },
    canDrag: !isRoot,
    collect: (monitor) => ({ isDragging: monitor.isDragging() }),
  }), [JSON.stringify(path), isRoot]);

  // ── Drop inside: when the user drops ON (not between) this container ──
  const [{ isOverInside }, dropInsideRef] = useDrop(() => ({
    accept: allowsChildren ? [ItemTypes.PALETTE_ITEM, ItemTypes.CANVAS_NODE] : [],
    drop: (item, monitor) => {
      if (monitor.didDrop()) return;
      // Fallback drop at end of children
      const idx = Array.isArray(node.children) ? node.children.length : 0;
      onDrop({ parentPath: path, index: idx }, item);
    },
    collect: (monitor) => ({ isOverInside: monitor.isOver({ shallow: true }) }),
  }), [JSON.stringify(path), allowsChildren, node.children?.length, onDrop]);

  const composeRef = (el) => { dragRef(el); dropInsideRef(el); };

  return (
    <div
      className={[
        'wb-node',
        isRoot && 'wb-node--root',
        isSelected && 'wb-node--selected',
        isOverInside && allowsChildren && 'wb-node--drop-inside',
        isDragging && 'wb-node--dragging',
      ].filter(Boolean).join(' ')}
      onClick={(e) => {
        if (isRoot) return;
        e.stopPropagation();
        onSelect(path);
      }}
    >
      {!isRoot && (
        <div className="wb-node__head" ref={composeRef}>
          <i className={`bi ${icon} wb-node__icon`} aria-hidden="true" />
          <span className="wb-node__label">{label}</span>
          {allowsChildren && <span className="wb-node__badge">container</span>}
          <div className="wb-node__actions" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="wb-node__action"
              onClick={() => onDuplicate(path)}
              title="Duplicate"
              aria-label="Duplicate"
            ><i className="bi bi-copy" /></button>
            <button
              type="button"
              className="wb-node__action wb-node__action--danger"
              onClick={() => onDelete(path)}
              title="Delete"
              aria-label="Delete"
            ><i className="bi bi-trash" /></button>
          </div>
        </div>
      )}

      {isRoot && <div ref={composeRef} style={{ display: 'none' }} />}

      {allowsChildren && (
        <div className={`wb-node__children ${isRoot ? 'wb-node__children--root' : ''}`}>
          <DropZone
            compact
            onDrop={(item) => onDrop({ parentPath: path, index: 0 }, item)}
          />

          {Array.isArray(node.children) && node.children.map((child, idx) => (
            <React.Fragment key={child._id || idx}>
              <CanvasNode
                node={child}
                path={[...path, idx]}
                catalogueByType={catalogueByType}
                selectedPath={selectedPath}
                onSelect={onSelect}
                onDrop={onDrop}
                onDelete={onDelete}
                onDuplicate={onDuplicate}
              />
              <DropZone
                compact
                onDrop={(item) => onDrop({ parentPath: path, index: idx + 1 }, item)}
              />
            </React.Fragment>
          ))}

          {Array.isArray(node.children) && node.children.length === 0 && (
            <div className="wb-node__empty-hint">
              {isRoot ? 'Drag components from the left to start building.' : 'Drop components here'}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
