from fastapi.openapi.docs import get_swagger_ui_html


def custom_docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="URL Shortener Service — Docs",
        swagger_favicon_url="/static/favicon.ico",
    )
