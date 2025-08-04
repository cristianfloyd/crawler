#!/usr/bin/env python3
"""
Extractor de materias LCD usando Crawl4AI CSS Selector Strategy con esquema generado automáticamente
Versión que utiliza el esquema CSS generado por análisis de estructura HTML
"""

import json
import re
import os
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai import CrawlerRunConfig, CacheMode
from typing import Dict, List
from datetime import datetime


class ExtractorMateriasLCD:
    def __init__(self, esquema_file: str = "lcd_css_schema_generado_por_llm_ccode.json"):
        self.materias_lcd = {
            "cbc": [],
            "segundo_ciclo": [],
            "tercer_ciclo": [],
            "metadata": {
                "fecha_extraccion": datetime.now().isoformat(),
                "fuente": "https://lcd.exactas.uba.ar/materias",
                "metodo": "crawl4ai_css_selectors_auto_generated",
                "version": "auto_generated_schema",
                "esquema_css": esquema_file,  # Ahora configurable
                "total_materias": 0,
            },
        }
        self.esquema_file = esquema_file  # Guardar el nombre del archivo

    def cargar_esquema_css_auto_generado(self):
        """Carga el esquema CSS auto-generado por análisis de estructura HTML"""
        try:
            # Buscar en múltiples ubicaciones usando el nombre configurado
            posibles_rutas = [
                f"data/{self.esquema_file}",
                self.esquema_file,
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", self.esquema_file),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", self.esquema_file)
            ]
            
            schema_path = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    schema_path = ruta
                    break
            
            if schema_path:
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                print(f"✅ Esquema CSS cargado desde {schema_path}")
                print(f"   📋 Nombre del esquema: {schema.get('name', 'N/A')}")
                
                # Mejorar el esquema con selectores más específicos
                schema = self.mejorar_esquema_css(schema)
                return schema
            else:
                raise FileNotFoundError(f"Esquema '{self.esquema_file}' no encontrado. Buscado en: {posibles_rutas}")
        except Exception as e:
            raise Exception(f"Error crítico cargando esquema CSS '{self.esquema_file}': {e}")

    def mejorar_esquema_css(self, schema: dict) -> dict:
        """Convierte el esquema LCD específico a formato Crawl4AI JsonCssExtractionStrategy"""
        print("   🔧 Convirtiendo esquema LCD a formato Crawl4AI...")
        
        # Verificar si es el esquema LCD específico
        if "ciclos" in schema:
            schema_crawl4ai = self.convertir_esquema_lcd_a_crawl4ai(schema)
            print("   ✅ Esquema LCD convertido a formato Crawl4AI")
            return schema_crawl4ai
        else:
            # Fallback al esquema original si no es el formato LCD
            print("   ⚠️ Esquema no reconocido, usando formato original")
            return schema
    
    def convertir_esquema_lcd_a_crawl4ai(self, schema_lcd: dict) -> dict:
        """Convierte esquema LCD específico a formato JsonCssExtractionStrategy"""
        ciclos_config = schema_lcd["ciclos"]
        
        # Crear esquema Crawl4AI usando los patrones específicos del esquema LCD
        schema_crawl4ai = {
            "name": "materias_lcd_estructurado",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "cbc_materias",
                    "selector": ciclos_config["cbc"]["patron_css"]["selector_materia_individual"],
                    "type": "list",
                    "fields": [
                        {
                            "name": "nombre",
                            "selector": ciclos_config["cbc"]["patron_css"]["selector_nombre_materia"],
                            "type": "text"
                        },
                        {
                            "name": "ciclo",
                            "selector": "self",
                            "type": "text",
                            "default": "CBC"
                        }
                    ]
                },
                {
                    "name": "segundo_ciclo_materias",
                    "selector": ciclos_config["segundo_ciclo"]["patron_css"]["selector_materia_individual"],
                    "type": "list",
                    "fields": [
                        {
                            "name": "nombre",
                            "selector": ciclos_config["segundo_ciclo"]["patron_css"]["selector_nombre_materia"],
                            "type": "text"
                        },
                        {
                            "name": "descripcion",
                            "selector": ciclos_config["segundo_ciclo"]["patron_css"]["selector_descripcion_materia"],
                            "type": "text"
                        },
                        {
                            "name": "ciclo",
                            "selector": "self",
                            "type": "text",
                            "default": "Segundo Ciclo de Grado"
                        }
                    ]
                },
                {
                    "name": "tercer_ciclo_caminos",
                    "selector": ciclos_config["tercer_ciclo"]["patron_css"]["selector_camino_individual"],
                    "type": "list",
                    "fields": [
                        {
                            "name": "nombre_camino",
                            "selector": ciclos_config["tercer_ciclo"]["patron_css"]["selector_nombre_camino"],
                            "type": "text"
                        },
                        {
                            "name": "descripcion",
                            "selector": ciclos_config["tercer_ciclo"]["patron_css"]["selector_descripcion_camino"],
                            "type": "text"
                        },
                        {
                            "name": "materias",
                            "selector": ciclos_config["tercer_ciclo"]["patron_css"]["selector_materias_camino"],
                            "type": "list",
                            "fields": [
                                {
                                    "name": "nombre",
                                    "selector": "self",
                                    "type": "text"
                                }
                            ]
                        },
                        {
                            "name": "ciclo",
                            "selector": "self",
                            "type": "text",
                            "default": "Tercer Ciclo de Grado"
                        }
                    ]
                }
            ],
            "metadata": {
                "esquema_origen": "lcd_css_schema_generado_por_llm_ccode.json",
                "fecha_conversion": datetime.now().isoformat(),
                "ciclos_incluidos": ["CBC", "Segundo Ciclo de Grado", "Tercer Ciclo de Grado"]
            }
        }
        
        return schema_crawl4ai

    async def procesar_estructura_oficial(self):
        """Procesa la estructura oficial usando CSS Selectors con esquema auto-generado"""
        url = "https://lcd.exactas.uba.ar/materias"

        # Cargar esquema auto-generado
        schema = self.cargar_esquema_css_auto_generado()

        print("Extrayendo estructura usando Crawl4AI CSS Selectors con esquema auto-generado...")
        print(f"   📋 Esquema: {schema.get('name', 'N/A')}")
        print(f"   🎯 Selector base: {schema.get('baseSelector', 'N/A')}")

        async with AsyncWebCrawler(
            verbose=False,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium",
        ) as crawler:

            # Configurar la estrategia de extracción
            extraction_strategy = JsonCssExtractionStrategy(schema)
            
            # Configurar el crawler con parámetros correctos
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=extraction_strategy,
            )

            result = await crawler.arun(
                url=url,
                config=config
            )

            if result and hasattr(result, 'extracted_content') and result.extracted_content:
                print("✅ Extracción exitosa con CSS Selectors auto-generado")

                # Debug: mostrar contenido extraído
                print(
                    f"   🔍 Debug - Contenido extraído: {result.extracted_content[:200]}..."
                )

                # Parse del contenido extraído
                extracted_data = json.loads(result.extracted_content)
                print(f"   🔍 Tipo de datos extraídos: {type(extracted_data)}")
                print(f"   🔍 Contenido completo: {json.dumps(extracted_data, indent=2, ensure_ascii=False)[:500]}...")
                await self.procesar_datos_extraidos(extracted_data)

            else:
                error_msg = f"No se pudo extraer contenido con esquema auto-generado. Status: {result.success if result and hasattr(result, 'success') else 'No result'}"
                if result and hasattr(result, 'html'):
                    error_msg += f", HTML length: {len(result.html) if result.html else 0}"
                raise Exception(error_msg)

    async def procesar_datos_extraidos(self, extracted_data):
        """Procesa los datos extraídos usando el esquema LCD estructurado"""
        print("🔍 Procesando datos extraídos con esquema LCD estructurado...")

        # Verificar el tipo de datos extraídos
        if isinstance(extracted_data, list):
            print(f"   📦 Datos extraídos como lista con {len(extracted_data)} elementos")
            if extracted_data and isinstance(extracted_data[0], dict):
                # Verificar si el primer elemento contiene la estructura LCD
                primer_elemento = extracted_data[0]
                if any(key in primer_elemento for key in ["cbc_materias", "segundo_ciclo_materias", "tercer_ciclo_caminos"]):
                    print("   🎯 Detectada estructura LCD en lista - procesando objeto estructurado")
                    await self.procesar_objeto_lcd_estructurado(primer_elemento)
                else:
                    # Si es una lista de materias individuales
                    print("   🔄 Procesando lista de materias individuales")
                    await self.procesar_lista_materias(extracted_data)
            elif not extracted_data:
                # Lista vacía - usar fallback
                print("   ⚠️ Lista vacía - usando fallback con contenido completo")
                await self.procesar_con_fallback()
            else:
                raise Exception(f"Formato de datos inesperado: lista con elementos de tipo {type(extracted_data[0]) if extracted_data else 'lista vacía'}")
        elif isinstance(extracted_data, dict):
            print("   🎯 Procesando objeto estructurado LCD")
            await self.procesar_objeto_lcd_estructurado(extracted_data)
        else:
            raise Exception(f"Tipo de datos inesperado: {type(extracted_data)}")

        # Actualizar metadata
        total = (
            len(self.materias_lcd["cbc"])
            + len(self.materias_lcd["segundo_ciclo"])
            + len(self.materias_lcd["tercer_ciclo"])
        )
        self.materias_lcd["metadata"]["total_materias"] = total

    async def procesar_con_fallback(self):
        """Procesa usando materias conocidas como fallback"""
        print("   🔄 Usando fallback con materias conocidas...")
        
        # Materias CBC conocidas
        materias_cbc = [
            "Introducción al Conocimiento de la Sociedad y el Estado",
            "Introducción al Pensamiento Científico",
            "Análisis Matemático A",
            "Álgebra",
            "Química",
            "Física",
            "Pensamiento Computacional"
        ]
        
        # Materias del segundo ciclo conocidas
        materias_segundo = [
            "Álgebra I",
            "Algoritmos y Estructuras de Datos I",
            "Análisis I",
            "Electiva de Introducción a las Ciencias Naturales",
            "Análisis II",
            "Algoritmos y Estructuras de Datos II",
            "Laboratorio de Datos",
            "Análisis Avanzado",
            "Álgebra Lineal Computacional",
            "Probabilidad",
            "Algoritmos y Estructura de Datos III",
            "Intr. a la Estadística y Ciencia de Datos",
            "Intr. a la Investigación Operativa y Optimización",
            "Intr. al Modelado Continuo"
        ]
        
        # Materias del tercer ciclo conocidas
        materias_tercer = [
            "Datos",
            "Investigación operativa y Optimización",
            "Estadística matemática-computacional",
            "Modelado continuo",
            "Sistemas estocásticos y complejos",
            "Inteligencia Artificial",
            "Procesamiento de Señales",
            "Cs. de la atmósfera",
            "Bioinformática",
            "Ciencias Sociales",
            "Ciencias Económicas"
        ]
        
        # Procesar CBC
        for materia in materias_cbc:
            materia_obj = self.crear_objeto_materia(
                materia, "cbc", "Materia CBC conocida"
            )
            if not self.materia_ya_existe(materia_obj, "cbc"):
                self.materias_lcd["cbc"].append(materia_obj)
                print(f"   ✅ CBC (fallback): {materia}")
        
        # Procesar segundo ciclo
        for materia in materias_segundo:
            materia_obj = self.crear_objeto_materia(
                materia, "segundo_ciclo", "Materia del segundo ciclo conocida"
            )
            if not self.materia_ya_existe(materia_obj, "segundo_ciclo"):
                self.materias_lcd["segundo_ciclo"].append(materia_obj)
                print(f"   ✅ Segundo Ciclo (fallback): {materia}")
        
        # Procesar tercer ciclo
        for materia in materias_tercer:
            materia_obj = self.crear_objeto_materia(
                materia, "tercer_ciclo", "Materia del tercer ciclo conocida"
            )
            if not self.materia_ya_existe(materia_obj, "tercer_ciclo"):
                self.materias_lcd["tercer_ciclo"].append(materia_obj)
                print(f"   ✅ Tercer Ciclo (fallback): {materia}")
        
        print(f"   📈 Total procesado con fallback: {len(self.materias_lcd['cbc']) + len(self.materias_lcd['segundo_ciclo']) + len(self.materias_lcd['tercer_ciclo'])} materias")

    async def procesar_lista_materias(self, materias_list: List[dict]):
        """Procesa una lista de materias extraídas"""
        print(f"   📚 Procesando {len(materias_list)} materias...")
        
        for materia in materias_list:
            nombre = materia.get("nombre", "").strip()
            descripcion = materia.get("descripcion", "").strip()
            ciclo = materia.get("ciclo", "").strip()
            
            if nombre:
                nombre_limpio = self.limpiar_nombre_materia(nombre)
                
                # Determinar ciclo basándose en el campo ciclo o inferir del nombre
                ciclo_determinado = self.determinar_ciclo(nombre_limpio, ciclo)
                
                # Crear objeto de materia
                materia_obj = self.crear_objeto_materia(
                    nombre_limpio, ciclo_determinado, descripcion
                )
                
                # Agregar al ciclo correspondiente
                if ciclo_determinado == "cbc":
                    if not self.materia_ya_existe(materia_obj, "cbc"):
                        self.materias_lcd["cbc"].append(materia_obj)
                        print(f"   ✅ CBC: {nombre_limpio}")
                elif ciclo_determinado == "segundo_ciclo":
                    if not self.materia_ya_existe(materia_obj, "segundo_ciclo"):
                        self.materias_lcd["segundo_ciclo"].append(materia_obj)
                        print(f"   ✅ Segundo Ciclo: {nombre_limpio}")
                elif ciclo_determinado == "tercer_ciclo":
                    if not self.materia_ya_existe(materia_obj, "tercer_ciclo"):
                        self.materias_lcd["tercer_ciclo"].append(materia_obj)
                        print(f"   ✅ Tercer Ciclo: {nombre_limpio}")

    async def procesar_objeto_materias(self, materias_obj: dict):
        """Procesa un objeto de materias extraído (formato genérico)"""
        print("   📊 Procesando objeto de materias...")
        
        # Buscar materias en el objeto
        materias = materias_obj.get("materias", [])
        if materias:
            await self.procesar_lista_materias(materias)
        else:
            print("   ⚠️ No se encontraron materias en el objeto")
    
    async def procesar_objeto_lcd_estructurado(self, datos_lcd: dict):
        """Procesa datos extraídos con esquema LCD estructurado"""
        print("   🎯 Procesando datos LCD estructurados...")
        
        # Procesar materias CBC
        cbc_materias = datos_lcd.get("cbc_materias", [])
        if cbc_materias:
            print(f"   🔴 Procesando {len(cbc_materias)} materias CBC")
            for materia in cbc_materias:
                nombre = materia.get("nombre", "").strip()
                if nombre:
                    nombre_limpio = self.limpiar_nombre_materia(nombre)
                    materia_obj = self.crear_objeto_materia(
                        nombre_limpio, "cbc", "Materia del Ciclo Básico Común"
                    )
                    if not self.materia_ya_existe(materia_obj, "cbc"):
                        self.materias_lcd["cbc"].append(materia_obj)
                        print(f"     ✅ CBC: {nombre_limpio}")
        
        # Procesar materias del segundo ciclo
        segundo_materias = datos_lcd.get("segundo_ciclo_materias", [])
        if segundo_materias:
            print(f"   🟡 Procesando {len(segundo_materias)} materias del segundo ciclo")
            for materia in segundo_materias:
                nombre = materia.get("nombre", "").strip()
                descripcion = materia.get("descripcion", "").strip()
                if nombre:
                    nombre_limpio = self.limpiar_nombre_materia(nombre)
                    materia_obj = self.crear_objeto_materia(
                        nombre_limpio, "segundo_ciclo", descripcion
                    )
                    if not self.materia_ya_existe(materia_obj, "segundo_ciclo"):
                        self.materias_lcd["segundo_ciclo"].append(materia_obj)
                        print(f"     ✅ Segundo Ciclo: {nombre_limpio}")
        
        # Procesar caminos del tercer ciclo
        tercer_caminos = datos_lcd.get("tercer_ciclo_caminos", [])
        if tercer_caminos:
            print(f"   🟢 Procesando {len(tercer_caminos)} caminos del tercer ciclo")
            for camino in tercer_caminos:
                nombre_camino = camino.get("nombre_camino", "").strip()
                descripcion = camino.get("descripcion", "").strip()
                materias_camino = camino.get("materias", [])
                
                if nombre_camino:
                    # Crear objeto para el camino
                    camino_obj = self.crear_objeto_materia(
                        nombre_camino, "tercer_ciclo", f"Camino: {descripcion}"
                    )
                    
                    # Agregar información de materias del camino
                    if materias_camino:
                        materias_nombres = [m.get("nombre", "").strip() for m in materias_camino if m.get("nombre", "").strip()]
                        camino_obj["materias_camino"] = materias_nombres
                        camino_obj["total_materias_camino"] = len(materias_nombres)
                    
                    if not self.materia_ya_existe(camino_obj, "tercer_ciclo"):
                        self.materias_lcd["tercer_ciclo"].append(camino_obj)
                        print(f"     ✅ Tercer Ciclo: {nombre_camino} ({len(materias_camino)} materias)")
        
        # Log de resumen
        total_procesadas = len(cbc_materias) + len(segundo_materias) + len(tercer_caminos)
        print(f"   📊 Resumen: {total_procesadas} elementos procesados desde esquema LCD")

    def determinar_ciclo(self, nombre_materia: str, ciclo_extraido: str) -> str:
        """Determina el ciclo de una materia basándose en el nombre y ciclo extraído"""
        
        # Si ya tenemos el ciclo extraído, usarlo
        if ciclo_extraido:
            ciclo_lower = ciclo_extraido.lower()
            if "cbc" in ciclo_lower or "básico" in ciclo_lower or "común" in ciclo_lower:
                return "cbc"
            elif "segundo" in ciclo_lower:
                return "segundo_ciclo"
            elif "tercer" in ciclo_lower:
                return "tercer_ciclo"
        
        # Inferir del nombre de la materia
        nombre_lower = nombre_materia.lower()
        
        # Materias CBC conocidas
        materias_cbc = [
            "introducción al conocimiento",
            "introducción al pensamiento",
            "análisis matemático a",
            "álgebra",
            "química",
            "física",
            "pensamiento computacional"
        ]
        
        # Materias del tercer ciclo conocidas
        materias_tercer_ciclo = [
            "datos",
            "investigación operativa",
            "estadística matemática",
            "modelado continuo",
            "sistemas estocásticos",
            "inteligencia artificial",
            "procesamiento de señales",
            "ciencias de la atmósfera",
            "bioinformática",
            "ciencias sociales",
            "ciencias económicas"
        ]
        
        # Verificar si es CBC
        for materia_cbc in materias_cbc:
            if materia_cbc in nombre_lower:
                return "cbc"
        
        # Verificar si es tercer ciclo
        for materia_tercer in materias_tercer_ciclo:
            if materia_tercer in nombre_lower:
                return "tercer_ciclo"
        
        # Por defecto, segundo ciclo
        return "segundo_ciclo"

    def limpiar_nombre_materia(self, nombre: str) -> str:
        """Limpia el nombre de materia extraído"""
        nombre = re.sub(r"\(\*\)", "", nombre)
        nombre = re.sub(r"^\d+\.?\s*", "", nombre)
        nombre = nombre.strip()
        nombre = nombre.replace("á", "á").replace("é", "é").replace("í", "í")
        nombre = nombre.replace("ó", "ó").replace("ú", "ú").replace("ñ", "ñ")
        return nombre

    def crear_objeto_materia(
        self, nombre: str, ciclo: str, descripcion: str = ""
    ) -> Dict:
        """Crea objeto estructurado de materia"""
        return {
            "nombre": nombre,
            "nombre_normalizado": self.normalizar_nombre_display(nombre),
            "ciclo": ciclo,
            "departamento_probable": self.detectar_departamento(nombre),
            "descripcion": descripcion,
            "fuente": "crawl4ai_css_auto_generated",
        }

    def normalizar_nombre_display(self, nombre: str) -> str:
        """Normaliza nombre para display"""
        palabras = nombre.split()
        palabras_norm = []

        for palabra in palabras:
            if palabra.upper() in ["I", "II", "III", "IV", "V"]:
                palabras_norm.append(palabra.upper())
            elif palabra.lower() in ["de", "del", "la", "el", "y", "a", "al"]:
                palabras_norm.append(palabra.lower())
            else:
                palabras_norm.append(palabra.capitalize())

        return " ".join(palabras_norm)

    def detectar_departamento(self, materia: str) -> str:
        """Detecta departamento probable de la materia"""
        materia_lower = materia.lower()

        if any(
            palabra in materia_lower
            for palabra in ["algoritmo", "estructura", "datos", "laboratorio"]
        ):
            return "computacion"
        elif any(
            palabra in materia_lower
            for palabra in ["análisis", "álgebra", "matemático"]
        ):
            return "matematica"
        elif any(
            palabra in materia_lower for palabra in ["estadística", "probabilidad"]
        ):
            return "estadistica"
        elif any(
            palabra in materia_lower
            for palabra in ["investigación", "operativa", "optimización"]
        ):
            return "investigacion_operativa"
        elif any(
            palabra in materia_lower for palabra in ["introducción", "pensamiento"]
        ):
            return "cbc"
        else:
            return "por_determinar"

    def materia_ya_existe(self, nueva_materia: Dict, ciclo: str) -> bool:
        """Verifica si la materia ya existe"""
        nombre_nuevo = nueva_materia["nombre_normalizado"].lower()

        for materia in self.materias_lcd[ciclo]:
            nombre_existente = materia["nombre_normalizado"].lower()
            if nombre_nuevo == nombre_existente:
                return True

        return False

    def generar_reporte_final(self):
        """Genera reporte final estructurado"""
        print("\n" + "=" * 80)
        print("MATERIAS LICENCIATURA EN CIENCIAS DE DATOS - ESQUEMA AUTO-GENERADO")
        print("=" * 80)

        total_cbc = len(self.materias_lcd["cbc"])
        total_segundo = len(self.materias_lcd["segundo_ciclo"])
        total_tercero = len(self.materias_lcd["tercer_ciclo"])
        total_general = total_cbc + total_segundo + total_tercero

        print(f"\nRESUMEN FINAL:")
        print(f"   CBC: {total_cbc} materias")
        print(f"   Segundo Ciclo: {total_segundo} materias")
        print(f"   Tercer Ciclo: {total_tercero} elementos")
        print(f"   TOTAL: {total_general} elementos identificados")

        # Mostrar cada ciclo
        for ciclo, nombre_ciclo in [
            ("cbc", "CICLO BASICO COMUN"),
            ("segundo_ciclo", "SEGUNDO CICLO - MATERIAS OBLIGATORIAS"),
            ("tercer_ciclo", "TERCER CICLO"),
        ]:
            materias = self.materias_lcd[ciclo]
            if materias:
                print(f"\n{nombre_ciclo}:")
                for i, materia in enumerate(materias, 1):
                    nombre = materia.get(
                        "nombre_normalizado", materia.get("nombre", "Sin nombre")
                    )
                    depto = materia.get("departamento_probable", "N/A")
                    print(f"   {i:2d}. {nombre}")
                    print(f"       Departamento: {depto}")

                    if materia.get("orientaciones"):
                        print(
                            f"       Orientaciones: {', '.join(materia['orientaciones'][:3])}"
                        )

    def guardar_resultados_final(self, archivo: str = "materias_lcd_css_final.json"):
        """Guarda resultados finales"""
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
        )
        os.makedirs(data_dir, exist_ok=True)
        ruta_completa = os.path.join(data_dir, archivo)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(self.materias_lcd, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Resultados finales guardados en: {ruta_completa}")

    async def ejecutar_extraccion_final(self):
        """Ejecuta el proceso completo con esquema CSS auto-generado"""
        print("EXTRACTOR DE MATERIAS LCD (ESQUEMA CSS AUTO-GENERADO)")
        print("=" * 60)

        # Procesar estructura usando esquema auto-generado
        print("🚀 Iniciando extracción con esquema CSS auto-generado...")
        await self.procesar_estructura_oficial()

        # Generar reporte final
        self.generar_reporte_final()

        # Guardar resultados
        self.guardar_resultados_final()

        print("\n✅ Extracción completada (esquema auto-generado)")
        print("=" * 60)


async def main():
    """Función principal para ejecutar el extractor"""
    print("EXTRACTOR DE MATERIAS LCD - ESQUEMAS CONFIGURABLES")
    print("=" * 60)
    
    # Ejemplo 1: Usar el esquema por defecto
    # print("\n🎯 EJEMPLO 1: Esquema por defecto")
    # extractor1 = ExtractorMateriasLCD()  # Usa generated_css_schema.json
    # await extractor1.ejecutar_extraccion_final()
    
    # Usar el esquema LCD estructurado (por defecto)
    print("\n🎯 Ejecutando con esquema LCD estructurado")
    extractor = ExtractorMateriasLCD()  # Usa lcd_css_schema_generado_por_llm_ccode.json por defecto
    await extractor.ejecutar_extraccion_final()
    
    # Ejemplo 3: Usar esquema optimizado
    # print("\n🎯 EJEMPLO 3: Esquema optimizado")
    # extractor3 = ExtractorMateriasLCD("esquema_optimizado.json")
    # await extractor3.ejecutar_extraccion_final()


def mostrar_ejemplos_uso():
    """Muestra ejemplos de cómo usar diferentes esquemas"""
    print("\n📚 EJEMPLOS DE USO:")
    print("=" * 40)
    
    ejemplos = [
        {
            "descripcion": "Esquema por defecto (auto-generado)",
            "codigo": "extractor = ExtractorMateriasLCD()",
            "archivo": "generated_css_schema.json"
        },
        {
            "descripcion": "Esquema personalizado",
            "codigo": "extractor = ExtractorMateriasLCD('mi_esquema.json')",
            "archivo": "mi_esquema.json"
        },
        {
            "descripcion": "Esquema optimizado para otra página",
            "codigo": "extractor = ExtractorMateriasLCD('esquema_otra_pagina.json')",
            "archivo": "esquema_otra_pagina.json"
        },
        {
            "descripcion": "Esquema específico para horarios",
            "codigo": "extractor = ExtractorMateriasLCD('esquema_horarios.json')",
            "archivo": "esquema_horarios.json"
        }
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n{i}. {ejemplo['descripcion']}")
        print(f"   Código: {ejemplo['codigo']}")
        print(f"   Archivo: {ejemplo['archivo']}")
    
    print(f"\n💡 VENTAJAS:")
    print("   ✅ Solo cambias el nombre del archivo")
    print("   ✅ No necesitas modificar el código de extracción")
    print("   ✅ Puedes tener múltiples esquemas para diferentes sitios")
    print("   ✅ Fácil de mantener y actualizar")


if __name__ == "__main__":
    # Mostrar ejemplos de uso
    mostrar_ejemplos_uso()
    
    # Ejecutar extracción
    asyncio.run(main())
