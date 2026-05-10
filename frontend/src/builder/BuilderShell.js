/**
 * BuilderShell — the top-level drag-and-drop website editor.
 *
 * Layout (CSS grid in wb-builder):
 *   ┌───────────────────────────────────────────────┐
 *   │                    TOPBAR                     │   ← save/publish, device toggles
 *   ├─────────┬──────────────────────┬──────────────┤
 *   │ PALETTE │        CANVAS        │  PROPERTIES  │
 *   │ (pages, │  ┌──────────────────┐│  (schema-    │
 *   │ themes, │  │   tree outline   ││  driven)     │
 *   │ compo-  │  ├──────────────────┤│              │
 *   │ nents)  │  │  iframe preview  ││              │
 *   │         │  └──────────────────┘│              │
 *   └─────────┴──────────────────────┴──────────────┘
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

import {
  fetchWebsite, savePageTree, savePageMeta, addPage as apiAddPage,
  deletePage as apiDeletePage, updateWebsite,
  publishWebsite, unpublishWebsite,
} from './api';
import useCatalogue from './useCatalogue';
import useHistory   from './tree/useHistory';
import useAutoSave  from './tree/useAutoSave';
import {
  hydrateIds, stripIds, emptyRoot, newNodeFromCatalogue,
  insertAt, moveTo, removeAt, duplicateAt, setPropsAt,
  findPathById,
} from './tree/treeOps';
import { useAuth } from '../context/AuthContext';

import PalettePanel     from './panels/PalettePanel';
import PagesPanel       from './panels/PagesPanel';
import SettingsPanel    from './panels/SettingsPanel';
import PropertiesPanel  from './panels/PropertiesPanel';
import CanvasNode       from './dnd/CanvasNode';
import Canvas           from './canvas/Canvas';

import './styles.css';

const SIDEBAR_TABS = [
  { key: 'elements', label: 'Elements', icon: 'bi-grid-3x3-gap' },
  { key: 'pages',    label: 'Pages',    icon: 'bi-file-earmark' },
  { key: 'theme',    label: 'Theme',    icon: 'bi-palette' },
];

const DEVICES = [
  { key: 'mobile',  icon: 'bi-phone',         label: 'Mobile'  },
  { key: 'tablet',  icon: 'bi-tablet',        label: 'Tablet'  },
  { key: 'desktop', icon: 'bi-laptop',        label: 'Desktop' },
];


export default function BuilderShell() {
  const { id } = useParams();
  const navigate = useNavigate();
  const auth = useAuth();

  const { loading: cataLoading, error: cataError, catalogue, byType, byCategory } = useCatalogue();

  const [website, setWebsite] = useState(null);
  const [currentPageId, setCurrentPageId] = useState(null);

  // The live canvas tree. We hold it here; undo/redo wraps it.
  const [tree, setTree, history] = useHistory(emptyRoot());
  const [selectedPath, setSelectedPath] = useState(null);

  const [sidebarTab, setSidebarTab] = useState('elements');
  const [device,      setDevice]    = useState('desktop');
  const [previewVersion, setPreviewVersion] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [isPublishing, setIsPublishing] = useState(false);

  // ── 1. Load the website + hydrate initial tree ───────────────────────
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        const w = await fetchWebsite(id);
        if (cancelled) return;
        setWebsite(w);
        const home = w.pages.find(p => p.slug === 'home') || w.pages[0];
        setCurrentPageId(home?.id || null);
        const initialTree = home?.tree ? hydrateIds(home.tree) : emptyRoot();
        history.reset(initialTree);
        setLoading(false);
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.message || err.message || 'Failed to load website');
          setLoading(false);
        }
      }
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // ── 2. When the user switches page, swap the tree in ─────────────────
  const switchToPage = useCallback((pageId) => {
    if (pageId === currentPageId || !website) return;
    const p = website.pages.find(x => x.id === pageId);
    if (!p) return;
    const nextTree = p.tree ? hydrateIds(p.tree) : emptyRoot();
    history.reset(nextTree);
    setCurrentPageId(pageId);
    setSelectedPath(null);
    setPreviewVersion(v => v + 1);
  }, [currentPageId, website, history]);

  const currentPage = useMemo(
    () => website?.pages.find(p => p.id === currentPageId) || null,
    [website, currentPageId]
  );

  // ── 3. Auto-save the tree ────────────────────────────────────────────
  const saveTreeToServer = useCallback(async (t) => {
    if (!currentPage) return;
    const cleanTree = stripIds(t);
    await savePageTree(id, currentPage.id, cleanTree);
    // Refresh iframe after successful save.
    setPreviewVersion(v => v + 1);
  }, [id, currentPage]);

  const { status: saveStatus, flush } = useAutoSave(
    tree, saveTreeToServer,
    { delayMs: 1500, enabled: !!currentPage }
  );

  // ── 4. Tree mutation helpers ─────────────────────────────────────────

  const handleDrop = useCallback((target, item) => {
    if (!catalogue) return;
    setTree(prev => {
      if (item.kind === 'new') {
        const entry = byType[item.componentType];
        if (!entry) return prev;
        const node = newNodeFromCatalogue(entry);
        const next = insertAt(prev, target.parentPath, target.index, node);
        // Select the newly-added node
        setTimeout(() => {
          const path = findPathById(next, node._id) || [...target.parentPath, target.index];
          setSelectedPath(path);
        }, 0);
        return next;
      }
      if (item.kind === 'move') {
        return moveTo(prev, item.fromPath, target.parentPath, target.index);
      }
      return prev;
    });
  }, [catalogue, byType, setTree]);

  const handleDelete = useCallback((path) => {
    setTree(prev => {
      const { tree: next } = removeAt(prev, path);
      return next;
    });
    setSelectedPath(null);
  }, [setTree]);

  const handleDuplicate = useCallback((path) => {
    setTree(prev => duplicateAt(prev, path));
  }, [setTree]);

  const handlePropsChange = useCallback((propsPatch) => {
    if (!selectedPath) return;
    setTree(prev => setPropsAt(prev, selectedPath, propsPatch));
  }, [selectedPath, setTree]);

  // Delete/duplicate from properties panel operate on the selected node.
  const deleteSelected    = useCallback(() => selectedPath && handleDelete(selectedPath),   [selectedPath, handleDelete]);
  const duplicateSelected = useCallback(() => selectedPath && handleDuplicate(selectedPath), [selectedPath, handleDuplicate]);

  // ── 5. Website-level actions ─────────────────────────────────────────

  const patchWebsite = useCallback(async (patch) => {
    if (!website) return;
    // Optimistic — patch local state, then persist.
    setWebsite(w => ({ ...w, ...patch }));
    try {
      const updated = await updateWebsite(id, patch);
      setWebsite(updated);
      // Theme changes need iframe reload.
      if ('theme' in patch) setPreviewVersion(v => v + 1);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Save failed');
    }
  }, [id, website]);

  const handleAddPage = useCallback(async ({ title, slug }) => {
    try {
      const page = await apiAddPage(id, { title, slug });
      setWebsite(w => ({ ...w, pages: [...w.pages, page] }));
      switchToPage(page.id);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Could not add page');
    }
  }, [id, switchToPage]);

  const handleRenamePage = useCallback(async (pageId, patch) => {
    try {
      const page = await savePageMeta(id, pageId, patch);
      setWebsite(w => ({
        ...w,
        pages: w.pages.map(p => p.id === pageId ? { ...p, ...page } : p),
      }));
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Could not rename page');
    }
  }, [id]);

  const handleDeletePage = useCallback(async (pageId) => {
    try {
      await apiDeletePage(id, pageId);
      setWebsite(w => {
        const nextPages = w.pages.filter(p => p.id !== pageId);
        return { ...w, pages: nextPages };
      });
      if (pageId === currentPageId) {
        const remaining = website.pages.filter(p => p.id !== pageId);
        if (remaining.length) switchToPage(remaining[0].id);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Could not delete page');
    }
  }, [id, currentPageId, website, switchToPage]);

  const handleTogglePublish = useCallback(async () => {
    if (!website) return;
    setIsPublishing(true);
    try {
      await flush();   // make sure draft is saved before publishing
      const updated = website.isPublished
        ? await unpublishWebsite(id)
        : await publishWebsite(id);
      setWebsite(updated);
      setPreviewVersion(v => v + 1);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Publish failed');
    } finally {
      setIsPublishing(false);
    }
  }, [id, website, flush]);

  const handleManualSave = useCallback(async () => {
    try { await flush(); } catch (_) { /* already logged */ }
  }, [flush]);

  // ── 6. Keyboard shortcuts ────────────────────────────────────────────
  useEffect(() => {
    const onKey = (e) => {
      const isMod = e.metaKey || e.ctrlKey;
      if (!isMod) return;
      if (e.key === 's')      { e.preventDefault(); handleManualSave(); }
      else if (e.key === 'z' && !e.shiftKey) { e.preventDefault(); history.undo(); }
      else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {
        e.preventDefault(); history.redo();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [history, handleManualSave]);

  // ── 7. Resolve selected node (re-derived every render) ───────────────
  const selectedNode = useMemo(() => {
    if (!selectedPath) return null;
    let n = tree;
    for (const i of selectedPath) {
      if (!n?.children || !n.children[i]) return null;
      n = n.children[i];
    }
    return n;
  }, [tree, selectedPath]);

  const selectedEntry = selectedNode ? byType[selectedNode.type] : null;

  // ── Loading/error states ─────────────────────────────────────────────
  if (loading || cataLoading) {
    return (
      <div className="wb-fullpage">
        <div className="wb-fullpage__spinner" />
        <p>Loading builder…</p>
      </div>
    );
  }
  if (error || cataError) {
    return (
      <div className="wb-fullpage">
        <i className="bi bi-exclamation-triangle" style={{ fontSize: '2.5rem', color: 'var(--wb-danger)' }} />
        <p>{error || cataError}</p>
        <button className="wb-btn wb-btn--primary" onClick={() => navigate('/websites')}>
          Back to Websites
        </button>
      </div>
    );
  }
  if (!website) return null;

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <DndProvider backend={HTML5Backend}>
      <div className="wb-builder" onClick={() => setSelectedPath(null)}>
        <div className="wb-topbar">
          <button
            className="wb-topbar__icon-btn"
            onClick={async () => { await handleManualSave(); navigate('/websites'); }}
            title="Back to Websites"
          ><i className="bi bi-arrow-left" /></button>

          <span className="wb-topbar__title">{website.name}</span>

          <div className="wb-topbar__divider" />

          <select
            className="wb-topbar__page-select"
            value={currentPageId || ''}
            onChange={(e) => switchToPage(Number(e.target.value))}
          >
            {website.pages.map(p => (
              <option key={p.id} value={p.id}>{p.title}</option>
            ))}
          </select>

          <div className="wb-topbar__spacer" />

          <div className="wb-topbar__group" role="group" aria-label="Device preview">
            {DEVICES.map(d => (
              <button
                key={d.key}
                className={`wb-topbar__icon-btn ${device === d.key ? 'is-active' : ''}`}
                onClick={() => setDevice(d.key)}
                title={d.label}
              ><i className={`bi ${d.icon}`} /></button>
            ))}
          </div>

          <div className="wb-topbar__divider" />

          <button
            className="wb-topbar__icon-btn"
            onClick={history.undo}
            disabled={!history.canUndo}
            title="Undo (Ctrl+Z)"
          ><i className="bi bi-arrow-counterclockwise" /></button>
          <button
            className="wb-topbar__icon-btn"
            onClick={history.redo}
            disabled={!history.canRedo}
            title="Redo (Ctrl+Shift+Z)"
          ><i className="bi bi-arrow-clockwise" /></button>

          <div className="wb-topbar__divider" />

          <button
            className="wb-btn wb-btn--outline wb-btn--sm"
            onClick={handleManualSave}
            title="Save (Ctrl+S)"
          >
            <i className="bi bi-save" /> Save
          </button>

          <button
            className={`wb-btn wb-btn--sm ${website.isPublished ? 'wb-btn--success' : 'wb-btn--primary'}`}
            onClick={handleTogglePublish}
            disabled={isPublishing}
          >
            {isPublishing ? (
              <><i className="bi bi-arrow-repeat wb-spin" /> Working…</>
            ) : website.isPublished ? (
              <><i className="bi bi-check2-circle" /> Published</>
            ) : (
              <><i className="bi bi-rocket-takeoff" /> Publish</>
            )}
          </button>

          {website.isPublished && (
            <a
              className="wb-topbar__icon-btn"
              href={`/s/${website.subdomain}`}
              target="_blank"
              rel="noreferrer"
              title="Open live site"
            ><i className="bi bi-box-arrow-up-right" /></a>
          )}
        </div>

        {/* Left sidebar */}
        <aside className="wb-sidebar" onClick={(e) => e.stopPropagation()}>
          <div className="wb-sidebar__tabs" role="tablist">
            {SIDEBAR_TABS.map(tab => (
              <button
                key={tab.key}
                role="tab"
                aria-selected={sidebarTab === tab.key}
                className={`wb-sidebar__tab ${sidebarTab === tab.key ? 'is-active' : ''}`}
                onClick={() => setSidebarTab(tab.key)}
              >
                <i className={`bi ${tab.icon}`} /> {tab.label}
              </button>
            ))}
          </div>
          <div className="wb-sidebar__body">
            {sidebarTab === 'elements' && (
              <PalettePanel byCategory={byCategory} />
            )}
            {sidebarTab === 'pages' && (
              <PagesPanel
                pages={website.pages}
                currentPageId={currentPageId}
                onSelectPage={switchToPage}
                onAddPage={handleAddPage}
                onRenamePage={handleRenamePage}
                onDeletePage={handleDeletePage}
              />
            )}
            {sidebarTab === 'theme' && (
              <SettingsPanel
                website={website}
                themes={catalogue.themes}
                onPatchWebsite={patchWebsite}
              />
            )}
          </div>
        </aside>

        {/* Middle column: tree outline + live iframe canvas */}
        <div className="wb-canvas-column" onClick={(e) => e.stopPropagation()}>
          <div className="wb-canvas-column__tree">
            <h4 className="wb-canvas-column__tree-title">
              Page structure <span className="wb-settings__muted">· click to select, drag to rearrange</span>
            </h4>
            <CanvasNode
              node={tree}
              path={[]}
              catalogueByType={byType}
              selectedPath={selectedPath}
              onSelect={setSelectedPath}
              onDrop={handleDrop}
              onDelete={handleDelete}
              onDuplicate={handleDuplicate}
            />
          </div>

          <Canvas
            websiteId={id}
            pageSlug={currentPage?.slug}
            device={device}
            version={previewVersion}
            token={auth?.token}
            saving={saveStatus}
          />
        </div>

        {/* Right sidebar: properties panel */}
        <PropertiesPanel
          selectedNode={selectedNode}
          selectedPath={selectedPath}
          catalogueEntry={selectedEntry}
          onChangeProps={handlePropsChange}
          onDeleteSelected={deleteSelected}
          onDuplicateSelected={duplicateSelected}
        />
      </div>
    </DndProvider>
  );
}
