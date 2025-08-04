#!/usr/bin/env python3
"""
Configuración específica para LLM Studio
"""

import os

# Configuración por defecto de LLM Studio
LLM_STUDIO_CONFIG = {
    "base_url": "http://192.168.1.35:1234/v1",
    "model": "gemma3-12b",
    "provider": "openai",  # LLM Studio usa el formato OpenAI
    "api_token": "not-needed"
}

def get_llm_studio_config():
    """
    Obtiene la configuración de LLM Studio desde variables de entorno o usa valores por defecto
    """
    return {
        "base_url": os.getenv("LLM_STUDIO_BASE_URL", LLM_STUDIO_CONFIG["base_url"]),
        "model": os.getenv("LLM_STUDIO_MODEL", LLM_STUDIO_CONFIG["model"]),
        "provider": LLM_STUDIO_CONFIG["provider"],
        "api_token": LLM_STUDIO_CONFIG["api_token"]
    }

def test_llm_studio_connection():
    """
    Prueba la conexión con LLM Studio
    """
    import requests
    
    config = get_llm_studio_config()
    try:
        # Prueba básica de conectividad
        response = requests.get(f"{config['base_url']}/models", timeout=5)
        if response.status_code == 200:
            print(f"✅ Conexión exitosa a LLM Studio en {config['base_url']}")
            return True
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión a LLM Studio: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Configuración de LLM Studio")
    print("="*40)
    
    config = get_llm_studio_config()
    print(f"Base URL: {config['base_url']}")
    print(f"Modelo: {config['model']}")
    print(f"Proveedor: {config['provider']}")
    
    print("\n🧪 Probando conexión...")
    test_llm_studio_connection() 