# Bootstrap 5.3 Drag-and-Drop Builder — Master Plan

Branch: `feature/bootstrap-drag-drop-builder`
Goal: Rebuild WebsiteBuilder around a real drag-and-drop canvas with the full
Bootstrap 5.3 component catalogue, CDN assets, all Bootswatch themes, and a
starter-site library. Keep existing auth / subscriptions / Stripe intact.

## Phase 1 — Backend foundation ✅ (current)
- [x] Bootswatch theme catalogue (`bootstrap_themes.py`, 27 themes, CDN URLs)
- [x] Bootstrap 5.3 component schema (`component_catalogue.py`, 56 components)
- [x] Python → Bootstrap HTML renderer (`bootstrap_renderer.py`)
- [x] Smoke tests: every type renders, every theme resolves, HTML parses
- [x] Demo pages rendered for default + Bootswatch cosmo + darkly
- [ ] Add `theme` + `tree_json` columns to the `Website` model
- [ ] Public `GET /s/<subdomain>` endpoint → renders a published site
- [ ] Editor-preview `GET /api/websites/<id>/preview` endpoint
- [ ] `GET /api/catalogue` → catalogue + themes (for the frontend palette)
- [ ] Flask-Migrate: migration for the new columns

## Phase 2 — Component catalogue ✅ already done in Phase 1

## Phase 3 — Drag-and-Drop Editor (frontend)
- [ ] Install Bootstrap + Bootstrap Icons in the React app (CDN links in index.html)
- [ ] Wire `react-dnd` with `HTML5Backend` (already in package.json)
- [ ] Palette sidebar — grouped by Layout / Content / Forms / Components / Helpers
- [ ] Canvas with nested drop zones; honour `allows_children` constraints
- [ ] Click-to-select + properties panel driven by catalogue `props` schema
- [ ] Reorder / duplicate / delete controls on every selected node
- [ ] Breakpoint preview toggles (xs / sm / md / lg / xl / xxl)
- [ ] Live iframe preview using `render_fragment` output (via backend endpoint)
- [ ] Undo/redo stack + auto-save (debounced)
- [ ] Replace the old HTML-textarea editor entirely

## Phase 4 — Starter-site catalogue
- [ ] Design 10+ starter templates as JSON trees:
  landing / portfolio / restaurant / business / blog / resume
  / e-commerce / event / non-profit / coming-soon
- [ ] `GET /api/starters` → catalogue; `POST /api/websites/from-starter` clones one
- [ ] Thumbnails (rendered offline, stored statically)

## Phase 5 — Theme picker UI
- [ ] Theme picker modal listing all 27 themes with live preview cards
- [ ] `PATCH /api/websites/<id>` accepts `theme` slug
- [ ] Preview/published pages reload with the chosen theme CSS

## Phase 6 — Published-site serving
- [ ] `subdomain.example.com` or `/s/<subdomain>` serves the rendered site
- [ ] Proper cache headers (ETag on tree hash)
- [ ] 404 page uses the user's chosen theme
- [ ] Only subscribers on active plans get custom subdomains (reuse existing gate)

## Phase 7 — Ship
- [ ] Update README + screenshots
- [ ] Commit, push, PR, merge
