import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import CosineStrategy
from bs4 import BeautifulSoup

URL_MATERIAS = "https://lcd.exactas.uba.ar/materias/"
SELECTOR_LINKS = "h4 > a"
SELECTOR_PANEL_MATERIA = "div.fusion-panel.panel-default"
OUTPUT_FILE = "materias.json"
OUTPUT_RAG_FILE = "materias_rag.json"


# Define qué funciones se importarán con
# "from crawler.scrap_materias_rag import *"
__all__ = [
    "obtener_links_materias",
    "obtener_materias_desde_html",
    "extraer_contenido_materia",
    "procesar_todas_las_materias",
    "main",
]


async def obtener_links_materias(crawler):
    """
    Obtiene los nombres de las materias y
    sus IDs de panel desde la página principal.

    Args:
        crawler: Instancia de AsyncWebCrawler

    Returns:
        list: Lista de diccionarios con nombre y
        el ID del panel de cada materia.
    """
    # Obtenemos el HTML completo de la página una sola vez
    result = await crawler.arun(url=URL_MATERIAS)

    if not result or not result.markdown:
        print(f"⚠️ No se pudo obtener el contenido de: {URL_MATERIAS}")
        return []

    # Usamos BeautifulSoup para parsear el HTML y encontrar los elementos
    soup = BeautifulSoup(result.html, "html.parser")

    materias_data = []
    # Encontramos todos los paneles de materia
    panels = soup.select(SELECTOR_PANEL_MATERIA)

    for panel in panels:
        # Extraemos el nombre de la materia
        title_span = panel.select_one(
            "h4.panel-title.toggle a span.fusion-toggle-heading"
        )
        nombre = title_span.get_text(strip=True) if title_span else "Nombre Desconocido"

        # Extraemos el ID del panel de contenido
        content_div = panel.select_one("div.panel-collapse")
        panel_id = content_div.get("id") if content_div else None

        if nombre and panel_id:
            materias_data.append({"nombre": nombre, "panel_id": panel_id})

    return materias_data


async def extraer_contenido_materia(crawler, materia_data, full_html_content):
    """
    Extrae el contenido de una materia específica usando CosineStrategy correctamente.

    Args:
        crawler: Instancia de AsyncWebCrawler
        materia_data: Diccionario con 'nombre' y 'panel_id' de la materia
        full_html_content: El contenido HTML completo de la página de materias

    Returns:
        dict: Información de la materia con sus chunks de texto
    """
    print(f"⏳ Procesando: {materia_data['nombre']}")

    soup = BeautifulSoup(full_html_content, "html.parser")

    # Encontramos el div de contenido de la materia usando el panel_id
    content_div = soup.find('div', {'id': materia_data['panel_id']})
    if content_div:
        content_div = content_div.find('div', class_='panel-body toggle-content fusion-clearfix')

    if not content_div:
        print(
            f"⚠️ No se encontró el contenido para {materia_data['nombre']} con ID: {materia_data['panel_id']}"
        )
        return {
            "nombre": materia_data["nombre"],
            "url": URL_MATERIAS + "#" + materia_data["panel_id"],
            "chunks": ["Contenido no encontrado."],
        }

    # Extraemos el texto del contenido
    content_text = content_div.get_text(separator="\n", strip=True)
    
    # Si el contenido es muy corto, lo devolvemos directamente
    if len(content_text.split()) < 20:
        return {
            "nombre": materia_data["nombre"],
            "url": URL_MATERIAS + "#" + materia_data["panel_id"],
            "chunks": [content_text],
        }

    try:
        # Crear una estrategia de CosineStrategy para chunking semántico
        chunking_strategy = CosineStrategy(
            semantic_filter=f"materia {materia_data['nombre']} información académica",
            word_count_threshold=10,
            sim_threshold=0.4,
            top_k=5,
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            verbose=False
        )
        
        # Crear un HTML temporal con solo el contenido de esta materia
        temp_html = f"""
        <html>
        <body>
        <div class="materia-content">
        {content_div}
        </div>
        </body>
        </html>
        """
        
        # Crear un archivo temporal con el contenido
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(temp_html)
            temp_file_path = temp_file.name
        
        try:
            # Usar el crawler con la estrategia de extracción
            result = await crawler.arun(
                url=f"file://{temp_file_path}",
                extraction_strategy=chunking_strategy
            )
            
            if result.success and result.extracted_content:
                try:
                    extracted_data = json.loads(result.extracted_content)
                    if isinstance(extracted_data, list) and extracted_data:
                        chunks = [item.get('content', item.get('text', str(item))) for item in extracted_data]
                    else:
                        chunks = [str(extracted_data)]
                except json.JSONDecodeError:
                    chunks = [result.extracted_content]
            else:
                # Fallback: chunking básico por párrafos
                paragraphs = content_text.split('\n\n')
                chunks = [p.strip() for p in paragraphs if p.strip() and len(p.split()) >= 5]
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"⚠️ Error en chunking para {materia_data['nombre']}: {e}")
        # Fallback: chunking básico por párrafos
        paragraphs = content_text.split('\n\n')
        chunks = [p.strip() for p in paragraphs if p.strip() and len(p.split()) >= 5]

    # Si no hay chunks, usar el contenido completo
    if not chunks:
        chunks = [content_text]

    return {
        "nombre": materia_data["nombre"],
        "url": URL_MATERIAS + "#" + materia_data["panel_id"],
        "chunks": chunks,
    }


