import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    from crawl4ai import AsyncWebCrawler
    return


@app.cell
def _():
    from descubrimiento.descubrir_sitios import DescubrirSitios
    return


if __name__ == "__main__":
    app.run()
