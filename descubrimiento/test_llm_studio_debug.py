#!/usr/bin/env python3
"""
Script de prueba simplificado para diagnosticar problemas con LLM Studio
"""

import asyncio
import os
import requests
from crawl4ai import AsyncWebCrawler, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_llm_studio_connection():
    """Prueba básica de conexión con LLM Studio"""
    print("🧪 PRUEBA: Conexión básica con LLM Studio")
    print("="*50)
    
    # Verificar configuración
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3")
    
    if not llm_studio_url:
        print("❌ Error: LLM_STUDIO_BASE_URL no configurado en .env")
        return False
    
    print(f"✅ Configuración detectada:")
    print(f"   URL: {llm_studio_url}")
    print(f"   Modelo: {llm_studio_model}")
    
    # Crear configuración LLM
    llm_config = LLMConfig(
        provider=f"openai/{llm_studio_model}",
        base_url=llm_studio_url,
        api_token="not-needed"  # LLM Studio local no requiere token real
    )
    
    print(f"🔧 Configuración LLM creada:")
    print(f"   Provider: {llm_config.provider}")
    print(f"   Base URL: {llm_config.base_url}")
    print(f"   API Token: {llm_config.api_token}")
    
    try:
        async with AsyncWebCrawler(
            verbose=True,  # Habilitar verbose para ver más detalles
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium"
        ) as crawler:
            
            print("\n📡 Probando extracción simple...")
            
            result = await crawler.arun(
                url="https://lcd.exactas.uba.ar/materias",
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=llm_config,
                    extraction_type="llm",
                    instruction="What is this webpage about? Answer in one sentence.",
                    chunk_token_threshold=1000,
                    apply_chunking=False  # Deshabilitar chunking para prueba simple
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
            
            # Verificar si el problema es específico del LLM
            if result and result.success and result.html and not result.extracted_content:
                print(f"\n🔍 DIAGNÓSTICO: El crawler funciona pero el LLM no responde")
                print(f"   - HTML obtenido correctamente")
                print(f"   - LLM Studio no está procesando la solicitud")
                print(f"   - Posibles causas:")
                print(f"     1. LLM Studio no está corriendo en {llm_studio_url}")
                print(f"     2. El modelo {llm_studio_model} no está cargado")
                print(f"     3. Problema de conectividad de red")
                print(f"     4. Configuración incorrecta del endpoint")
                return False
            elif result and result.extracted_content:
                print(f"\n✅ ÉXITO: LLM Studio responde correctamente")
                return True
            else:
                print(f"\n❌ FALLO: Problema general con el crawler o LLM")
                return False
                
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        return False

def test_network_connectivity():
    """Prueba conectividad de red básica"""
    print("\n🌐 PRUEBA: Conectividad de red")
    print("="*50)
    
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    if not llm_studio_url:
        print("❌ LLM_STUDIO_BASE_URL no configurado")
        return False
    
    try:
        # Probar conectividad básica
        response = requests.get(f"{llm_studio_url}/v1/models", timeout=5)
        print(f"✅ Conectividad exitosa: {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}...")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Error de conexión: No se puede conectar a {llm_studio_url}")
        print("   Verifica que LLM Studio esté corriendo")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: La conexión a {llm_studio_url} tardó demasiado")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

async def test_alternative_configs():
    """Prueba configuraciones alternativas"""
    print("\n🔧 PRUEBA: Configuraciones alternativas")
    print("="*50)
    
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3")
    
    # Configuración 1: Sin base_url (usar default)
    print("📋 Configuración 1: Sin base_url")
    try:
        llm_config1 = LLMConfig(
            provider=f"openai/{llm_studio_model}",
            api_token="not-needed"
        )
        print(f"   ✅ Configuración 1 creada: {llm_config1.provider}")
    except Exception as e:
        print(f"   ❌ Error en configuración 1: {e}")
    
    # Configuración 2: Con base_url explícito
    print("📋 Configuración 2: Con base_url explícito")
    try:
        llm_config2 = LLMConfig(
            provider=f"openai/{llm_studio_model}",
            base_url=llm_studio_url,
            api_token="not-needed"
        )
        print(f"   ✅ Configuración 2 creada: {llm_config2.provider} -> {llm_config2.base_url}")
    except Exception as e:
        print(f"   ❌ Error en configuración 2: {e}")
    
    # Configuración 3: Sin api_token
    print("📋 Configuración 3: Sin api_token")
    try:
        llm_config3 = LLMConfig(
            provider=f"openai/{llm_studio_model}",
            base_url=llm_studio_url
        )
        print(f"   ✅ Configuración 3 creada: {llm_config3.provider}")
    except Exception as e:
        print(f"   ❌ Error en configuración 3: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de LLM Studio...")
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("❌ Error: Archivo .env no encontrado")
        print("   Crea un archivo .env con:")
        print("   LLM_STUDIO_BASE_URL=http://192.168.1.35:1234")
        print("   LLM_STUDIO_MODEL=gemma-3")
        exit(1)
    
    # Ejecutar pruebas
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO COMPLETO DE LLM STUDIO")
    print("="*60)
    
    # 1. Prueba de conectividad de red
    network_ok = test_network_connectivity()
    
    # 2. Prueba configuraciones alternativas
    asyncio.run(test_alternative_configs())
    
    # 3. Prueba de conexión LLM (solo si la red funciona)
    if network_ok:
        success = asyncio.run(test_llm_studio_connection())
    else:
        success = False
    
    # Resumen final
    print("\n" + "="*60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("="*60)
    
    if success:
        print("🎉 LLM Studio funciona correctamente!")
    else:
        print("❌ LLM Studio tiene problemas de configuración")
        print("\n🔧 PASOS PARA SOLUCIONAR:")
        print("   1. Verifica que LLM Studio esté corriendo")
        print("   2. Verifica la URL en .env")
        print("   3. Verifica que el modelo esté cargado")
        print("   4. Prueba acceder a la URL desde el navegador")
        print("   5. Verifica que no haya firewall bloqueando el puerto") 