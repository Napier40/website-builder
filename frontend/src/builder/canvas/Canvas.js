/**
 * Canvas — the central iframe live preview.
 *
 * Rather than try to reproduce Bootstrap's visual output in React (and risk
 * subtle drift), we embed the authoritative backend renderer inside an iframe
 * that points at /api/websites/<id>/preview/<slug>. After every save, we
 * bump a `version` query param to force a reload.
 *
 * The iframe is sized according to the selected device breakpoint; the
 * outer wrapper centres it on a grey workspace.
 */
import React, { useRef } from 'react';
import { previewUrl } from '../api';

const DEVICE_SIZES = {
  mobile:  { width: 375,  label: 'Mobile'  },
  tablet:  { width: 768,  label: 'Tablet'  },
  desktop: { width: '100%', label: 'Desktop' },
  full:    { width: '100%', label: 'Full'   },
};

export default function Canvas({
  websiteId, pageSlug, device = 'desktop',
  version,       // bump to force-reload the iframe
  token,
  saving,
}) {
  const frameRef = useRef(null);

  // When `version` bumps, the URL query changes → browser reloads.
  const url = `${previewUrl(websiteId, pageSlug, token)}${previewUrl(websiteId, pageSlug, token).includes('?') ? '&' : '?'}v=${version}`;

  const size = DEVICE_SIZES[device] || DEVICE_SIZES.desktop;

  return (
    <div className="wb-canvas">
      <div className="wb-canvas__statusbar">
        <span className="wb-canvas__url">
          <i className="bi bi-globe2" />
          <code>/api/websites/{websiteId}/preview{pageSlug ? '/' + pageSlug : ''}</code>
        </span>
        <span className={`wb-canvas__status wb-canvas__status--${saving}`}>
          {saving === 'saving' && <><i className="bi bi-arrow-repeat wb-spin" /> Saving…</>}
          {saving === 'saved'  && <><i className="bi bi-check2-circle" /> Saved</>}
          {saving === 'dirty'  && <><i className="bi bi-pencil" /> Unsaved changes</>}
          {saving === 'error'  && <><i className="bi bi-exclamation-triangle" /> Save failed</>}
          {saving === 'idle'   && <><i className="bi bi-check2-circle" /> Up to date</>}
        </span>
      </div>
      <div className="wb-canvas__viewport">
        <div
          className={`wb-canvas__frame-wrap wb-canvas__frame-wrap--${device}`}
          style={{ width: typeof size.width === 'number' ? `${size.width}px` : size.width }}
        >
          <iframe
            ref={frameRef}
            key={version}          // React: force remount on version bump
            src={url}
            title="Live preview"
            className="wb-canvas__frame"
          />
        </div>
      </div>
    </div>
  );
}

export { DEVICE_SIZES };
