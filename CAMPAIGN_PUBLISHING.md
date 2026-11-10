# Campaign web editions

Seven campaign-*.html wrappers publish the original root Markdown notes under /campaign/ using the shared default layout. Original source notes remain unchanged. A Sword of Sunlight and the docs archive are not converted.

## Build preparation

Jekyll 3.10 rejects spaces in include filenames, even after resolving a Liquid variable. Before Jekyll runs, the Actions workflow copies four source notes into _includes/campaign/ under space-free filenames. Those wrappers use standard include tags. The other three wrappers use include_relative with their existing space-free source filenames.

The staged files are build-time copies, not separately maintained source documents. Edit the original root Markdown notes to update the next build. For local builds, run the same four cp commands from the workflow before running Jekyll.

Wrappers apply markdownify to the included content and remove the two existing page-title headings to avoid duplicate titles. Treasure enables Markdown parsing inside its details element. No story text or game mechanics are rewritten.

Original note exclusions prevent separate raw copies from being published. Spoiler notices are not access controls.

## Verification

Require a successful pull-request build before merging. Then verify the production deployment, all seven note pages, player-hook tables and the expandable treasure item. A commit alone does not verify rendering or deployment.
