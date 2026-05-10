/**
 * useHistory — a minimal undo/redo stack around any state value.
 *
 * Usage:
 *   const [tree, setTree, { undo, redo, canUndo, canRedo, reset }] = useHistory(initialTree);
 *
 * Every call to setTree pushes a new entry onto the past stack and clears
 * the future stack. undo() moves the current value to future and pops past.
 */
import { useCallback, useRef, useState } from 'react';

export default function useHistory(initialValue, { limit = 100 } = {}) {
  const [present, setPresent] = useState(initialValue);
  const pastRef   = useRef([]);
  const futureRef = useRef([]);
  // Bump this whenever undo/redo shifts the stacks so components that care
  // about canUndo/canRedo re-render.
  const [, forceTick] = useState(0);
  const bump = () => forceTick(t => t + 1);

  const set = useCallback((next) => {
    setPresent((prev) => {
      const resolved = typeof next === 'function' ? next(prev) : next;
      if (resolved === prev) return prev;
      pastRef.current.push(prev);
      if (pastRef.current.length > limit) pastRef.current.shift();
      futureRef.current = [];
      bump();
      return resolved;
    });
  }, [limit]);

  const undo = useCallback(() => {
    if (pastRef.current.length === 0) return;
    const prev = pastRef.current.pop();
    setPresent((curr) => {
      futureRef.current.push(curr);
      return prev;
    });
    bump();
  }, []);

  const redo = useCallback(() => {
    if (futureRef.current.length === 0) return;
    const next = futureRef.current.pop();
    setPresent((curr) => {
      pastRef.current.push(curr);
      return next;
    });
    bump();
  }, []);

  /** Reset the history and the present value. */
  const reset = useCallback((value) => {
    pastRef.current = [];
    futureRef.current = [];
    setPresent(value);
    bump();
  }, []);

  return [present, set, {
    undo,
    redo,
    reset,
    canUndo: pastRef.current.length > 0,
    canRedo: futureRef.current.length > 0,
  }];
}
