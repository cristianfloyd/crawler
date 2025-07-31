import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    # Ejemplo sencillo de scraping
    import asyncio
    from crawl4ai import AsyncWebCrawler

    async def main(url):
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url)
            print(result.markdown)  # Print first 300 chars

    return AsyncWebCrawler, main


@app.cell
async def _(main, url):
    await main(url)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Configuracion""")
    return


@app.cell
def _(AsyncWebCrawler):
    from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode

    async def config_example(url):
        browser_conf = BrowserConfig(headless=True)  # or False to see the browser
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS
        )

        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_conf
            )
            print(result.markdown)

    return (config_example,)


@app.cell
async def _(config_example, url):
    await config_example(url)
    return


if __name__ == "__main__":
    app.run()
