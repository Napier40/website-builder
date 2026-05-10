/**
 * useCatalogue — fetches /api/catalogue once per browser session and returns
 *   { loading, error, catalogue }
 *
 * The catalogue rarely changes (only on backend deploys), so we cache it on
 * window to avoid duplicate HTTP calls when multiple builder components mount.
 */
import { useEffect, useState, useMemo } from 'react';
import { fetchCatalogue } from './api';

const CACHE_KEY = '__builder_catalogue_cache__';

export default function useCatalogue() {
  const [state, setState] = useState(() => ({
    loading: !window[CACHE_KEY],
    error:   null,
    catalogue: window[CACHE_KEY] || null,
  }));

  useEffect(() => {
    if (window[CACHE_KEY]) return;
    let cancelled = false;

    fetchCatalogue()
      .then(data => {
        window[CACHE_KEY] = data;
        if (!cancelled) setState({ loading: false, error: null, catalogue: data });
      })
      .catch(err => {
        if (!cancelled) setState({
          loading: false,
          error:   err.message || 'Failed to load catalogue',
          catalogue: null,
        });
      });

    return () => { cancelled = true; };
  }, []);

  /** Index components by `type` for O(1) lookup in the editor. */
  const byType = useMemo(() => {
    if (!state.catalogue) return {};
    const out = {};
    for (const comp of state.catalogue.components) out[comp.type] = comp;
    return out;
  }, [state.catalogue]);

  /** Group components by category for sidebar section headers. */
  const byCategory = useMemo(() => {
    if (!state.catalogue) return {};
    const groups = {};
    for (const comp of state.catalogue.components) {
      (groups[comp.category] ||= []).push(comp);
    }
    return groups;
  }, [state.catalogue]);

  return { ...state, byType, byCategory };
}
