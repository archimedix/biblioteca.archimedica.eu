<!-- .github/copilot-instructions.md
     Guidance for AI coding agents working on the biblioteca.archimedica.eu repo.
     Keep this short, concrete and specific to the repository's structure and workflows.
-->

# Copilot instructions — biblioteca.archimedica.eu

This repository preserves and presents archival content for the Biblioteca Archimedica project
(static site + scraping tools + legacy PHP app). Follow the notes below to be productive quickly.

Core points
- The site is static and served via GitHub Pages. The entry point is `index.html` and static
  archives live under `oldwp/`, `waybiblio/`, and `ebook/`.
- Three parallel data sources are intentionally preserved: `oldwp/` (raw HTML), `waybiblio/`
  (structured JSON produced by the scraper), and the WordPress XML `bibliotecaarchimedica.wordpress.2016-03-26.xml`.

What to modify and where
- Content fixes or HTML updates: edit files under `oldwp/` or `index.html` for the main landing page.
- Add or transform structured data: update `waybiblio/summary.json` or the `wayback-scraper/` scripts.
- Legacy PHP catalog: `app/catalog.php` is a legacy interface — avoid large refactors unless requested.

Developer workflows and commands
- No build step for the static site. To run the scraper (Python 3):
  - `cd wayback-scraper`
  - `pip3 install -r requirements.txt`
  - `python3 wayback_scraper.py`
- PHP components (legacy): verify with a local PHP built-in server when needed:
  - `php -S localhost:8000 -t app`

Repository-specific patterns and conventions
- Content is intentionally duplicated in three formats for preservation; do not remove any source
  without confirming which canonical copy is requested.
- `waybiblio/articles/*.json` stores one article per file (use `summary.json` for bulk operations).
- Image assets are referenced with local filenames (e.g. `images/`, `ebook/`); prefer relative paths.

Integration points & important files
- `wayback-scraper/wayback_scraper.py` — entry point for scraping and generating `waybiblio/` outputs.
- `app/` — legacy PHP ebook catalog (uses eBookLib). Touch cautiously; tests are not present.
- `bibliotecaarchimedica.wordpress.2016-03-26.xml` — WordPress export: use for full metadata and comments.

Examples (concrete patterns to follow)
- When extracting structured content prefer `waybiblio/summary.json` rather than parsing `oldwp/` HTML.
- To add a derived JSON file for an article, place it in `waybiblio/articles/` alongside existing files and
  include the keys: `title`, `date`, `author`, `content`, `images`, `source_url`.

Constraints and do-not-change
- Do not remove `oldwp/` or `bibliotecaarchimedica.wordpress.2016-03-26.xml` — they are authoritative backups.
- Avoid changing image filenames unless you also update all references across `oldwp/`, `waybiblio/`, and `index.html`.

If unsure
- Refer to `CLAUDE.md` for historical context and the `wayback-scraper/README.md` for scraper usage.
- Ask the repository owner (commits are under `archimedix`) before large-scale restructuring.

If you modify these instructions, keep them short and focused on concrete commands, file paths, and
repository-specific constraints.
