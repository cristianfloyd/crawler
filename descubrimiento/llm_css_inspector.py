#!/usr/bin/env python3
"""
LLM CSS Schema Inspector - Versión Corregida
Clase especializada para usar LLM en análisis de HTML y generación de esquemas CSS optimizados
"""

import json
import asyncio
import os
import requests
from typing import Dict, List, Optional, Tuple
from crawl4ai import AsyncWebCrawler, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class LLMCSSInspector:
    """
    Inspector que usa LLM para analizar HTML y generar esquemas CSS optimizados
    """

    def __init__(self, llm_provider: str = "openai", api_key: Optional[str] = None):
        """
        Inicializa el inspector LLM

        Args:
            llm_provider: Proveedor LLM (openai para LLM Studio, ollama, google, etc.)
            api_key: API key para el proveedor (si None, lee de variables de entorno)
        """
        self.llm_provider = llm_provider
        self.api_key = api_key or self._get_api_key()
        self.analysis_result = None
        self.generated_schema = None

    def _get_api_key(self) -> str:
        """Obtiene API key de variables de entorno (.env)"""
        if self.llm_provider == "ollama":
            # Ollama no requiere API key
            return ""
        elif self.llm_provider == "google":
            key = os.getenv("GOOGLE_API_KEY", "")
        elif self.llm_provider == "openai":
            key = os.getenv("OPENAI_API_KEY", "")
        elif self.llm_provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY", "")
        else:
            key = os.getenv("LLM_API_KEY", "")

        if not key and self.llm_provider != "ollama":
            print(f"⚠️  Advertencia: No se encontró API key para {self.llm_provider}")
            if self.llm_provider == "google":
                print("   Obtén tu API key en: https://aistudio.google.com/app/apikey")
            print(
                "   Asegúrate de que el archivo .env existe y contiene la clave correcta"
            )

        return key  # ✅ CORRECCIÓN: Agregar return key

    def _get_llm_studio_config(self) -> Tuple[str, str]:
        """Obtiene configuración de LLM Studio"""
        llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
        llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")

        if not llm_studio_url:
            raise ValueError("LLM_STUDIO_BASE_URL no configurado en .env")

        return llm_studio_url, llm_studio_model

    def _call_llm_studio_direct(
        self, prompt: str, max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Llama directamente a LLM Studio usando requests

        Args:
            prompt: Prompt para enviar al LLM
            max_tokens: Máximo número de tokens en la respuesta

        Returns:
            Respuesta del LLM o None si falla
        """
        try:
            llm_studio_url, llm_studio_model = self._get_llm_studio_config()

            # Payload para la solicitud de chat
            payload = {
                "model": f"google/{llm_studio_model}",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }

            headers = {"Content-Type": "application/json"}

            print(f"   📡 Enviando solicitud a LLM Studio: {llm_studio_url}")

            response = requests.post(
                f"{llm_studio_url}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                content = (
                    result.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
                print(f"   ✅ LLM Studio respondió correctamente")
                return content
            else:
                print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"   ❌ Error llamando a LLM Studio: {e}")
            return None

    def _get_llm_provider_string(self) -> str:
        """Genera string de proveedor para LLMConfig"""
        if os.getenv("LLM_STUDIO_BASE_URL"):
            # LLM Studio usa API compatible con OpenAI
            model = os.getenv("LLM_STUDIO_MODEL", "gemma-3")
            return f"openai/{model}"
        elif self.llm_provider == "ollama":
            model = os.getenv("OLLAMA_MODEL", "llama3.3")
            return f"ollama/{model}"
        elif self.llm_provider == "google":
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
            return f"google/{model}"
        elif self.llm_provider == "openai":
            return "openai/gpt-4"
        elif self.llm_provider == "anthropic":
            return "anthropic/claude-3-sonnet"
        else:
            return f"{self.llm_provider}/default"

    def _get_llm_config(self) -> LLMConfig:
        """Crea configuración LLM apropiada"""
        config_params = {"provider": self._get_llm_provider_string()}

        # Configurar para LLM Studio local
        llm_studio_base_url = os.getenv("LLM_STUDIO_BASE_URL")
        if llm_studio_base_url is not None:
            # ✅ CORRECCIÓN: Configuración probada que funciona
            config_params["base_url"] = llm_studio_base_url
            # LLM Studio local no requiere api_token real
            config_params["api_token"] = "not-needed"
        # Configurar para Ollama
        elif self.llm_provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            config_params["base_url"] = base_url
            # Ollama no necesita API token
        else:
            # Proveedores externos requieren API token
            config_params["api_token"] = self.api_key

        return LLMConfig(**config_params)

    def _create_analysis_prompt(self, html_content: str) -> str:
        """
        Crea el prompt para que el LLM analice la estructura HTML
        """
        return f"""
        Analiza este HTML de la página de materias de la Licenciatura en Ciencias de Datos y identifica los selectores CSS exactos para extraer:

        HTML a analizar:
        {html_content[:5000]}...

        1. **Secciones principales**: 
           - CBC (Ciclo Básico Común)
           - Segundo Ciclo (materias obligatorias)
           - Tercer Ciclo (electivas y tesis)

        2. **Nombres de materias**: 
           - Elementos que contienen nombres como "Álgebra I", "Algoritmos y Estructuras de Datos I"
           - Probable que estén en H3, H4 o elementos específicos

        3. **Descripciones de materias**:
           - Texto que sigue a cada nombre de materia
           - Información adicional sobre prerrequisitos, contenido

        4. **Información de orientaciones**:
           - Menciones de "640 horas", "electivas", "orientaciones"
           - Listas de caminos como "Data", "Investigación Operativa"

        **IMPORTANTE**: 
        - Proporciona selectores CSS específicos y precisos
        - Indica la jerarquía HTML real que observas
        - Si hay contenido dinámico, mencionalo
        - Sugiere selectores alternativos si los principales fallan

        Responde en formato JSON con esta estructura:
        {{
          "analisis_estructura": "descripción de lo que encontraste",
          "selectores_principales": {{
            "secciones": "selector CSS para secciones",
            "materias": "selector CSS para nombres de materias", 
            "descripciones": "selector CSS para descripciones",
            "orientaciones": "selector CSS para info de orientaciones"
          }},
          "selectores_alternativos": {{
            "materias_alt": "selector alternativo para materias",
            "descripciones_alt": "selector alternativo para descripciones"
          }},
          "estructura_detectada": {{
            "cbc_presente": true/false,
            "segundo_ciclo_presente": true/false,
            "tercer_ciclo_presente": true/false,
            "contenido_dinamico": true/false
          }},
          "recomendaciones": "sugerencias para mejorar extracción"
        }}
        """

    def _create_schema_generation_prompt(self, analysis_data: dict) -> str:
        """
        Crea prompt para generar esquema CSS basado en análisis
        """
        return f"""
        Basándote en este análisis de la estructura HTML:
        {json.dumps(analysis_data, indent=2)}

        Genera un esquema JsonCssExtractionStrategy óptimo para Crawl4AI.

        El esquema debe extraer:
        1. **Encabezados de sección** (H3/H2 que indican CBC, Segundo Ciclo, etc.)
        2. **Materias individuales** (nombres limpios)
        3. **Contenido descriptivo** (información adicional de cada materia)
        4. **Información de orientaciones** (para tercer ciclo)

        Responde SOLO con un JSON válido que siga esta estructura:
        {{
          "name": "materias_lcd_optimizado",
          "baseSelector": "selector_base_detectado",
          "fields": [
            {{
              "name": "secciones",
              "selector": "selector_css_para_secciones",
              "type": "list",
              "fields": [
                {{
                  "name": "titulo",
                  "selector": "self",
                  "type": "text"
                }},
                {{
                  "name": "tag_type",
                  "selector": "self",
                  "type": "attribute",
                  "attribute": "tagName"
                }}
              ]
            }},
            {{
              "name": "materias",
              "selector": "selector_css_para_materias",
              "type": "list",
              "fields": [
                {{
                  "name": "nombre",
                  "selector": "self",
                  "type": "text"
                }},
                {{
                  "name": "siguiente_texto",
                  "selector": "siguiente_elemento_css",
                  "type": "text"
                }}
              ]
            }},
            {{
              "name": "contenido_completo",
              "selector": "body",
              "type": "text"
            }}
          ]
        }}

        **CRÍTICO**: Responde ÚNICAMENTE con JSON válido, sin texto adicional.
        """

    async def analyze_html_structure(self, url: str) -> Tuple[bool, dict]:
        """
        Analiza la estructura HTML usando LLM Studio con requests directos

        Returns:
            Tuple[bool, dict]: (éxito, datos_de_análisis)
        """
        print("🧠 Iniciando análisis LLM de estructura HTML...")

        try:
            # Obtener HTML usando Crawl4AI
            async with AsyncWebCrawler(
                verbose=False,
                headless=True,
                always_by_pass_cache=True,
                browser_type="chromium",
            ) as crawler:

                print("   📄 Obteniendo HTML de la página...")
                result = await crawler.arun(url=url, bypass_cache=True)

                if not result or not result.html:
                    print("   ❌ No se pudo obtener HTML")
                    return False, {"error": "No HTML content"}

                html_content = result.html
                print(f"   ✅ HTML obtenido: {len(html_content)} caracteres")

                # Crear prompt para análisis
                prompt = self._create_analysis_prompt(html_content)

                # Llamar a LLM Studio directamente
                print("   🧠 Enviando HTML al LLM para análisis...")
                llm_response = self._call_llm_studio_direct(prompt, max_tokens=2000)

                if not llm_response:
                    print("   ❌ LLM Studio no respondió")
                    return False, {"error": "No response from LLM Studio"}

                print("   ✅ LLM análisis completado")

                try:
                    # Limpiar respuesta si tiene markdown
                    content = llm_response.strip()
                    if content.startswith("```json"):
                        content = (
                            content.replace("```json", "").replace("```", "").strip()
                        )

                    # ✅ MEJORA: Extraer solo la parte JSON válida
                    # Buscar el primer { y el último } para extraer solo el JSON
                    start_idx = content.find("{")
                    end_idx = content.rfind("}")

                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_content = content[start_idx : end_idx + 1]
                        print(
                            f"   🔧 Extrayendo JSON válido (líneas {start_idx}-{end_idx})"
                        )
                    else:
                        json_content = content

                    analysis_data = json.loads(json_content)
                    self.analysis_result = analysis_data

                    print("   📊 Resultados del análisis:")
                    print(
                        f"      - CBC presente: {analysis_data.get('estructura_detectada', {}).get('cbc_presente', '?')}"
                    )
                    print(
                        f"      - Segundo ciclo: {analysis_data.get('estructura_detectada', {}).get('segundo_ciclo_presente', '?')}"
                    )
                    print(
                        f"      - Tercer ciclo: {analysis_data.get('estructura_detectada', {}).get('tercer_ciclo_presente', '?')}"
                    )
                    print(
                        f"      - Contenido dinámico: {analysis_data.get('estructura_detectada', {}).get('contenido_dinamico', '?')}"
                    )

                    return True, analysis_data

                except json.JSONDecodeError as e:
                    print(f"   ❌ Error parseando respuesta LLM: {e}")
                    print(f"   📄 Contenido recibido: {llm_response[:500]}...")
                    return False, {
                        "error": "JSON parsing failed",
                        "raw_content": llm_response,
                    }

        except Exception as e:
            print(f"   ❌ Error en análisis LLM: {e}")
            return False, {"error": str(e)}

    async def generate_css_schema(self, analysis_data: dict) -> Tuple[bool, dict]:
        """
        Genera esquema CSS optimizado basado en análisis LLM

        Args:
            analysis_data: Datos del análisis previo

        Returns:
            Tuple[bool, dict]: (éxito, esquema_css)
        """
        print("🔧 Generando esquema CSS optimizado...")

        try:
            # Crear prompt para generación de esquema
            prompt = self._create_schema_generation_prompt(analysis_data)

            print("   🎯 Solicitando esquema CSS al LLM...")
            llm_response = self._call_llm_studio_direct(prompt, max_tokens=1500)

            if not llm_response:
                print("   ❌ LLM Studio no devolvió esquema")
                return False, {"error": "No schema from LLM Studio"}

            print("   ✅ Esquema CSS generado")

            try:
                # Limpiar respuesta si tiene markdown
                content = llm_response.strip()
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()

                # ✅ MEJORA: Extraer solo la parte JSON válida
                # Buscar el primer { y el último } para extraer solo el JSON
                start_idx = content.find("{")
                end_idx = content.rfind("}")

                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_content = content[start_idx : end_idx + 1]
                    print(
                        f"   🔧 Extrayendo JSON válido (líneas {start_idx}-{end_idx})"
                    )
                else:
                    json_content = content

                schema_data = json.loads(json_content)
                self.generated_schema = schema_data

                print("   📋 Esquema generado:")
                print(f"      - Nombre: {schema_data.get('name', 'N/A')}")
                print(
                    f"      - Base selector: {schema_data.get('baseSelector', 'N/A')}"
                )
                print(f"      - Campos: {len(schema_data.get('fields', []))}")

                return True, schema_data

            except json.JSONDecodeError as e:
                print(f"   ❌ Error parseando esquema CSS: {e}")
                print(f"   📄 Contenido recibido: {content[:500]}...")
                return False, {
                    "error": "Schema JSON parsing failed",
                    "raw_content": content,
                }

        except Exception as e:
            print(f"   ❌ Error generando esquema CSS: {e}")
            return False, {"error": str(e)}

    async def full_analysis_and_schema_generation(
        self, url: str
    ) -> Tuple[bool, dict, dict]:
        """
        Ejecuta análisis completo: estructura HTML + generación de esquema CSS

        Returns:
            Tuple[bool, dict, dict]: (éxito, análisis, esquema)
        """
        print("🚀 Iniciando análisis completo LLM → CSS Schema")
        print("=" * 60)

        # Paso 1: Analizar estructura HTML
        analysis_success, analysis_data = await self.analyze_html_structure(url)

        if not analysis_success:
            print("❌ Falló análisis de estructura HTML")
            return False, analysis_data, {}

        print("\n🔄 Continuando con generación de esquema...")

        # Paso 2: Generar esquema CSS
        schema_success, schema_data = await self.generate_css_schema(analysis_data)

        if not schema_success:
            print("❌ Falló generación de esquema CSS")
            return False, analysis_data, schema_data

        print("\n✅ Análisis completo exitoso!")
        print("=" * 60)

        return True, analysis_data, schema_data

    def get_fallback_schema(self) -> dict:
        """
        Retorna esquema CSS de fallback si falla la generación por LLM
        """
        return {
            "name": "materias_lcd_fallback",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "todos_los_elementos",
                    "selector": "h1, h2, h3, h4, h5, h6, p, div, li",
                    "type": "list",
                    "fields": [
                        {
                            "name": "tag",
                            "selector": "self",
                            "type": "attribute",
                            "attribute": "tagName",
                        },
                        {"name": "texto", "selector": "self", "type": "text"},
                        {
                            "name": "class",
                            "selector": "self",
                            "type": "attribute",
                            "attribute": "className",
                        },
                    ],
                }
            ],
        }

    async def test_simple_llm_extraction(self, url: str) -> Tuple[bool, str]:
        """
        Prueba simple de LLM para diagnosticar problemas
        """
        print("🧪 Ejecutando prueba simple de LLM...")

        # ✅ DEBUG: Mostrar configuración LLM
        llm_config = self._get_llm_config()
        print("   🔧 Configuración LLM:")
        print(f"      Provider: {llm_config.provider}")
        print(f"      Base URL: {getattr(llm_config, 'base_url', 'No configurado')}")
        print(
            f"      API Token: {'Configurado' if hasattr(llm_config, 'api_token') and llm_config.api_token else 'No configurado'}"
        )

        try:
            async with AsyncWebCrawler(
                verbose=False,
                headless=True,
                always_by_pass_cache=True,
                browser_type="chromium",
            ) as crawler:

                print("   📡 Enviando pregunta simple al LLM...")

                # ✅ CORRECCIÓN: Usar la configuración LLM correcta
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=LLMExtractionStrategy(
                        llm_config=llm_config,  # ✅ Usar configuración correcta
                        extraction_type="llm",
                        instruction="Describe briefly what this webpage is about in one sentence. Just respond with plain text, no JSON.",
                        chunk_token_threshold=2000,
                        apply_chunking=True,
                    ),
                    bypass_cache=True,
                )

                # ✅ DEBUG: Información detallada del resultado
                print(f"   🔍 Debug completo del resultado:")
                print(f"      Success: {result.success if result else 'No result'}")
                print(f"      Has HTML: {bool(result and result.html)}")
                print(f"      Has Markdown: {bool(result and result.markdown)}")
                print(
                    f"      Has Extracted Content: {bool(result and hasattr(result, 'extracted_content') and result.extracted_content)}"
                )
                if result and hasattr(result, "error_message") and result.error_message:
                    print(f"      Error Message: {result.error_message}")

                if result and result.extracted_content:
                    print(
                        f"   ✅ LLM respuesta simple: {result.extracted_content[:200]}..."
                    )
                    return True, result.extracted_content
                else:
                    print(f"   ❌ LLM simple falló")
                    print(
                        f"   🔍 Result success: {result.success if result else 'No result'}"
                    )
                    if result and hasattr(result, "error_message"):
                        print(f"   🔍 Error message: {result.error_message}")
                    return False, "No response from simple LLM test"

        except Exception as e:
            print(f"   ❌ Error en prueba simple: {e}")
            return False, str(e)

    def save_analysis_results(self, output_dir: str = "data"):
        """
        Guarda resultados del análisis en archivos JSON
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.analysis_result:
            analysis_file = os.path.join(output_dir, f"llm_analysis_.json")
            with open(analysis_file, "w", encoding="utf-8") as f:
                json.dump(self.analysis_result, f, ensure_ascii=False, indent=2)
            print(f"💾 Análisis guardado: {analysis_file}")

        if self.generated_schema:
            schema_file = os.path.join(output_dir, f"css_schema.json")
            with open(schema_file, "w", encoding="utf-8") as f:
                json.dump(self.generated_schema, f, ensure_ascii=False, indent=2)
            print(f"💾 Esquema guardado: {schema_file}")


# Función de prueba
async def test_llm_inspector():
    """
    Función de prueba para el LLM CSS Inspector con LLM Studio local
    """
    print("🧪 PRUEBA: LLM CSS Inspector (LLM Studio + Requests Directos)")
    print("=" * 65)

    # Verificar que .env existe
    if not os.path.exists(".env"):
        print("❌ Error: Archivo .env no encontrado")
        print("   Crea un archivo .env con configuración de LLM Studio")
        return

    # Verificar configuración LLM Studio
    try:
        llm_studio_url = os.getenv("LLM_STUDIO_BASE_URL")
        llm_studio_model = os.getenv("LLM_STUDIO_MODEL", "gemma-3-12b")

        print(f"✅ Configuración LLM Studio:")
        print(f"   URL: {llm_studio_url}")
        print(f"   Modelo: {llm_studio_model}")

        # Crear inspector con LLM Studio
        inspector = LLMCSSInspector(llm_provider="openai", api_key=None)

        # Ejecutar análisis completo
        print("\n🔧 Ejecutando análisis completo...")
        success, analysis, schema = await inspector.full_analysis_and_schema_generation(
            "https://lcd.exactas.uba.ar/materias"
        )

        if success:
            print("\n🎉 Prueba exitosa con LLM Studio + Requests Directos!")

            # Mostrar resumen del análisis
            if analysis and "estructura_detectada" in analysis:
                est = analysis["estructura_detectada"]
                print(f"\n📊 Estructura detectada:")
                print(f"   CBC: {'✅' if est.get('cbc_presente') else '❌'}")
                print(
                    f"   Segundo Ciclo: {'✅' if est.get('segundo_ciclo_presente') else '❌'}"
                )
                print(
                    f"   Tercer Ciclo: {'✅' if est.get('tercer_ciclo_presente') else '❌'}"
                )
                print(
                    f"   Contenido dinámico: {'⚠️' if est.get('contenido_dinamico') else '✅'}"
                )

            # Mostrar info del esquema
            if schema:
                print(f"\n🔧 Esquema CSS generado:")
                print(f"   Nombre: {schema.get('name', 'N/A')}")
                print(f"   Selector base: {schema.get('baseSelector', 'N/A')}")
                print(f"   Campos: {len(schema.get('fields', []))}")

            inspector.save_analysis_results()
        else:
            print("\n❌ Análisis completo falló")
            print(f"Análisis: {analysis}")
            print(f"Esquema: {schema}")

    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando prueba del LLM CSS Inspector con LLM Studio...")
    print("📁 Verificando configuración...")
    asyncio.run(test_llm_inspector())
