import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


    return (
        AsyncWebCrawler,
        CacheMode,
        CrawlerRunConfig,
        DefaultMarkdownGenerator,
        PruningContentFilter,
    )


@app.cell
def _(DefaultMarkdownGenerator, PruningContentFilter):
    url = "https://lcd.exactas.uba.ar/materias"

    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
    )


    return md_generator, url


@app.cell
def _(CacheMode, CrawlerRunConfig, md_generator):
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator
    )
    return (config,)


@app.cell
async def _(AsyncWebCrawler, config, url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=config)
        print("Raw Markdown length:", len(result.markdown.raw_markdown))
        print("Fit Markdown length:", len(result.markdown.fit_markdown))
    return


if __name__ == "__main__":
    app.run()
