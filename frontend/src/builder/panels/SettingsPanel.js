/**
 * SettingsPanel — global site settings: name, description, theme.
 *
 * The theme picker shows all 27 themes as swatch cards; clicking one
 * updates the website's theme and triggers an iframe reload in the canvas.
 */
import React from 'react';

export default function SettingsPanel({ website, themes, onPatchWebsite }) {
  const current = website?.theme || 'default';

  return (
    <div className="wb-settings">
      <section className="wb-settings__section">
        <h4 className="wb-settings__title">Site details</h4>
        <label className="wb-field">
          <span className="wb-field__label">Name</span>
          <input
            type="text"
            value={website?.name || ''}
            onChange={(e) => onPatchWebsite({ name: e.target.value })}
          />
        </label>
        <label className="wb-field">
          <span className="wb-field__label">Description</span>
          <textarea
            rows={3}
            value={website?.description || ''}
            onChange={(e) => onPatchWebsite({ description: e.target.value })}
            placeholder="Shown in the site's meta description"
          />
        </label>
        <label className="wb-field">
          <span className="wb-field__label">Subdomain</span>
          <div className="wb-field__fixed">
            <code>{website?.subdomain}</code>
            <span className="wb-field__hint">
              /s/{website?.subdomain}
            </span>
          </div>
        </label>
      </section>

      <section className="wb-settings__section">
        <h4 className="wb-settings__title">
          Theme <span className="wb-settings__muted">— choose a Bootswatch style</span>
        </h4>

        <div className="wb-themes">
          {themes?.map(t => (
            <button
              key={t.slug}
              type="button"
              className={[
                'wb-theme',
                t.slug === current && 'wb-theme--active',
                t.isDark && 'wb-theme--dark',
              ].filter(Boolean).join(' ')}
              onClick={() => onPatchWebsite({ theme: t.slug })}
              title={t.description}
            >
              <span className="wb-theme__swatch">
                <span className="wb-theme__swatch-a" />
                <span className="wb-theme__swatch-b" />
                <span className="wb-theme__swatch-c" />
              </span>
              <span className="wb-theme__label">
                {t.name}
                {t.slug === current && <i className="bi bi-check-circle-fill wb-theme__tick" />}
              </span>
              <span className="wb-theme__desc">{t.description}</span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
