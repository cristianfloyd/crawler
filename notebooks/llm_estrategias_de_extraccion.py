import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    from crawl4ai import JsonCssExtractionStrategy
    from crawl4ai import LLMConfig

    async def llm_extraction_no_schema():
        pass

    return


if __name__ == "__main__":
    app.run()
