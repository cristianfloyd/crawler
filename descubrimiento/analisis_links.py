# Check crawl4ai version
import crawl4ai
from crawl4ai import AsyncWebCrawler

print(crawl4ai.__version__.__version__)

#crawl4ai-setup
#!crawl4ai-doctor
# If you face with an error try it manually
# !playwright install --with-deps chrome # Recommended for Colab/Linux

import asyncio
import sys
import os
import nest_asyncio

# Solución: Establecer la política de bucle de eventos correcta para Windows.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# nest_asyncio permite que asyncio se ejecute dentro de un entorno
# como Jupyter Notebook que ya tiene su propio bucle de eventos.
nest_asyncio.apply()
# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('.'))))

# Importar desde el módulo
from crawler.descubrimiento import DescubrirSitios, PATRONES_INTERES, DEPARTAMENTOS_CONOCIDOS, DOMINIO, URLS_BASE

# 1. Crear instancia de la clase:
descubridor = DescubrirSitios()

async def procesar_url_simple(url):
    async with AsyncWebCrawler() as crawler:
        resultado = await descubridor.procesar_url(crawler, url)
        return resultado


# Ejecutamos la función asíncrona
url_ejemplo = "https://lcd.exactas.uba.ar/"
print("Iniciando la prueba del navegador...")
links = asyncio.run(procesar_url_simple(url_ejemplo))
print(links)

print("Prueba finalizada.")
