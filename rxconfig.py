import reflex as rx

config = rx.Config(
    app_name="short_url",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)