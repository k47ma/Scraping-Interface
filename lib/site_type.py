# module for determining the site type


HORIZONTAL = 1
VERTICAL = 2


def site_type(soup):
    template = soup.find('div', id="template")
    try:
        template_class = template.get('class')
    except AttributeError:
        return None
    template_class = " ".join(template_class)
    if template_class.find("h_left") != -1 or template_class.find("h_center") != -1 \
            or template_class.find("essential") != -1:
        return HORIZONTAL
    elif template_class.find("vertical") != -1:
        return VERTICAL
