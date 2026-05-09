/**
 * useAutoSave — calls `saveFn(value)` whenever `value` changes, debounced.
 *
 * Exposes:
 *   status: 'idle' | 'dirty' | 'saving' | 'saved' | 'error'
 *   flush(): force immediate save (used by Ctrl+S / explicit Save button)
 */
import { useCallback, useEffect, useRef, useState } from 'react';

export default function useAutoSave(value, saveFn, {
  delayMs    = 1500,
  enabled    = true,
} = {}) {
  const [status, setStatus] = useState('idle');
  const lastSavedRef = useRef(value);
  const timerRef     = useRef(null);
  const saveFnRef    = useRef(saveFn);
  saveFnRef.current  = saveFn;

  const doSave = useCallback(async (v) => {
    setStatus('saving');
    try {
      await saveFnRef.current(v);
      lastSavedRef.current = v;
      setStatus('saved');
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('[autosave] failed:', err);
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    if (!enabled) return;
    if (value === lastSavedRef.current) return;

    setStatus('dirty');

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      doSave(value);
    }, delayMs);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [value, delayMs, enabled, doSave]);

  const flush = useCallback(async () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (lastSavedRef.current !== value) {
      await doSave(value);
    }
  }, [value, doSave]);

  return { status, flush };
}
