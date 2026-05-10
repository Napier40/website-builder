/**
 * PaletteItem — a draggable entry in the left-sidebar component palette.
 * Dragging one onto the canvas emits an `item` of shape:
 *   { kind: 'new', componentType: <string> }
 */
import React from 'react';
import { useDrag } from 'react-dnd';
import { ItemTypes } from './ItemTypes';

export default function PaletteItem({ component }) {
  const [{ isDragging }, dragRef] = useDrag(() => ({
    type: ItemTypes.PALETTE_ITEM,
    item: { kind: 'new', componentType: component.type },
    collect: (monitor) => ({ isDragging: monitor.isDragging() }),
  }), [component.type]);

  return (
    <div
      ref={dragRef}
      className="wb-palette-item"
      style={{ opacity: isDragging ? 0.4 : 1 }}
      title={component.label}
    >
      <i className={`bi ${component.icon || 'bi-box'}`} aria-hidden="true" />
      <span>{component.label}</span>
    </div>
  );
}
