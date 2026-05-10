# Bootstrap 5.3 Drag-and-Drop Builder — Master Plan

Branch: `feature/bootstrap-drag-drop-builder`
Goal: Rebuild WebsiteBuilder around a real drag-and-drop canvas with the full
Bootstrap 5.3 component catalogue, CDN assets, all Bootswatch themes, and a
starter-site library. Keep existing auth / subscriptions / Stripe intact.

## Phase 1 — Backend foundation ✅ (current)
- [x] Bootswatch theme catalogue (`bootstrap_themes.py`, 27 themes, CDN URLs)
- [x] Bootstrap 5.3 component schema (`component_catalogue.py`, 69 components)
- [x] Python → Bootstrap HTML renderer (`bootstrap_renderer.py`)
- [x] Smoke tests: every type renders, every theme resolves, HTML parses
- [x] Demo pages rendered for default + Bootswatch cosmo + darkly
- [x] Add `theme` + `tree_json` columns to the `Website`/`Page` models
- [x] SQLite schema-evolution helper (additive `ALTER TABLE ADD COLUMN`)
- [x] Public `GET /s/<subdomain>[/<slug>]` endpoint — published sites
- [x] Editor-preview `GET /api/websites/<id>/preview[/<slug>]` endpoint
- [x] `GET /api/catalogue` → catalogue + themes + CDN URLs (for frontend palette)
- [x] `PUT /api/websites/<id>` accepts & validates `theme`
- [x] Integration tests for every new endpoint (16 new, 99 total passing)
- [x] Proper `requirements.txt` for the Flask backend

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

## Phase 4 — Starter-site catalogue + Multilingual Support
- [x] Design 10+ starter templates as JSON trees:
  landing / portfolio / restaurant / business / blog / resume
  / e-commerce / event / non-profit / coming-soon
- [x] `GET /api/templates` → catalogue (filter by category)
- [x] `POST /api/templates/:id/clone` → clone into user's websites
- [x] Add Translation model + `/api/i18n` endpoints
- [x] Seed 11 starter templates (landing, portfolio, blog, etc.) + 5 existing = 16 total
- [x] Seed 144 English translations (6 namespaces) — English is principal/fallback language
- [x] Add test file for translations + templates (20 tests, need minor fixes to response format assertions)
- [ ] Frontend work:
  - [ ] Add i18n setup (react-i18next or lightweight solution)
  - [ ] LanguageSwitcher component
  - [ ] Apply i18n to BuilderShell UI strings
  - [ ] Create TemplateGallery page
  - [ ] TemplateCard component
  - [ ] "Start from template" option in website creation modal
- [ ] VS Code dev environment setup:
  - [ ] Create .vscode/launch.json for Flask + React debugging
  - [ ] Create .vscode/settings.json for Python + ESLint configs
  - [ ] Add tasks.json for backend + frontend start commands
  - [ ] Update README with VS Code setup instructions
- [ ] DO NOT publish or deploy — for local VS Code testing only

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
