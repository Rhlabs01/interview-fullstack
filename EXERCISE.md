# Take-home exercise: medication detection in visit notes

## Goal

Clinicians write free-text **visit notes** that mention medications in messy,
real-world ways — misspelled, abbreviated, or by brand name. Your job is to make
those medications **light up in the note**, with the matching **RxNorm**
information available to the reader.

Concretely, when a clinician views a visit note, every medication mention should
be:

1. **detected** and **highlighted** in the note text,
2. **fuzzy-matched** to a normalized RxNorm concept — even when the note has a
   misspelling (`metformn`), shorthand (`HCTZ`, `APAP`, `ASA`, `MTX`), or an
   alternative/brand name (`Glucophage`, `Tylenol`, `Advil`),
3. **displayed** with its structured RxNorm data, and
4. for misspellings, the display must also call out the **misspelling → proper
   spelling**.

How you present (3) is your call — think about what UI makes the most sense.

## Stretch Goals

**Form and dosage.** Some mentions include form (e.g. tablets, capsule) or
dosage (e.g. 250mg). Handle that when it's there and highlight them together.

**Catalog import.** `POST /api/medications/import` builds the catalog. Look at
how it runs, then think about possible failure cases and make them more robust.

## Ground rules

- **Timebox:** aim for under 45 minutes. It's fine to leave things unfinished —
  tell us what you'd do with more time.
- **Use any tools you like, including AI coding assistants.** We assume you'll use
  them; we're evaluating your engineering judgment, not whether you typed every
  line. Be ready to explain and defend your choices.
- **Deliverables:** a deployed URL and a short video recording explaining your
decisions and approach. Bonus if you can also include your coding agent transcript
in the submission!

## What's already built (the scaffold)

You do **not** need to build the app from scratch. The following is provided:

- **Visit notes** — each visit has an editable free-text notes field
  (`frontend/src/pages/VisitPage.tsx`), currently rendered as plain text. Seed
  data deliberately includes exact names, brand names, shorthand, misspellings,
  and some forms and doses.
- **RxNorm reference catalog** — a `medications` table of normalized RxNorm
  concepts (RxCUI, normalized name, term type, brand names, drug class; no
  dosages), browsable in the UI at **`/medications`**.
  - `GET /api/medications?search=&limit=&offset=` — **paginated** search over the
    catalog (default 100 rows, max 1000), returning `total` alongside the page.
  - `GET /api/medications/{rxcui}` — one concept.
  - `POST /api/medications/import` — import the full RxNorm ingredient set from
    [RxNav](https://rxnav.nlm.nih.gov). Runs in the background; poll
    `GET /api/medications/import` for progress.
  - `POST /api/medications/scrape` — resolve a handful of specific names
    (`{"names": ["montelukast", …]}`). Several requests per name, so this is for
    targeted additions, not bulk.
  - `GET /api/rxnorm/lookup?name=<name>` — **exact** normalized lookup (catalog
    first, then live RxNav). This is intentionally *not* fuzzy.

  **The catalog is big on purpose.** A full import is ~15,000 ingredient
  concepts. You cannot paste it into an LLM prompt, and you should not scan it
  linearly for every mention.
- **Analysis endpoint + contract** — `POST /api/visits/{visit_id}/analyze` exists
  and returns a `NoteAnalysis` (see `backend/app/schemas.py`), but `analyze_note` in
  `backend/app/routers/analysis.py` is an **empty stub**: it detects nothing.

Run the app, open a visit, and the note renders as plain text. Everything from
detection through display is yours to build.

## What we're evaluating

- **Technical Design** of the matching approach and how you use the LLM.
- **Code quality**: read over your code and tests - you are responsible for what you generate.
- **Product sense** in how you present highlights and the RxNorm detail.

