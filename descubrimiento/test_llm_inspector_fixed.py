#!/usr/bin/env python3
"""
Script de prueba final con configuración corregida de LLM Studio
"""

import asyncio
import os
from crawl4ai import AsyncWebCrawler, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_llm_inspector_fixed():
    """Prueba el LLM Inspector con configuración corregida"""
    print("🧪 PRUEBA: LLM Inspector con configuración corregida")
    print("="*60)
    
    # Verificar configuración
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")
    
    if not llm_studio_url:
        print("❌ LLM_STUDIO_BASE_URL no configurado")
        return False
    
    print(f"✅ Configuración detectada:")
    print(f"   URL: {llm_studio_url}")
    print(f"   Modelo: {llm_studio_model}")
    
    # ✅ CONFIGURACIÓN CORREGIDA: Usar la que funciona
    llm_config = LLMConfig(
        provider=f"openai/{llm_studio_model}",
        base_url=llm_studio_url,
        api_token="not-needed"
    )
    
    print(f"🔧 Configuración LLM creada:")
    print(f"   Provider: {llm_config.provider}")
    print(f"   Base URL: {llm_config.base_url}")
    print(f"   API Token: {llm_config.api_token}")
    
    try:
        async with AsyncWebCrawler(
            verbose=True,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium"
        ) as crawler:
            
            print("\n📡 Probando extracción con LLM Studio...")
            
            result = await crawler.arun(
                url="https://lcd.exactas.uba.ar/materias",
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=llm_config,
                    extraction_type="llm",
                    instruction="What is this webpage about? Answer in one sentence.",
                    chunk_token_threshold=1000,
                    apply_chunking=False
                ),
                bypass_cache=True
            )
            
            print(f"\n📊 Resultado de la prueba:")
            print(f"   Success: {result.success if result else 'No result'}")
            print(f"   Has HTML: {bool(result and result.html)}")
            print(f"   HTML Length: {len(result.html) if result and result.html else 0}")
            print(f"   Has Markdown: {bool(result and result.markdown)}")
            print(f"   Markdown Length: {len(result.markdown) if result and result.markdown else 0}")
            print(f"   Has Extracted Content: {bool(result and hasattr(result, 'extracted_content') and result.extracted_content)}")
            
            if result and hasattr(result, 'extracted_content'):
                print(f"   Extracted Content: '{result.extracted_content}'")
            else:
                print(f"   Extracted Content: None")
            
            if result and hasattr(result, 'error_message') and result.error_message:
                print(f"   Error Message: {result.error_message}")
            
            # Verificar resultado
            if result and result.extracted_content:
                print(f"\n🎉 ÉXITO: LLM Studio responde correctamente!")
                print(f"   Contenido extraído: {result.extracted_content[:200]}...")
                return True
            else:
                print(f"\n❌ FALLO: LLM Studio no responde")
                return False
                
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        return False

async def test_schema_extraction():
    """Prueba extracción con esquema JSON"""
    print("\n🧪 PRUEBA: Extracción con esquema JSON")
    print("="*60)
    
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")
    
    # Configuración LLM
    llm_config = LLMConfig(
        provider=f"openai/{llm_studio_model}",
        base_url=llm_studio_url,
        api_token="not-needed"
    )
    
    # Esquema simple para prueba
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"}
        }
    }
    
    try:
        async with AsyncWebCrawler(
            verbose=True,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium"
        ) as crawler:
            
            print("📡 Probando extracción con esquema...")
            
            result = await crawler.arun(
                url="https://lcd.exactas.uba.ar/materias",
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=llm_config,
                    schema=schema,
                    extraction_type="schema",
                    instruction="Extract the title and description of this webpage."
                ),
                bypass_cache=True
            )
            
            print(f"\n📊 Resultado del esquema:")
            print(f"   Success: {result.success if result else 'No result'}")
            print(f"   Has Extracted Content: {bool(result and hasattr(result, 'extracted_content') and result.extracted_content)}")
            
            if result and hasattr(result, 'extracted_content'):
                print(f"   Extracted Content: '{result.extracted_content}'")
                return True
            else:
                print(f"   Extracted Content: None")
                return False
                
    except Exception as e:
        print(f"\n❌ Error en esquema: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba final con configuración corregida...")
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("❌ Error: Archivo .env no encontrado")
        exit(1)
    
    print("\n" + "="*70)
    print("🔍 PRUEBA FINAL CON CONFIGURACIÓN CORREGIDA")
    print("="*70)
    
    # Ejecutar pruebas
    success1 = asyncio.run(test_llm_inspector_fixed())
    success2 = asyncio.run(test_schema_extraction())
    
    # Resumen final
    print("\n" + "="*70)
    print("📋 RESUMEN FINAL")
    print("="*70)
    
    print(f"💬 Extracción LLM simple: {'✅' if success1 else '❌'}")
    print(f"📋 Extracción con esquema: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print("\n🎉 ¡ÉXITO TOTAL! LLM Studio funciona correctamente con Crawl4AI")
        print("   El script llm_css_inspector.py ahora debería funcionar")
    elif success1:
        print("\n⚠️  Parcial: LLM simple funciona, esquema puede tener problemas")
    else:
        print("\n❌ FALLO: Problema persistente con Crawl4AI y LLM Studio") 