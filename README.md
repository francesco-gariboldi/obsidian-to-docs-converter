# obsidian-to-docs-converter
A bsaic tool to convert an Obsidian vault to HTML documentation

### Instructions
1) Clone it directly in your vault.
2) For now you have to put all `.md` files (Obsidian notes) and images in the `/pages` directory.
2) Run python generate_site.py
3) An `/output` will be generated with all the HTML converted files (notes are converted from `.md` to `.html`).

Obsidian links are pretty well converted, but sometimes you can get an error. It distinguishes file obsidian links (`![[file]]`) from non file ones.

### Limits:
Only transfers notes. All notes must be in the same folder (doesn'work on folder structures)

### Next features (work in progress):
- Also transfer images
- Recognize and reproduce vaults entire folder structure
