# Campaign web editions

Seven root campaign notes are rendered through campaign-*.html wrapper pages. The wrappers sit at the repository root so Jekyll include_relative can read the adjacent Markdown sources; their permalinks publish them under /campaign/.

The original notes remain unchanged and are included at build time. Edit the original Markdown note to update its web edition on the next build. Source exclusions in _config.yml prevent separate raw copies from being published; they do not prevent include_relative from reading the source.

The wrappers capture each note and apply markdownify within the shared default layout. The existing top-level titles are removed from the two sources that already have them, avoiding duplicate page titles. Treasure enables Markdown parsing inside its existing details element. No story text or game mechanics are rewritten.

The campaign index links to all seven generated pages. A Sword of Sunlight and the docs archive are not converted. Existing archive links still point to GitHub. Spoiler notices do not restrict access.

After opening a pull request against main, check that Jekyll builds successfully. Review all seven pages, particularly player-hook tables and the expandable treasure item, before merging. Browser rendering and deployment have not been verified merely by committing these files.
