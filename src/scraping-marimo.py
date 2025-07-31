import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import crawl4ai
    from crawl4ai import AsyncWebCrawler

    print(crawl4ai.__version__.__version__)
    return (AsyncWebCrawler,)


@app.cell
def _():
    import asyncio
    import sys
    import os
    import nest_asyncio
    from descubrimiento import DescubrirSitios, PATRONES_INTERES, DEPARTAMENTOS_CONOCIDOS, DOMINIO, URLS_BASE
    return (DescubrirSitios,)


@app.cell
def _(DescubrirSitios):
    descubridor = DescubrirSitios()
    return (descubridor,)


@app.cell
def _(AsyncWebCrawler, descubridor):
    async def procesar_url_simple(url):
        async with AsyncWebCrawler() as crawler:
            resultado = await descubridor.procesar_url(crawler, url)
            return resultado
    return (procesar_url_simple,)


@app.cell
async def _(procesar_url_simple):
    url_ejemplo = "https://lcd.exactas.uba.ar/"
    print("Iniciando la prueba del navegador...")
    links = await procesar_url_simple(url_ejemplo)
    print(links)

    print("Prueba finalizada.")
    return (links,)


@app.cell
def _(links):
    links
    return


if __name__ == "__main__":
    app.run()
