def index():
    with open('./templates/index.html') as f:
        html = f.read()
        return html


def about():
    with open('./templates/about.html') as f:
        html = f.read()
        return html