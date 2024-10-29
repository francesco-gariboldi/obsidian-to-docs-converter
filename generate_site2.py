import os
import re
import shutil
from markdown_it import MarkdownIt
from jinja2 import Environment, FileSystemLoader
from citeproc import CitationStylesStyle, Citation, CitationItem
from citeproc.source.bibtex import BibTeX

# Main paths
pages_dir = 'pages'
output_dir = 'output'
templates_dir = 'templates'
css_filename = 'style.css'
bib_file = 'references.bib'
csl_file = 'apa.csl'

# Load the template with Jinja2
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('base.html')

# Ensure the output folder exists
os.makedirs(output_dir, exist_ok=True)

# Configure markdown-it-py for Markdown parsing
md = MarkdownIt()

# Custom BibTeX class to filter unsupported fields and handle parsing errors
class CustomBibTeX(BibTeX):
    def create_reference(self, key, bibtex_entry):
        # Unsupported fields to remove before processing
        unsupported_fields = [
            'url', 'journaltitle', 'shortjournal', 'urldate', 
            'date', 'langid', 'keywords', 'file', 'shorttitle', 'rights'
        ]
        
        # Remove unsupported fields directly if they exist in the bibtex_entry dictionary
        for field in unsupported_fields:
            if field in bibtex_entry:
                del bibtex_entry[field]

        # Ensure document_type exists and map unsupported BibTeX types to a compatible CSL type
        document_type = bibtex_entry.get('document_type', 'article')  # Default to "article"
        document_type = {
            'online': 'article',
            'webpage': 'article'
        }.get(document_type, document_type)  # Map unsupported types if necessary
        
        # Set document_type explicitly in case it's missing
        bibtex_entry['document_type'] = document_type

        try:
            return super().create_reference(key, bibtex_entry)
        except RuntimeError as e:
            print(f"Warning: Failed to parse BibTeX entry '{key}': {e}")
            return None  # Skip this entry if it raises parsing issues


# Load the bibliography using the custom BibTeX class with UTF-8 encoding
bib_source = CustomBibTeX(bib_file, encoding='utf-8')

# Initialize the citation style for APA formatting
style = CitationStylesStyle(csl_file, validate=False)

# Function to replace Pandoc-style citations with formatted APA citations
def convert_citations(text):
    citation_pattern = r'\[@([^\]]+?)(?:, p\. (\d+))?\]'
    citations = []

    def citation_replacer(match):
        citekey = match.group(1)
        page = match.group(2)
        citation_item = CitationItem(citekey, label='page', locator=page) if page else CitationItem(citekey)
        citation = Citation([citation_item])
        citations.append((citation, citekey))
        return f'[{len(citations) - 1}]'  # Placeholder for citation

    # Replace citations with placeholders and collect Citation objects
    text = re.sub(citation_pattern, citation_replacer, text)

    # Render citations and replace placeholders with formatted APA-style citations
    for i, (citation, citekey) in enumerate(citations):
        rendered_citation = style.render_citation(citation, bib_source)[0]
        text = text.replace(f'[{i}]', rendered_citation)

    return text

# Function to extract Obsidian internal links and images
def get_md_matches(content):
    md_reg = r'(!)?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
    matches = re.finditer(md_reg, content)
    
    output_array = [
        {
            'link': match.group(2).strip(),
            'alt': match.group(3).strip() if match.group(3) else match.group(2).strip(),
            'isEmbed': bool(match.group(1)),
            'original': match.group(0)
        }
        for match in matches
    ]
    
    return output_array

# Function to convert Obsidian internal links to HTML links
def convert_obsidian_links(text):
    matches = get_md_matches(text)
    
    for match in matches:
        if match['isEmbed']:
            replacement = f'<img src="{match["link"]}" alt="{match["alt"]}">'
        else:
            replacement = f'<a href="{match["link"]}.html">{match["alt"] or match["link"]}</a>'
        text = text.replace(match['original'], replacement)
    
    return text

# Function to convert Obsidian callouts to HTML
def convert_callouts(text):
    callout_pattern = r'^\s*>\s*(\[\s*(!|\?|i|x)\s*\])?\s*(.*)$'
    callout_classes = {'!': 'note', '?': 'question', 'i': 'info', 'x': 'warning'}

    def callout_replacer(match):
        callout_type = match.group(2)
        content = match.group(3)
        callout_class = callout_classes.get(callout_type, 'note') if callout_type else 'blockquote'
        return f'<div class="callout {callout_class}"><p>{content}</p></div>'

    lines = text.split('\n')
    for i, line in enumerate(lines):
        lines[i] = re.sub(callout_pattern, callout_replacer, line)
    return '\n'.join(lines)

# List of generated pages for the menu
pages = []

# Generate an HTML file for each Markdown file
for filename in os.listdir(pages_dir):
    if filename.endswith('.md'):
        with open(os.path.join(pages_dir, filename), 'r', encoding='utf-8') as f:
            text = f.read()

        text = convert_callouts(text)
        text = convert_obsidian_links(text)
        text = convert_citations(text)

        html_content = md.render(text)

        page_title = filename.replace('.md', '')[0].upper() + filename.replace('.md', '')[1:]

        output_content = template.render(
            title=page_title,
            content=html_content,
            pages=[f"{file.replace('.md', '.html')}" for file in os.listdir(pages_dir) if file.endswith('.md')]
        )

        output_filename = os.path.join(output_dir, filename.replace('.md', '.html'))
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        pages.append((page_title, filename.replace('.md', '.html')))

index_content = template.render(
    title="Home",
    content="<h1>Indice dei contenuti</h1><ul>" +
            "".join(f'<li><a href="{page[1]}">{page[0]}</a></li>' for page in pages) +
            "</ul>",
    pages=[page[1] for page in pages]
)

with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_content)

css_source = os.path.join(templates_dir, css_filename)
css_dest = os.path.join(output_dir, css_filename)
if os.path.exists(css_source):
    shutil.copy(css_source, css_dest)

for filename in os.listdir(pages_dir):
    src_path = os.path.join(pages_dir, filename)
    dest_path = os.path.join(output_dir, filename)
    if not filename.endswith('.md'):
        shutil.copy(src_path, dest_path)

print("Sito generato nella cartella 'output'")
