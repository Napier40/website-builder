/**
 * PropertiesPanel — right sidebar. Shows the selected node's props as a
 * dynamically-generated form driven by the catalogue's prop schema.
 *
 * Prop kinds handled (matching the backend's component_catalogue.py):
 *   'text'    – <input type="text">
 *   'textarea'– <textarea> (multi-line)
 *   'rich'    – <textarea> for ::-separated compound strings + helper hint
 *   'number'  – <input type="number">
 *   'bool'    – checkbox
 *   'enum'    – <select> with options
 *   'url'     – <input type="url">
 *   'color'   – <input type="color">
 *   'html'    – code textarea (monospace) for raw HTML
 */
import React from 'react';

export default function PropertiesPanel({
  selectedNode, selectedPath,
  catalogueEntry,
  onChangeProps,
  onDeleteSelected,
  onDuplicateSelected,
}) {
  if (!selectedNode || !selectedPath || selectedPath.length === 0) {
    return (
      <div className="wb-props wb-props--empty">
        <i className="bi bi-mouse2" />
        <p>Select a component to edit its properties.</p>
      </div>
    );
  }

  if (!catalogueEntry) {
    return (
      <div className="wb-props wb-props--empty">
        <i className="bi bi-exclamation-triangle" />
        <p>Unknown component type: <code>{selectedNode.type}</code></p>
      </div>
    );
  }

  const propsSchema = catalogueEntry.props || {};
  const values      = selectedNode.props || {};

  const fieldEntries = Object.entries(propsSchema);

  return (
    <div className="wb-props">
      <header className="wb-props__header">
        <div className="wb-props__title">
          <i className={`bi ${catalogueEntry.icon || 'bi-box'}`} />
          <span>{catalogueEntry.label}</span>
        </div>
        <div className="wb-props__actions">
          <button
            type="button"
            className="wb-btn wb-btn--ghost wb-btn--sm"
            onClick={onDuplicateSelected}
            title="Duplicate"
          ><i className="bi bi-copy" /></button>
          <button
            type="button"
            className="wb-btn wb-btn--ghost-danger wb-btn--sm"
            onClick={onDeleteSelected}
            title="Delete"
          ><i className="bi bi-trash" /></button>
        </div>
      </header>

      <div className="wb-props__body">
        {fieldEntries.length === 0 && (
          <p className="wb-props__muted">This component has no editable properties.</p>
        )}

        {fieldEntries.map(([name, schema]) => (
          <PropField
            key={name}
            name={name}
            schema={schema}
            value={values[name]}
            onChange={(v) => onChangeProps({ [name]: v })}
          />
        ))}
      </div>
    </div>
  );
}


function PropField({ name, schema, value, onChange }) {
  const kind  = schema.kind || 'text';
  const label = schema.label || prettify(name);
  const hint  = schema.help  || schema.hint  || null;
  const fallback = schema.default;

  const current = value === undefined ? fallback : value;

  if (kind === 'bool') {
    return (
      <label className="wb-field wb-field--inline">
        <input
          type="checkbox"
          checked={!!current}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span className="wb-field__label">{label}</span>
        {hint && <span className="wb-field__hint">{hint}</span>}
      </label>
    );
  }

  if (kind === 'enum') {
    const options = schema.options || [];
    return (
      <label className="wb-field">
        <span className="wb-field__label">{label}</span>
        <select
          value={current ?? ''}
          onChange={(e) => onChange(e.target.value)}
        >
          {options.map(opt => {
            const [optValue, optLabel] =
              typeof opt === 'string' ? [opt, opt || '— none —']
                                     : [opt.value, opt.label];
            return <option key={optValue} value={optValue}>{optLabel}</option>;
          })}
        </select>
        {hint && <span className="wb-field__hint">{hint}</span>}
      </label>
    );
  }

  if (kind === 'number') {
    return (
      <label className="wb-field">
        <span className="wb-field__label">{label}</span>
        <input
          type="number"
          value={current ?? ''}
          min={schema.min}
          max={schema.max}
          step={schema.step || 1}
          onChange={(e) => {
            const v = e.target.value;
            onChange(v === '' ? null : Number(v));
          }}
        />
        {hint && <span className="wb-field__hint">{hint}</span>}
      </label>
    );
  }

  if (kind === 'url') {
    return (
      <label className="wb-field">
        <span className="wb-field__label">{label}</span>
        <input
          type="url"
          value={current ?? ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder="https://…"
        />
        {hint && <span className="wb-field__hint">{hint}</span>}
      </label>
    );
  }

  if (kind === 'icon') {
    return (
      <label className="wb-field">
        <span className="wb-field__label">{label}</span>
        <div className="wb-field__icon-row">
          <input
            type="text"
            value={current ?? ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder="bi-star"
          />
          {current && <i className={`bi ${current} wb-field__icon-preview`} aria-hidden="true" />}
        </div>
        <span className="wb-field__hint">
          {hint || (
            <>Bootstrap Icons class — see <a href="https://icons.getbootstrap.com/" target="_blank" rel="noreferrer">icons.getbootstrap.com</a>.</>
          )}
        </span>
      </label>
    );
  }

  if (kind === 'color') {
    return (
      <label className="wb-field wb-field--color">
        <span className="wb-field__label">{label}</span>
        <input
          type="color"
          value={current || '#000000'}
          onChange={(e) => onChange(e.target.value)}
        />
        {hint && <span className="wb-field__hint">{hint}</span>}
      </label>
    );
  }

  if (kind === 'textarea' || kind === 'rich' || kind === 'html') {
    return (
      <label className="wb-field">
        <span className="wb-field__label">{label}</span>
        <textarea
          rows={kind === 'html' ? 8 : 4}
          className={kind === 'html' ? 'wb-field__code' : ''}
          value={current ?? ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={schema.placeholder || ''}
        />
        {kind === 'rich' && (
          <span className="wb-field__hint">
            {hint || 'Use ` :: ` to separate fields within a row, and new lines to separate rows.'}
          </span>
        )}
        {kind === 'html' && (
          <span className="wb-field__hint">
            {hint || 'Raw HTML — sanitised on the server before rendering.'}
          </span>
        )}
        {kind === 'textarea' && hint && <span className="wb-field__hint">{hint}</span>}
      </label>
    );
  }

  // default 'text'
  return (
    <label className="wb-field">
      <span className="wb-field__label">{label}</span>
      <input
        type="text"
        value={current ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={schema.placeholder || ''}
      />
      {hint && <span className="wb-field__hint">{hint}</span>}
    </label>
  );
}

function prettify(name) {
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, s => s.toUpperCase())
    .trim();
}
