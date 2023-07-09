from streamlit.components.v1 import html


def open_page(url):
    open_script = f"""
        <script type="text/javascript">
            window.open('{url}', '_blank').focus();
        </script>
    """
    html(open_script)
