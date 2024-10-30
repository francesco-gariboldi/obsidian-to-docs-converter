# obsidian-to-docs-converter
A Python basic tool to convert an Obsidian vault to HTML documentation, shipped with an optional ready compiler (uses `pyinstaller`).


### Instructions
1) Clone it directly in your vault.
2) `pip install -r requirements.txt` # Installs necessary Python packages (creating a virtual environment first is highly suggested)
3)  Run `python generate_site.py`

An `/output` will be generated with all the HTML converted files (notes are converted from `.md` to `.html`).
Obsidian links are pretty well converted, but sometimes you can get an error. It distinguishes file obsidian links (`![[file]]`) from non file ones.


### Limits:
All notes must be in the same folder (doesn'work on folder structures).
No citations rendering.

### Next features (work in progress):
- Recognizing and copying vault's entire folder structure
- Citations rendered as happens with Pandoc citations to APA7th edition with the "Pandoc Reference List" plugin in Obsidian. 
