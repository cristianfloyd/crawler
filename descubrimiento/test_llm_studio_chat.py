#!/usr/bin/env python3
"""
Script para probar directamente el endpoint de chat de LLM Studio
"""

import asyncio
import os
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_llm_studio_chat_direct():
    """Prueba directa del endpoint de chat de LLM Studio"""
    print("🧪 PRUEBA: Endpoint de chat directo de LLM Studio")
    print("="*60)
    
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")
    
    if not llm_studio_url:
        print("❌ LLM_STUDIO_BASE_URL no configurado")
        return False
    
    # Payload para la solicitud de chat
    payload = {
        "model": f"google/{llm_studio_model}",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'LLM Studio is working!' if you can see this message."
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Enviando solicitud de chat a: {llm_studio_url}/v1/chat/completions")
        print(f"🔧 Modelo: {payload['model']}")
        print(f"📝 Mensaje: {payload['messages'][0]['content']}")
        
        response = requests.post(
            f"{llm_studio_url}/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Respuesta JSON exitosa:")
                print(f"   Content: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                return True
            except json.JSONDecodeError:
                print(f"   ❌ Error parseando JSON: {response.text}")
                return False
        else:
            print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Error de conexión")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return False

def test_llm_studio_completions():
    """Prueba del endpoint de completions (alternativo)"""
    print("\n🧪 PRUEBA: Endpoint de completions de LLM Studio")
    print("="*60)
    
    llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
    llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")
    
    # Payload para completions
    payload = {
        "model": f"google/{llm_studio_model}",
        "prompt": "Hello! Please respond with 'LLM Studio is working!' if you can see this message.",
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Enviando solicitud de completions a: {llm_studio_url}/v1/completions")
        
        response = requests.post(
            f"{llm_studio_url}/v1/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Respuesta JSON exitosa:")
                print(f"   Content: {result.get('choices', [{}])[0].get('text', 'No content')}")
                return True
            except json.JSONDecodeError:
                print(f"   ❌ Error parseando JSON: {response.text}")
                return False
        else:
            print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_crawl4ai_llm_config():
    """Prueba la configuración específica de Crawl4AI"""
    print("\n🧪 PRUEBA: Configuración Crawl4AI para LLM Studio")
    print("="*60)
    
    try:
        from crawl4ai import LLMConfig
        
        llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
        llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")
        
        # Configuración 1: Con base_url y api_token
        print("📋 Configuración 1: Con base_url y api_token")
        config1 = LLMConfig(
            provider=f"openai/{llm_studio_model}",
            base_url=llm_studio_url,
            api_token="not-needed"
        )
        print(f"   ✅ Creada: {config1.provider} -> {config1.base_url}")
        
        # Configuración 2: Sin api_token
        print("📋 Configuración 2: Sin api_token")
        config2 = LLMConfig(
            provider=f"openai/{llm_studio_model}",
            base_url=llm_studio_url
        )
        print(f"   ✅ Creada: {config2.provider} -> {config2.base_url}")
        
        # Configuración 3: Con modelo específico
        print("📋 Configuración 3: Modelo específico")
        config3 = LLMConfig(
            provider="openai/gemma-3-12b",
            base_url=llm_studio_url,
            api_token="not-needed"
        )
        print(f"   ✅ Creada: {config3.provider} -> {config3.base_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creando configuraciones: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas directas de LLM Studio...")
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("❌ Error: Archivo .env no encontrado")
        exit(1)
    
    print("\n" + "="*70)
    print("🔍 PRUEBAS DIRECTAS DE LLM STUDIO")
    print("="*70)
    
    # 1. Probar configuración Crawl4AI
    config_ok = test_crawl4ai_llm_config()
    
    # 2. Probar endpoint de chat
    chat_ok = test_llm_studio_chat_direct()
    
    # 3. Probar endpoint de completions
    completions_ok = test_llm_studio_completions()
    
    # Resumen
    print("\n" + "="*70)
    print("📋 RESUMEN DE PRUEBAS")
    print("="*70)
    
    print(f"🔧 Configuración Crawl4AI: {'✅' if config_ok else '❌'}")
    print(f"💬 Endpoint Chat: {'✅' if chat_ok else '❌'}")
    print(f"📝 Endpoint Completions: {'✅' if completions_ok else '❌'}")
    
    if chat_ok or completions_ok:
        print("\n🎉 LLM Studio responde correctamente!")
        print("   El problema está en la configuración de Crawl4AI")
    else:
        print("\n❌ LLM Studio no responde a solicitudes de chat")
        print("   Verifica la configuración del modelo en LLM Studio") 