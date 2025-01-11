from pelican import signals
import logging
import re

log = logging.getLogger(__name__)

pattern = r'\[responsive-images\]\((([^|\s,]+),)*([^|\s,]+)\|(([^\n\r,]+),)*([^\n\r,]+)\)'

def test(sender):
    log.error("%s initialized !!", sender._content)

def parse_image_data(match):
    log.error(match)

def generate_html(image_data):
    return ''

def process_content(content):
    if not content._content:
        return
    def replace_pattern(match):
        log.error(match)

        image_data = parse_image_data(match)
        return generate_html(image_data)

    # if 'Midas' in content._content:
    #     log.error(content._content)
    log.error(re.findall(pattern, content._content))

    content._content = re.sub(pattern, replace_pattern, content._content)

def register():
    signals.static_generator_init.connect(process_content)
