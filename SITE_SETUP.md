# Jekyll site setup

The site builds from the repository root. GitHub Actions builds pull requests without deploying, and builds and deploys pushes to main or manual runs.

## Enable deployment

In repository Settings > Pages > Build and deployment, set Source to GitHub Actions. The workflow does not change this setting automatically. Check the Actions tab after committing or run the workflow manually after changing the setting.

Expected project URL: https://skroxiousdm.github.io/SkroxiousDM/

## Edit the site

- index.md: project introduction.
- campaign/index.md: campaign archive entry points.
- _layouts/default.html: shared accessible HTML layout.
- assets/css/rpg.css: manuscript-inspired palette and responsive styling.
- _config.yml: site metadata, URL, exclusions and defaults.
- .github/workflows/ci.yml: Jekyll build and Pages deployment; replaces the previous MkDocs publisher.

The old mkdocs.yml, root ci.yml and all campaign sources remain unchanged for archival use. The root ci.yml is not an Actions workflow.

## Manuscript reference

The visual reference is SkroxiousDM/2d12GameSystem, docs/2d12System/common.typ: charcoal #1c1f24, paper #fcfbf8, navy #2d4a66, steel blue #3f6a8f and pewter #8d99a6. Typography prefers EB Garamond and Source Sans 3 when installed, with local system fallbacks. Font files and external font services are not bundled or loaded.

## Campaign archive

Existing docs, images and root campaign notes are deliberately excluded from the generated site. The campaign landing page links to their GitHub sources instead. This avoids silently converting Obsidian/MkDocs syntax or duplicating third-party archive material. Exclusions are publication choices, not access controls: the repository itself is public.

For a curated web edition, add a Markdown page with YAML front matter under campaign/, use standard Markdown links with relative_url for site paths, and link it from campaign/index.md. Review spoilers, source attribution, redistribution permissions and embedded images before publishing archive content. Typst manuscripts are not compiled by this workflow.
