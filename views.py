from utils import render


def index():
    name = 'World'
    with open('./templates/index.html') as f:
        html = f.read()
        return render(html, name=name)


def about():
    with open('./templates/about.html') as f:
        html = f.read()
        return render(html)
