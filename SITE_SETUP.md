# Jekyll site setup

The site builds from the repository root. GitHub Actions builds pull requests without deploying, and builds and deploys pushes to main or manual runs.

## Enable deployment

In repository Settings > Pages > Build and deployment, set Source to GitHub Actions. The workflow does not change this setting automatically. Check the Actions tab after committing or run the workflow manually after changing the setting.

In Settings > Pages, set Custom domain to skroxiousdm.com. Configure the domain's DNS separately and enable Enforce HTTPS when the certificate is ready. The CNAME file documents the domain but does not configure DNS or replace the Pages custom-domain setting for this Actions-based deployment.

Expected production URL: https://skroxiousdm.com/

## Edit the site

- index.md: existing project introduction.
- projects.md: RPG project overview.
- rules.md: current manuscript links and future online rules.
- about.md: creator introduction.
- blog.md: automatic list of published posts.
- _posts/: development posts named YYYY-MM-DD-title.md.
- campaign/index.md: campaign archive entry points.
- _layouts/default.html: shared accessible HTML layout and navigation.
- assets/css/rpg.css: manuscript-inspired palette and responsive styling.
- _config.yml: site metadata, custom-domain URL, exclusions and defaults.
- .github/workflows/ci.yml: Jekyll build and Pages deployment.

Create posts with YAML front matter containing title and date. The existing default layout is inherited automatically. Categories and tags are optional. The blog page lists posts newest first. Use relative_url for internal links so paths remain consistent.

The old mkdocs.yml, root ci.yml and all campaign sources remain unchanged for archival use. The root ci.yml is not an Actions workflow. Do not switch the publishing source to /docs: that directory is excluded by the active Jekyll configuration.

## Manuscript reference

The visual reference is SkroxiousDM/2d12GameSystem, docs/2d12System/common.typ: charcoal #1c1f24, paper #fcfbf8, navy #2d4a66, steel blue #3f6a8f and pewter #8d99a6. Typography prefers EB Garamond and Source Sans 3 when installed, with local system fallbacks. Font files and external font services are not bundled or loaded.

## Campaign archive

Existing docs, images and root campaign notes are excluded from direct Jekyll publication. Campaign pages and workflow-staged includes are maintained separately; this update does not change them. Exclusions are publication choices, not access controls: the repository itself is public.

For a curated web edition, add a Markdown page with YAML front matter under campaign/, use standard Markdown links with relative_url for site paths, and link it from campaign/index.md. Review spoilers, source attribution, redistribution permissions and embedded images before publishing archive content. Typst manuscripts are not compiled by this workflow.

## Published downloads

The rules page preserves the existing GitHub manuscript links. Add itch.io product links when available. Do not commit paid-only PDFs or private source material to this public repository.
