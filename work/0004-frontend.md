# Intent 0004: the front end in React, small components

- **Id**: 0004
- **What we want**: the Board screen rebuilt in React as small components, one per folder under the same shape rules as everything else, served by the existing Python API. Pages as Python strings stop.
- **Why**: the Board said so 2026-09-05 after three reopens of one page job. A page held in a Python string cannot be split into pieces a cheap model builds and tests reliably; components can, and each is its own V.
- **Care level**: Low for the components, High for the decision surfaces (Release, Yes, No), which write to the record.
- **How the Board will say yes**: shown the same board, modal and decisions working in the React build, with the Python pages removed, and one component reopened and rebuilt by a Builder unattended.
- **Out of scope**: changing the API, changing the record, any design system or styling library, server-side rendering.

## Architect decisions, for the Board to confirm

1. **Stack**: React with TypeScript, built by Vite, tested with Vitest and Testing Library. Chosen because they are the mainstream defaults every cheap model has seen most, which is the cost lever.
2. **Shape rules apply unchanged**: one component per folder under `web/src/`, three files: `Name.tsx`, `Name.test.tsx`, `Name.md`. Fifty lines per component file, one exported component, tests exempt from length. The linter is ESLint with the equivalent complexity limits; the formatter is Prettier. The shape checker grows one rule set for `web/src`.
3. **The API stays Python** and unchanged; the React build is static files served by the existing server from `web/dist`. One tiny route job adds that.
4. **Builders need Node**: a Node toolchain becomes an environment requirement like Dolt. The Builder skill gains the commands; sheets name them exactly.
5. **Components, first cut**: Board, Column, Card, StatePill, ItemModal, DecisionPanel, ReasonInput, IntentTable, Tree, Breadcrumb, plus one `api` module of fetch functions and one `App`. Each is a Story pair; no component may reach the API except through `api`.

## Stories

### Story 0004-1: toolchain and shape rules for web

- **One thing it must do**: a fresh checkout can build, lint, format and test an empty React app under `web/`, and the shape checker enforces the folder and length rules there.
- **Customer**: every later Story. **Supplier**: Builders; the Architect owns the config files as spec.
- **Contract**: `npm run build`, `npm run lint`, `npm run format:check`, `npm test` all exit zero on the empty app; `tools/lint.py` reports a `.tsx` component over fifty lines or a folder with the wrong three files.
- **Checklist**: 1. The four commands pass on a clean checkout. [testing] 2. A fixture folder with a 51-line component fails the shape checker. [testing] 3. The Builder skill lists the four commands. [looking]
- **Job pairs**: `web_shape` (Python, the rule set in tools/lint.py) and the config files as looking items.

### Story 0004-2: data layer and leaf components

- **One thing it must do**: `api` functions for every existing route, and the leaf components StatePill, Card, Breadcrumb, ReasonInput, each rendering from props only.
- **Contract**: every component has a test that renders it from props and asserts the text; `api` is tested against a mocked fetch. No component imports another Story's component yet.
- **Job pairs**: `api`, `StatePill`, `Card`, `Breadcrumb`, `ReasonInput`.

### Story 0004-3: composed views

- **One thing it must do**: Column, Board, IntentTable, Tree, ItemModal, DecisionPanel composed from Story 0004-2, reproducing today's two pages.
- **Contract**: DecisionPanel is the only component that posts; it shows Release for a waiting intent, Yes and No for a checking intent or proposal, and names the decision in words; the modal shows the full sheet text.
- **Job pairs**: `Column`, `Board`, `IntentTable`, `Tree`, `ItemModal`, `DecisionPanel`, `App`.

### Story 0004-4: served and switched over

- **One thing it must do**: the Python server serves `web/dist` at `/` and `/columns`, the Python page functions are deleted with their tests, and the Board sees no difference except speed.
- **Job pairs**: `serve_static` (Python), removals as a looking item.

### Story 0004-5: one unattended component rebuild

- **One thing it must do**: the Board changes one visual rule on one component's sheet; pullers rebuild it end to end; cost per line recorded.

## Order

0004-1, then 0004-2, then 0004-3, then 0004-4, then 0004-5.

## Status

Drafted 2026-09-05 by the Architect at the Board's request. Not loaded into the record; awaiting the Board's confirmation of decisions 1 to 4 and release.
