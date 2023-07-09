from streamlit.components.v1 import html
from streamlit_javascript import st_javascript


def get_url():
    return st_javascript("await fetch('').then(r => window.parent.location.href)")


def open_page(url):
    st_javascript(f"window.open('{url}', '_blank').focus()")
