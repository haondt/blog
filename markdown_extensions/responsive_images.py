# responsive_images.py
# requires hyperscript
from markdown import Extension
from markdown import util
from markdown.inlinepatterns import Pattern
import xml.etree.ElementTree as etree
from jinja2 import Template

TEMPLATE = """<div class="image-container">
    {% for path, caption, size in images %}
    <a _="on click remove .is-hidden from the next .modal-image">
        <figure>
            <img src="{{ path | e }}" alt="Image {{ loop.index }}" class="{{ size }}">
            {% if caption %}<figcaption>{{ caption | e }}</figcaption>{% endif %}
        </figure>
    </a>
    <div class="modal-image is-hidden" _="
        on click add .is-hidden to me end
        on keydown from elsewhere
            if I do not match .is-hidden
                add .is-hidden to me
        ">
        <div class="modal-image-background">
        </div>
        <div class="modal-image-container">
            <img src="{{ path | e }}">
        </div>
    </div>
    {% endfor %}
</div>"""

class ResponsiveImagesPattern(Pattern):
    """Pattern to match responsive images syntax and convert to HTML."""
    
    def handleMatch(self, m):
        """Convert the matched pattern into HTML elements."""
        container = etree.Element('div')
        # container.set('class', 'image-container')
        
        full_data = m.group(2)
        
        # Handle the case where the size is included
        if '|' in full_data:
            parts = full_data.split('|')
            paths_str = parts[0]
            captions_str = parts[1] if len(parts) > 1 else ''
            size_str = parts[2] if len(parts) > 2 else ''
        else:
            paths_str = full_data
            captions_str = ''
            size_str = ''
        
        paths = [p.strip() for p in paths_str.split(',')]
        captions = [c.strip() for c in captions_str.split(',')] if captions_str else [''] * len(paths)
        sizes = [size_str.strip()] * len(paths) if size_str else ['medium'] * len(paths)  # Default size is 'medium'

        template = Template(TEMPLATE)
        html = template.render(images=zip(paths, captions, sizes))
        container.text = util.AtomicString(html)
        container.text = self.md.htmlStash.store(html)
        return container
        
        for i, (path, caption, size) in enumerate(zip(paths, captions, sizes), 1):
            # Create the anchor tag to make the image clickable
            anchor = etree.SubElement(container, 'a')
            anchor.set('href', path)
            anchor.set('target', '_blank')  # Open the link in a new tab
            
            figure = etree.SubElement(anchor, 'figure')
            
            img = etree.SubElement(figure, 'img')
            img.set('src', path)  # Use the path for the image source
            img.set('alt', f'Image {i}')
            
            # Apply the size as a class
            img.set('class', size)
            
            if caption:
                figcaption = etree.SubElement(figure, 'figcaption')
                figcaption.text = caption
        
        return container


class ResponsiveImagesExtension(Extension):
    """Markdown extension for responsive images."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # The updated regular expression to handle size and captions
        self.pattern = r'\[responsive-images\]\(([\s\S]+?)\)'
    
    def extendMarkdown(self, md):
        responsive_images = ResponsiveImagesPattern(self.pattern, md)
        md.inlinePatterns.register(responsive_images, 'responsive_images', 175)

def makeExtension(**kwargs):
    return ResponsiveImagesExtension(**kwargs)

