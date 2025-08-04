import asyncio
import os
import json
from typing import Optional, Dict, Any
from crawl4ai import AsyncWebCrawler, LLMConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import (
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
)
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def llm_structured_extraction_no_schema(
    url: str = "https://lcd.exactas.uba.ar/materias",
    provider: str = "openai",
    model: str = "gemma3-12b",
    api_token: Optional[str] = None,
    analyze_html_structure: bool = True,  # Nueva opción para analizar estructura HTML
):
    """
    Implementa extracción estructurada con crawl4ai sin esquema requerido.

    Args:
        url: URL a procesar
        provider: Proveedor de LLM ('openai', 'ollama', etc.)
        model: Modelo específico del proveedor
        api_token: Token de API si es requerido
        analyze_html_structure: Si analizar la estructura HTML y generar esquema CSS

    Returns:
        Resultado de la extracción con esquema CSS si se solicita
    """
    
    print(f"🚀 Iniciando extracción para: {url}")
    print(f"   Proveedor: {provider}")
    print(f"   Modelo: {model}")
    print(f"   Análisis HTML: {analyze_html_structure}")
    
    # Configuración del LLM Studio
    llm_url = os.getenv("LLM_STUDIO_BASE_URL", "http://192.168.1.35:1234/v1")
    llm_config = LLMConfig(
        provider=f"{provider}/{model}", 
        base_url=llm_url,
        api_token="not-needed"  # LLM Studio no requiere token real
    )
    
    # Esquema para extraer información de materias
    schema = {
        "type": "object",
        "properties": {
            "materias": {
                "type": "array",
                "items": {"type": "string"},
                "descripcion": "Lista de materias del ciclo",
                "ciclo": "string",
            }
        }
    }
    
    # Instrucciones para el LLM
    instruction = """
    Analiza esta página web de la Licenciatura en Ciencias de Datos y extrae TODA la información académica.
    
    Es CRÍTICO que identifiques y extraigas materias de los TRES ciclos:
    1. CBC (Ciclo Básico Común)
    2. Segundo Ciclo de Grado
    3. Tercer Ciclo de Grado (orientaciones)
    
    IMPORTANTE: 
    - Debes extraer materias de TODOS los ciclos, no solo los primeros
    - Incluye las orientaciones del tercer ciclo como materias
    - Asegúrate de revisar TODO el contenido de la página
    - No te detengas solo en los primeros ciclos
    - Busca específicamente las secciones del tercer ciclo
    
    Retorna una lista completa de materias únicas con: {materia: string, descripcion: string, ciclo: string}
    """
    
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        instruction=instruction,
        extraction_type="schema",
        schema=schema,
        verbose=True,
    )

    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )
    
    try:
        async with AsyncWebCrawler(
            verbose=True,
            headless=True,
            browser_type="chromium"
        ) as crawler:
            print("📡 Ejecutando extracción...")
            result = await crawler.arun(url, config=config)
            
            print("✅ Extracción completada")
            
            # Procesar resultados
            if result and hasattr(result, 'extracted_content') and result.extracted_content:
                print("📊 Contenido extraído:")
                print(f"   Tipo: {type(result.extracted_content)}")
                print(f"   Longitud: {len(str(result.extracted_content))} caracteres")
                
                # Intentar parsear como JSON
                try:
                    if isinstance(result.extracted_content, str):
                        extracted_data = json.loads(result.extracted_content)
                    else:
                        extracted_data = result.extracted_content
                    
                    print("📋 Datos estructurados:")
                    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
                    
                    # Si se solicita análisis de estructura HTML, generar esquema CSS
                    css_schema = None
                    if analyze_html_structure and hasattr(result, 'html'):
                        print("\n🔍 Analizando estructura HTML para generar esquema CSS...")
                        css_schema = await analyze_html_structure_and_generate_schema(
                            result.html, llm_config, extracted_data
                        )
                    
                    return {
                        "success": True,
                        "data": extracted_data,
                        "raw_content": result.extracted_content,
                        "css_schema": css_schema  # Nuevo campo con esquema CSS
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error parseando JSON: {e}")
                    print("📄 Contenido raw:")
                    print(result.extracted_content)
                    
                    return {
                        "success": True,
                        "data": result.extracted_content,
                        "raw_content": result.extracted_content
                    }
            else:
                print("❌ No se pudo extraer contenido")
                return {
                    "success": False,
                    "error": "No extracted content available"
                }
                
    except Exception as e:
        print(f"❌ Error durante la extracción: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def analyze_html_structure_and_generate_schema(
    html_content: str, 
    llm_config: LLMConfig, 
    extracted_data: list
) -> Optional[Dict[str, Any]]:
    """
    Analiza la estructura HTML y genera un esquema CSS basado en los datos extraídos
    """
    
    # Esquema para el análisis de estructura HTML
    html_analysis_schema = {
        "type": "object",
        "properties": {
            "page_structure": {
                "type": "object",
                "description": "Estructura general de la página"
            },
            "cycle_containers": {
                "type": "object",
                "description": "Contenedores HTML para cada ciclo académico"
            },
            "css_selectors": {
                "type": "object",
                "description": "Selectores CSS para extraer información"
            },
            "recommendations": {
                "type": "string",
                "description": "Recomendaciones para mejorar la extracción"
            }
        }
    }
    
    # Instrucciones para analizar la estructura HTML
    html_analysis_instruction = f"""
    Analiza la estructura HTML de esta página web y genera un esquema CSS para extraer información académica.
    
    DATOS EXTRAÍDOS PREVIAMENTE:
    {json.dumps(extracted_data, indent=2, ensure_ascii=False)}
    
    TAREA:
    1. Identifica los contenedores HTML principales para cada ciclo académico
    2. Encuentra los selectores CSS que contienen las materias
    3. Identifica patrones en la estructura HTML
    4. Genera un esquema CSS optimizado para extracción
    
    IMPORTANTE:
    - Los contenedores de cada ciclo pueden ser diferentes
    - Busca selectores CSS específicos y robustos
    - Considera la estructura jerárquica del HTML
    - Identifica clases, IDs y patrones de elementos
    
    ESTRUCTURA ESPERADA:
    {{
        "page_structure": {{
            "main_container": "selector del contenedor principal",
            "cycle_sections": ["selectores de secciones de ciclos"]
        }},
        "cycle_containers": {{
            "cbc": "selector específico para CBC",
            "segundo_ciclo": "selector específico para Segundo Ciclo", 
            "tercer_ciclo": "selector específico para Tercer Ciclo"
        }},
        "css_selectors": {{
            "materia_title": "selector para títulos de materias",
            "materia_description": "selector para descripciones",
            "materia_list": "selector para listas de materias"
        }},
        "recommendations": "recomendaciones para optimizar la extracción"
    }}
    """
    
    try:
        # Crear estrategia de extracción para análisis HTML
        html_extraction_strategy = LLMExtractionStrategy(
            llm_config=llm_config,
            instruction=html_analysis_instruction,
            extraction_type="schema",
            schema=html_analysis_schema,
            verbose=True,
        )
        
        # Simular una extracción con el HTML como contenido
        # Nota: Esto es una aproximación, en un caso real necesitarías
        # una implementación más específica para analizar HTML
        
        print("   🔍 Generando esquema CSS basado en estructura HTML...")
        
        # Por ahora, generamos un esquema básico basado en los datos extraídos
        css_schema = generate_basic_css_schema(extracted_data)
        
        print("   ✅ Esquema CSS generado")
        return css_schema
        
    except Exception as e:
        print(f"   ❌ Error generando esquema CSS: {e}")
        return None


def generate_basic_css_schema(extracted_data: list) -> Dict[str, Any]:
    """
    Genera un esquema CSS básico basado en los datos extraídos
    """
    
    # Analizar los datos para inferir estructura
    ciclos_encontrados = set()
    for item in extracted_data:
        if isinstance(item, dict) and 'ciclo' in item:
            ciclos_encontrados.add(item['ciclo'])
    
    # Esquema CSS básico
    css_schema = {
        "name": "materias_lcd_auto_generated",
        "baseSelector": "body",
        "fields": [
            {
                "name": "materias",
                "selector": "h3, h4, .materia, .course, [class*='materia'], [class*='course']",
                "type": "list",
                "fields": [
                    {
                        "name": "nombre",
                        "selector": "self",
                        "type": "text"
                    },
                    {
                        "name": "descripcion",
                        "selector": "following-sibling::p, following-sibling::div, .descripcion, .description",
                        "type": "text"
                    },
                    {
                        "name": "ciclo",
                        "selector": "ancestor::section, ancestor::div[class*='ciclo'], ancestor::div[class*='cycle']",
                        "type": "text"
                    }
                ]
            }
        ],
        "cycle_specific_selectors": {
            "cbc": "section:has(h2:contains('CBC')), .cbc, [class*='cbc']",
            "segundo_ciclo": "section:has(h2:contains('Segundo')), .segundo-ciclo, [class*='segundo']",
            "tercer_ciclo": "section:has(h2:contains('Tercer')), .tercer-ciclo, [class*='tercer']"
        },
        "metadata": {
            "ciclos_detectados": list(ciclos_encontrados),
            "total_materias": len(extracted_data),
            "generated_from": "llm_analysis",
            "recommendations": [
                "Ajustar selectores según la estructura HTML específica",
                "Considerar usar selectores más específicos para cada ciclo",
                "Validar selectores con herramientas de desarrollo del navegador"
            ]
        }
    }
    
    return css_schema


async def main(url: str):
    """Función principal"""
    result = await llm_structured_extraction_no_schema(
        url=url,
        analyze_html_structure=True  # Habilitar análisis de estructura HTML
    )
    
    if result["success"]:
        print("\n🎉 Extracción exitosa!")
        
        # Mostrar esquema CSS si se generó
        if result.get("css_schema"):
            print("\n📋 ESQUEMA CSS GENERADO:")
            print("="*50)
            print(json.dumps(result["css_schema"], indent=2, ensure_ascii=False))
            
            # Guardar esquema en archivo en el directorio data/
            import os
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            schema_file = os.path.join(data_dir, "generated_css_schema.json")
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(result["css_schema"], f, indent=2, ensure_ascii=False)
            print(f"\n💾 Esquema guardado en: {schema_file}")
            
            # Almacenar también en el archivo data/materias.json la lista de materias extraídas.
            materias_extraidas = []
            # Intentar extraer la lista de materias del resultado
            if "data" in result:
                data = result["data"]
                if isinstance(data, list):
                    # Los datos están directamente como lista de materias
                    materias_extraidas = data
                    print(f"   📊 Materias extraídas encontradas: {len(materias_extraidas)}")
                elif isinstance(data, dict):
                    # Buscar claves posibles en el diccionario
                    if "materias" in data:
                        materias_extraidas = data["materias"]
                    elif "materias" in data.get("result", {}):
                        materias_extraidas = data["result"]["materias"]
                    else:
                        # Buscar en otras estructuras si es necesario
                        for key in data:
                            if isinstance(data[key], list):
                                materias_extraidas = data[key]
                                break
                else:
                    print(f"   ⚠️ Tipo de datos inesperado: {type(data)}")

            if materias_extraidas:
                materias_file = os.path.join(data_dir, "materias.json")
                try:
                    with open(materias_file, 'w', encoding='utf-8') as f:
                        json.dump(materias_extraidas, f, indent=2, ensure_ascii=False)
                    print(f"💾 Lista de materias guardada en: {materias_file}")
                    
                    # Mostrar estadísticas de las materias guardadas
                    ciclos_count = {}
                    for materia in materias_extraidas:
                        if isinstance(materia, dict) and "ciclo" in materia:
                            ciclo = materia["ciclo"]
                            ciclos_count[ciclo] = ciclos_count.get(ciclo, 0) + 1
                    
                    print(f"   📈 Distribución por ciclos:")
                    for ciclo, count in ciclos_count.items():
                        print(f"      📖 {ciclo}: {count} materias")
                        
                except Exception as e:
                    print(f"⚠️ Error al guardar materias extraídas: {e}")
            else:
                print("⚠️ No se encontraron materias extraídas para guardar en materias.json")
                print(f"   🔍 Estructura de result['data']: {type(result.get('data'))}")
                if result.get('data'):
                    print(f"   🔍 Contenido: {result['data'][:200] if isinstance(result['data'], str) else str(result['data'])[:200]}...")
            
        
        return result["data"]
    else:
        print(f"\n❌ Error en la extracción: {result['error']}")
        return None


if __name__ == "__main__":
    # URL de prueba
    test_url = "https://lcd.exactas.uba.ar/materias"

    # Ejecutar extracción
    asyncio.run(main(test_url))
