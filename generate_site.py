import os
import re
import shutil
from markdown_it import MarkdownIt
from jinja2 import Environment, FileSystemLoader

# Percorsi principali
pages_dir = 'pages'
output_dir = 'output'
templates_dir = 'templates'

# Carica il template con Jinja2
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('base.html')

# Assicura che la cartella di output esista
os.makedirs(output_dir, exist_ok=True)

# Configura markdown-it-py per il parsing Markdown
md = MarkdownIt()

# Funzione per estrarre link interni e immagini Obsidian
def get_md_matches(content):
    md_reg = r'(!)?\[\[(?:(.+?)\|)?(.+?)\]\]'
    matches = re.finditer(md_reg, content)
    
    output_array = [
        {
            'link': match.group(3),
            'alt': match.group(2) or "",
            'isEmbed': bool(match.group(1)),
            'original': match.group(0)
        }
        for match in matches
    ]
    
    return output_array

# Funzione per convertire i link interni di Obsidian in link HTML
def convert_obsidian_links(text):
    matches = get_md_matches(text)
    
    for match in matches:
        if match['isEmbed']:
            # If it's an embedded image
            replacement = f'<img src="{match["link"]}" alt="{match["alt"]}">'
        else:
            # If it's a regular internal link
            replacement = f'<a href="{match["link"]}.html">{match["alt"] or match["link"]}</a>'
        
        # Replace original Obsidian syntax with the generated HTML
        text = text.replace(match['original'], replacement)
    
    return text

# Lista delle pagine generate per il menu
pages = []

# Genera un file HTML per ogni file Markdown
for filename in os.listdir(pages_dir):
    if filename.endswith('.md'):
        # Legge il file Markdown
        with open(os.path.join(pages_dir, filename), 'r', encoding='utf-8') as f:
            text = f.read()

        # Converte i link interni di Obsidian
        text = convert_obsidian_links(text)

        # Converte il contenuto Markdown in HTML
        html_content = md.render(text)

        # Nome della pagina per il menu
        page_title = filename.replace('.md', '').title()

        # Renderizza il contenuto nel template
        output_content = template.render(
            title=page_title,
            content=html_content,
            pages=[f"{file.replace('.md', '.html')}" for file in os.listdir(pages_dir) if file.endswith('.md')]
        )

        # Salva la pagina come file HTML
        output_filename = os.path.join(output_dir, filename.replace('.md', '.html'))
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        # Aggiunge al menu
        pages.append((page_title, filename.replace('.md', '.html')))

# Genera la homepage (index.html) con i link a tutte le pagine
index_content = template.render(
    title="Home",
    content="<h1>Indice dei Contenuti</h1><ul>" +
            "".join(f'<li><a href="{page[1]}">{page[0]}</a></li>' for page in pages) +
            "</ul>",
    pages=[page[1] for page in pages]
)

# Salva la homepage come index.html
with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_content)

print("Sito generato nella cartella 'output'")
