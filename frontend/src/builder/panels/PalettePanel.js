/**
 * PalettePanel — the left sidebar's "Elements" tab.
 *
 * Shows every component from the backend catalogue, grouped by category.
 * Each tile is draggable onto the canvas (see PaletteItem).
 */
import React, { useMemo, useState } from 'react';
import PaletteItem from '../dnd/PaletteItem';

const CATEGORY_ORDER = ['Layout', 'Content', 'Forms', 'Components', 'Helpers'];

export default function PalettePanel({ byCategory }) {
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    if (!query.trim()) return byCategory;
    const q = query.toLowerCase();
    const out = {};
    for (const [cat, comps] of Object.entries(byCategory)) {
      const matches = comps.filter(c =>
        c.label.toLowerCase().includes(q) ||
        c.type.toLowerCase().includes(q)
      );
      if (matches.length) out[cat] = matches;
    }
    return out;
  }, [byCategory, query]);

  const orderedCategories = useMemo(() => {
    const keys = Object.keys(filtered);
    return keys.sort((a, b) => {
      const ai = CATEGORY_ORDER.indexOf(a);
      const bi = CATEGORY_ORDER.indexOf(b);
      if (ai === -1 && bi === -1) return a.localeCompare(b);
      if (ai === -1) return 1;
      if (bi === -1) return -1;
      return ai - bi;
    });
  }, [filtered]);

  return (
    <div className="wb-palette">
      <div className="wb-palette__search">
        <i className="bi bi-search" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search components…"
          aria-label="Search components"
        />
        {query && (
          <button
            type="button"
            className="wb-palette__clear"
            onClick={() => setQuery('')}
            aria-label="Clear search"
          ><i className="bi bi-x-lg" /></button>
        )}
      </div>

      {orderedCategories.length === 0 && (
        <div className="wb-palette__empty">No matches.</div>
      )}

      {orderedCategories.map(cat => (
        <section key={cat} className="wb-palette__section">
          <h4 className="wb-palette__title">{cat}</h4>
          <div className="wb-palette__grid">
            {filtered[cat].map(comp => (
              <PaletteItem key={comp.type} component={comp} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
