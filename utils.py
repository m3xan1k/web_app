def render(html: str, **kwargs) -> str:
    return html.format(**kwargs)


def redirect(location: str) -> tuple:
    return (f'HTTP/1.1 301 Moved permanently\nLocation: http://{location}\n\n', 301)
