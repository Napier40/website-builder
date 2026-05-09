/**
 * PagesPanel — manage the website's pages (add / rename / select / delete).
 */
import React, { useState } from 'react';

export default function PagesPanel({
  pages, currentPageId, onSelectPage,
  onAddPage, onRenamePage, onDeletePage,
}) {
  const [adding, setAdding] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  const handleAdd = async (e) => {
    e.preventDefault();
    const title = newTitle.trim();
    if (!title) return;
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    await onAddPage({ title, slug });
    setNewTitle('');
    setAdding(false);
  };

  const startRename = (page) => {
    setRenamingId(page.id);
    setRenameValue(page.title);
  };

  const commitRename = async (page) => {
    const title = renameValue.trim();
    if (title && title !== page.title) {
      await onRenamePage(page.id, { title });
    }
    setRenamingId(null);
  };

  return (
    <div className="wb-pages">
      <ul className="wb-pages__list">
        {pages.map(page => (
          <li
            key={page.id}
            className={`wb-pages__item ${page.id === currentPageId ? 'wb-pages__item--active' : ''}`}
          >
            <i className="bi bi-file-earmark-text wb-pages__icon" />
            {renamingId === page.id ? (
              <input
                className="wb-pages__rename"
                autoFocus
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                onBlur={() => commitRename(page)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') commitRename(page);
                  else if (e.key === 'Escape') setRenamingId(null);
                }}
              />
            ) : (
              <button
                type="button"
                className="wb-pages__select"
                onClick={() => onSelectPage(page.id)}
                onDoubleClick={() => startRename(page)}
                title="Click to switch · double-click to rename"
              >
                <span className="wb-pages__title">{page.title}</span>
                <span className="wb-pages__slug">/{page.slug}</span>
              </button>
            )}
            <div className="wb-pages__actions">
              <button
                type="button"
                className="wb-pages__action"
                onClick={() => startRename(page)}
                title="Rename"
              ><i className="bi bi-pencil" /></button>
              {pages.length > 1 && (
                <button
                  type="button"
                  className="wb-pages__action wb-pages__action--danger"
                  onClick={() => {
                    if (window.confirm(`Delete "${page.title}"? This can't be undone.`)) {
                      onDeletePage(page.id);
                    }
                  }}
                  title="Delete"
                ><i className="bi bi-trash" /></button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {adding ? (
        <form className="wb-pages__add-form" onSubmit={handleAdd}>
          <input
            autoFocus
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="New page title"
          />
          <div className="wb-pages__add-actions">
            <button type="submit" className="wb-btn wb-btn--primary wb-btn--sm">Add</button>
            <button type="button" className="wb-btn wb-btn--ghost wb-btn--sm" onClick={() => setAdding(false)}>
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <button
          type="button"
          className="wb-btn wb-btn--outline wb-btn--block"
          onClick={() => setAdding(true)}
        >
          <i className="bi bi-plus-lg" /> Add page
        </button>
      )}
    </div>
  );
}