async def extraer_contenido_materia_simple(crawler, materia_data, full_html_content):
    """
    Versión simplificada que usa chunking básico en lugar de CosineStrategy.
    Recomendada si CosineStrategy causa problemas.

    Args:
        crawler: Instancia de AsyncWebCrawler
        materia_data: Diccionario con 'nombre' y 'panel_id' de la materia
        full_html_content: El contenido HTML completo de la página de materias

    Returns:
        dict: Información de la materia con sus chunks de texto
    """
    print(f"⏳ Procesando (método simple): {materia_data['nombre']}")

    soup = BeautifulSoup(full_html_content, "html.parser")

    # Encontramos el div de contenido de la materia usando el panel_id
    content_div = soup.find('div', {'id': materia_data['panel_id']})
    if content_div:
        content_div = content_div.find('div', class_='panel-body toggle-content fusion-clearfix')

    if not content_div:
        print(
            f"⚠️ No se encontró el contenido para {materia_data['nombre']} con ID: {materia_data['panel_id']}"
        )
        return {
            "nombre": materia_data["nombre"],
            "url": URL_MATERIAS + "#" + materia_data["panel_id"],
            "chunks": ["Contenido no encontrado."],
        }

    # Extraemos el texto del contenido
    content_text = content_div.get_text(separator="\n", strip=True)
    
    # Chunking básico pero efectivo
    # 1. Dividir por párrafos
    paragraphs = content_text.split('\n\n')
    
    # 2. Filtrar párrafos muy cortos
    meaningful_paragraphs = [p.strip() for p in paragraphs if p.strip() and len(p.split()) >= 5]
    
    # 3. Si los párrafos son muy largos, dividirlos por oraciones
    chunks = []
    for paragraph in meaningful_paragraphs:
        if len(paragraph.split()) > 100:  # Párrafo muy largo
            sentences = paragraph.split('. ')
            current_chunk = ""
            for sentence in sentences:
                if len((current_chunk + sentence).split()) <= 100:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
        else:
            chunks.append(paragraph)
    
    # Si no hay chunks, usar el contenido completo
    if not chunks:
        chunks = [content_text]

    return {
        "nombre": materia_data["nombre"],
        "url": URL_MATERIAS + "#" + materia_data["panel_id"],
        "chunks": chunks,
    }


async def procesar_todas_las_materias(usar_cosine_strategy=True):
    """
    Procesa todas las materias disponibles extrayendo su contenido.

    Args:
        usar_cosine_strategy: Si True, usa CosineStrategy. Si False, usa chunking básico.

    Returns:
        list: Lista con la información de todas las materias procesadas
    """
    all_materias = []
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Primero, obtenemos el HTML completo de la página de materias
        full_page_result = await crawler.arun(url=URL_MATERIAS)
        if not full_page_result or not full_page_result.markdown:
            print(
                f"⚠️ No se pudo obtener el contenido completo de la página: {URL_MATERIAS}"
            )
            return []

        full_html_content = full_page_result.html

        # Luego, obtenemos la lista de materias (nombres e IDs de panel)
        materias_list = await obtener_links_materias(crawler)

        for materia_data in materias_list:
            try:
                if usar_cosine_strategy:
                    datos = await extraer_contenido_materia(
                        crawler, materia_data, full_html_content
                    )
                else:
                    datos = await extraer_contenido_materia_simple(
                        crawler, materia_data, full_html_content
                    )
                all_materias.append(datos)
            except Exception as e:
                print(f"⚠️ Error con {materia_data['nombre']}: {e}")
                
    return all_materias


async def obtener_materias_desde_html(crawler):
    result = await crawler.arun(url=URL_MATERIAS, bypass_cache=True)
    soup = BeautifulSoup(result.html, 'html.parser')

    materias = []

    for panel in soup.select("div.fusion-panel.panel-default"):
        nombre_el = panel.select_one("span.fusion-toggle-heading")
        descripcion_el = panel.select_one("div.panel-body.toggle-content")

        if not nombre_el or not descripcion_el:
            continue

        nombre = nombre_el.get_text(strip=True)
        descripcion = descripcion_el.get_text(separator=" ", strip=True)

        materias.append({
            "nombre": nombre,
            "descripcion": descripcion
        })

    return materias


async def main():
    print("🚀 Iniciando procesamiento de materias...")
    
    # Primero intentar con CosineStrategy
    try:
        print("📊 Intentando con CosineStrategy...")
        all_materias = await procesar_todas_las_materias(usar_cosine_strategy=True)
    except Exception as e:
        print(f"⚠️ Error con CosineStrategy: {e}")
        print("📝 Usando método de chunking básico...")
        all_materias = await procesar_todas_las_materias(usar_cosine_strategy=False)

    with open(OUTPUT_RAG_FILE, "w", encoding="utf-8") as f:
        json.dump(all_materias, f, ensure_ascii=False, indent=2)

    print(f"✅ Archivo generado en formato RAG: {OUTPUT_RAG_FILE}")
    print(f"Total de materias procesadas: {len(all_materias)}")
    
    # Mostrar estadísticas de chunks
    total_chunks = sum(len(materia['chunks']) for materia in all_materias)
    promedio_chunks = total_chunks / len(all_materias) if all_materias else 0
    print(f"Total de chunks generados: {total_chunks}")
    print(f"Promedio de chunks por materia: {promedio_chunks:.2f}")


if __name__ == "__main__":
    asyncio.run(main())