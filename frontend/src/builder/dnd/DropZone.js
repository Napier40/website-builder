/**
 * DropZone — a thin horizontal drop target inserted *between* sibling nodes
 *            (and at the start/end of each container's children list).
 *
 * Accepts both PALETTE_ITEM (new component) and CANVAS_NODE (move an existing
 * node). The onDrop handler is called with the payload; the parent component
 * is responsible for mutating the tree.
 */
import React from 'react';
import { useDrop } from 'react-dnd';
import { ItemTypes } from './ItemTypes';

export default function DropZone({ onDrop, compact = false }) {
  const [{ isOver, canDrop }, dropRef] = useDrop(() => ({
    accept: [ItemTypes.PALETTE_ITEM, ItemTypes.CANVAS_NODE],
    drop:   (item, monitor) => {
      // Only fire on the innermost matching drop zone.
      if (monitor.didDrop()) return;
      onDrop(item);
    },
    collect: (monitor) => ({
      isOver:  monitor.isOver({ shallow: true }),
      canDrop: monitor.canDrop(),
    }),
  }), [onDrop]);

  const active = isOver && canDrop;

  return (
    <div
      ref={dropRef}
      className={`wb-dropzone ${compact ? 'wb-dropzone--compact' : ''} ${active ? 'wb-dropzone--active' : ''}`}
      aria-hidden="true"
    >
      <div className="wb-dropzone__bar" />
    </div>
  );
}
