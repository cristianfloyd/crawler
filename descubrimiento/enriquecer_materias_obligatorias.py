#!/usr/bin/env python3
"""
FASE 5: Enriquecedor de Materias Obligatorias LCD
Extrae información adicional de https://lcd.exactas.uba.ar/materias-obligatorias/
"""

import json
import re
import os
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai import CrawlerRunConfig, CacheMode
from datetime import datetime


class EnriquecedorMateriasObligatorias:
    def __init__(self):
        self.url_obligatorias = "https://lcd.exactas.uba.ar/materias-obligatorias/"
        self.materias_enriquecidas = {
            "cbc": [],
            "segundo_ciclo": [],
            "tercer_ciclo": [],
            "metadata": {
                "fecha_enriquecimiento": datetime.now().isoformat(),
                "fuente_enriquecimiento": self.url_obligatorias,
                "metodo": "crawl4ai_css_obligatorias",
                "version": "fase5_enrichment",
                "total_enriquecidas": 0,
            },
        }

    async def extraer_informacion_obligatorias(self):
        """Extrae información detallada de materias obligatorias"""
        print("🔍 FASE 5: Extrayendo información de materias obligatorias...")
        print(f"   📍 URL: {self.url_obligatorias}")

        # Esquema para extraer información de la página de obligatorias
        schema_obligatorias = {
            "name": "materias_obligatorias_detalle",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "cuatrimestres",
                    "selector": "h2, h3, .semester-title, [class*='cuatrimestre'], [class*='semester']",
                    "type": "list",
                    "fields": [{"name": "titulo", "selector": "self", "type": "text"}],
                },
                {
                    "name": "materias_por_periodo",
                    "selector": "table, .course-table, .materia-row, tr",
                    "type": "list",
                    "fields": [
                        {
                            "name": "materia",
                            "selector": "td:first-child, .course-name, .materia-nombre",
                            "type": "text",
                        },
                        {
                            "name": "departamento",
                            "selector": "td:nth-child(2), .department, .departamento",
                            "type": "text",
                        },
                        {
                            "name": "enlace_web",
                            "selector": "a[href], .web-link",
                            "type": "attribute",
                            "attribute": "href",
                        },
                        {
                            "name": "codigo",
                            "selector": "td:nth-child(3), .course-code, .codigo",
                            "type": "text",
                        },
                    ],
                },
                {
                    "name": "informacion_general",
                    "selector": "p, .info-text, .description",
                    "type": "list",
                    "fields": [{"name": "texto", "selector": "self", "type": "text"}],
                },
                {"name": "contenido_completo", "selector": "body", "type": "text"},
            ],
        }

        async with AsyncWebCrawler(
            verbose=False,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium",
        ) as crawler:

            extraction_strategy = JsonCssExtractionStrategy(schema_obligatorias)

            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=extraction_strategy,
            )

            result = await crawler.arun(url=self.url_obligatorias, config=config)

            if (
                result
                and hasattr(result, "extracted_content")
                and result.extracted_content
            ):
                print("✅ Extracción exitosa de materias obligatorias")

                # Parse del contenido extraído
                extracted_data = json.loads(result.extracted_content)
                print(f"   🔍 Datos extraídos: {type(extracted_data)}")

                # Debug del contenido
                with open("debug_obligatorias.json", "w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                print("   📁 Debug guardado en: debug_obligatorias.json")

                await self.procesar_datos_obligatorias(extracted_data)

            else:
                print("❌ No se pudo extraer contenido de materias obligatorias")
                # Usar análisis alternativo
                await self.analisis_alternativo()

    async def procesar_datos_obligatorias(self, extracted_data):
        """Procesa los datos extraídos de materias obligatorias"""
        print("🔄 Procesando datos de materias obligatorias...")

        if isinstance(extracted_data, list) and extracted_data:
            extracted_data = extracted_data[0]

        # Procesar información de cuatrimestres
        cuatrimestres = extracted_data.get("cuatrimestres", [])
        materias_periodo = extracted_data.get("materias_por_periodo", [])
        info_general = extracted_data.get("informacion_general", [])

        print(f"   📅 Cuatrimestres encontrados: {len(cuatrimestres)}")
        print(f"   📚 Materias por período: {len(materias_periodo)}")
        print(f"   ℹ️ Información general: {len(info_general)}")

        # Procesar materias encontradas y enriquecer con información de horarios
        await self.enriquecer_materias_con_info_obligatorias(materias_periodo)

        # Analizar contenido completo para extraer patrones
        contenido_completo = extracted_data.get("contenido_completo", "")
        await self.extraer_patrones_del_contenido(contenido_completo)

    async def extraer_patrones_del_contenido(self, contenido: str):
        """Extrae patrones útiles del contenido completo"""
        print("🔍 Analizando patrones en el contenido...")

        # Buscar menciones de cuatrimestres
        patrones_cuatrimestre = re.findall(
            r"(1er|2do|primer|segundo)\s+cuatrimestre\s+(\d{4})",
            contenido,
            re.IGNORECASE,
        )
        patrones_verano = re.findall(r"verano\s+(\d{4})", contenido, re.IGNORECASE)

        # Buscar códigos de materia
        patrones_codigo = re.findall(
            r"\b\d{2}\.\d{2}\b|\b[A-Z]{2,4}\d{2,4}\b", contenido
        )

        # Buscar información de departamentos
        patrones_depto = re.findall(
            r"departamento\s+de\s+([a-záéíóúñ\s]+)", contenido, re.IGNORECASE
        )

        print(f"   📅 Patrones de cuatrimestre: {len(patrones_cuatrimestre)}")
        print(f"   ☀️ Patrones de verano: {len(patrones_verano)}")
        print(f"   🔢 Códigos encontrados: {len(patrones_codigo)}")
        print(f"   🏢 Departamentos: {len(patrones_depto)}")

        # Guardar patrones encontrados
        self.materias_enriquecidas["metadata"]["patrones_encontrados"] = {
            "cuatrimestres": patrones_cuatrimestre,
            "veranos": patrones_verano,
            "codigos": patrones_codigo[:10],  # Primeros 10
            "departamentos": list(set(patrones_depto)),
        }

    async def analisis_alternativo(self):
        """Análisis alternativo si falla la extracción principal"""
        print("🔄 Ejecutando análisis alternativo...")

        async with AsyncWebCrawler(
            verbose=False,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium",
        ) as crawler:

            result = await crawler.arun(url=self.url_obligatorias)

            if result and result.html:
                print("✅ HTML obtenido para análisis alternativo")

                # Análisis básico del HTML
                html_content = result.html

                # Buscar tablas
                tablas = re.findall(r"<table[^>]*>.*?</table>", html_content, re.DOTALL)
                print(f"   📊 Tablas encontradas: {len(tablas)}")

                # Buscar enlaces de materias
                enlaces = re.findall(
                    r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html_content
                )
                enlaces_materias = [
                    e
                    for e in enlaces
                    if "materia" in e[0].lower() or len(e[1].strip()) > 10
                ]
                print(f"   🔗 Enlaces de materias: {len(enlaces_materias)}")

                # Guardar análisis
                with open("debug_html_obligatorias.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("   📁 HTML guardado en: debug_html_obligatorias.html")

    async def enriquecer_materias_con_info_obligatorias(self, materias_obligatorias):
        """Enriquece las materias base con información de materias obligatorias"""
        print("🔗 Enriqueciendo materias con información de horarios...")

        # Cargar materias base como referencia
        materias_base = self.cargar_materias_base()
        if not materias_base:
            print("   ⚠️ No se pudieron cargar materias base")
            return

        # Crear diccionario de referencia para búsqueda rápida
        materias_referencia = {}
        for ciclo in ["cbc", "segundo_ciclo", "tercer_ciclo"]:
            for materia in materias_base.get(ciclo, []):
                nombre_norm = self.normalizar_nombre_para_busqueda(materia["nombre"])
                materias_referencia[nombre_norm] = {
                    "ciclo": ciclo,
                    "materia_original": materia,
                }

        print(f"   📋 Materias de referencia cargadas: {len(materias_referencia)}")

        # Procesar materias obligatorias y buscar coincidencias
        materias_enriquecidas = 0
        cuatrimestres_detectados = set()

        for materia_obl in materias_obligatorias:
            if not materia_obl or not materia_obl.get("materia"):
                continue

            nombre_obl = materia_obl["materia"].strip()
            nombre_norm = self.normalizar_nombre_para_busqueda(nombre_obl)

            # Buscar coincidencia en materias de referencia
            if nombre_norm in materias_referencia:
                ref_data = materias_referencia[nombre_norm]
                ciclo = ref_data["ciclo"]
                materia_original = ref_data["materia_original"]

                # Enriquecer la materia original con información de horarios
                self.agregar_info_horarios(materia_original, materia_obl)

                # Detectar cuatrimestre del enlace
                cuatrimestre = self.extraer_cuatrimestre_de_url(
                    materia_obl.get("enlace_web", "")
                )
                if cuatrimestre:
                    cuatrimestres_detectados.add(cuatrimestre)
                    materia_original["cuatrimestre_detectado"] = cuatrimestre

                materias_enriquecidas += 1
                print(f"     ✅ Enriquecida: {nombre_obl} -> {ciclo}")
            else:
                # Intentar coincidencia parcial
                coincidencia_parcial = self.buscar_coincidencia_parcial(
                    nombre_norm, materias_referencia
                )
                if coincidencia_parcial:
                    ref_data = materias_referencia[coincidencia_parcial]
                    materia_original = ref_data["materia_original"]
                    self.agregar_info_horarios(materia_original, materia_obl)
                    materias_enriquecidas += 1
                    print(
                        f"     🔄 Coincidencia parcial: {nombre_obl} -> {coincidencia_parcial}"
                    )

        print(f"   📊 Materias enriquecidas: {materias_enriquecidas}")
        print(f"   📅 Cuatrimestres detectados: {sorted(cuatrimestres_detectados)}")

        # Actualizar metadata con información de enriquecimiento
        self.materias_enriquecidas["metadata"][
            "materias_enriquecidas"
        ] = materias_enriquecidas
        self.materias_enriquecidas["metadata"]["cuatrimestres_detectados"] = sorted(
            cuatrimestres_detectados
        )
        self.materias_enriquecidas["metadata"]["cuatrimestre_mas_actual"] = (
            max(cuatrimestres_detectados) if cuatrimestres_detectados else None
        )

    def normalizar_nombre_para_busqueda(self, nombre):
        """Normaliza nombre de materia para búsqueda"""
        nombre = nombre.lower()
        # Remover acentos
        nombre = nombre.replace("á", "a").replace("é", "e").replace("í", "i")
        nombre = nombre.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        # Remover caracteres especiales y espacios extra
        nombre = re.sub(r"[^\w\s]", " ", nombre)
        nombre = re.sub(r"\s+", " ", nombre)
        nombre = nombre.strip()
        return nombre

    def buscar_coincidencia_parcial(self, nombre_busqueda, materias_referencia):
        """Busca coincidencias parciales en nombres de materias"""
        palabras_busqueda = nombre_busqueda.split()

        for nombre_ref in materias_referencia.keys():
            palabras_ref = nombre_ref.split()

            # Verificar si al menos 2 palabras coinciden
            coincidencias = sum(
                1 for palabra in palabras_busqueda if palabra in palabras_ref
            )
            if coincidencias >= 2 and len(palabras_busqueda) >= 2:
                return nombre_ref

        return None

    def agregar_info_horarios(self, materia_original, materia_obligatoria):
        """Agrega información de horarios a la materia original"""
        if "info_horarios" not in materia_original:
            materia_original["info_horarios"] = {}

        info_horarios = materia_original["info_horarios"]
        info_horarios["departamento_confirmado"] = materia_obligatoria.get(
            "departamento", ""
        )
        info_horarios["enlace_horarios"] = materia_obligatoria.get("enlace_web", "")
        info_horarios["codigo_materia"] = materia_obligatoria.get("codigo", "")
        info_horarios["fuente_enriquecimiento"] = "materias_obligatorias_lcd"
        info_horarios["fecha_enriquecimiento"] = datetime.now().isoformat()

    def extraer_cuatrimestre_de_url(self, url):
        """Extrae información de cuatrimestre de la URL"""
        if not url:
            return None

        # Buscar patrón cuatrimestre=X
        match = re.search(r"cuatrimestre=([^&]+)", url)
        if match:
            cuatrimestre = match.group(1)
            # Mapear códigos a nombres legibles
            if cuatrimestre == "1":
                return "2025_1er_cuatrimestre"
            elif cuatrimestre == "2":
                return "2025_2do_cuatrimestre"
            elif cuatrimestre == "v":
                return "2025_verano"
            else:
                return f"2025_{cuatrimestre}"

        # Buscar año en la URL
        match_ano = re.search(r"ano=(\d{4})", url)
        if match_ano:
            return f"{match_ano.group(1)}_general"

        return None

    def cargar_materias_base(self):
        """Carga las materias base desde el archivo utilizado por los componentes superiores"""
        archivo_base = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "materias.json"
        )

        if os.path.exists(archivo_base):
            with open(archivo_base, "r", encoding="utf-8") as f:
                materias_lista = json.load(f)

            # Convertir lista plana a estructura por ciclos para compatibilidad
            materias_por_ciclo = {
                "cbc": [],
                "segundo_ciclo": [],
                "tercer_ciclo": [],
                "metadata": {
                    "total_materias": len(materias_lista),
                    "fuente": "data/materias.json",
                    "estructura": "lista_plana_convertida",
                },
            }

            for materia in materias_lista:
                ciclo = materia.get("ciclo", "")

                # Mapear nombres de ciclos
                if ciclo == "CBC":
                    materias_por_ciclo["cbc"].append(
                        {
                            "nombre": materia.get("materia", ""),
                            "descripcion": materia.get("descripcion", ""),
                            "ciclo": "cbc",
                        }
                    )
                elif ciclo == "Segundo Ciclo de Grado":
                    materias_por_ciclo["segundo_ciclo"].append(
                        {
                            "nombre": materia.get("materia", ""),
                            "descripcion": materia.get("descripcion", ""),
                            "ciclo": "segundo_ciclo",
                        }
                    )
                elif ciclo == "Tercer Ciclo de Grado":
                    materias_por_ciclo["tercer_ciclo"].append(
                        {
                            "nombre": materia.get("materia", ""),
                            "descripcion": materia.get("descripcion", ""),
                            "ciclo": "tercer_ciclo",
                        }
                    )

            print(f"✅ Materias cargadas desde {archivo_base}")
            print(f"   📊 CBC: {len(materias_por_ciclo['cbc'])}")
            print(f"   📊 Segundo Ciclo: {len(materias_por_ciclo['segundo_ciclo'])}")
            print(f"   📊 Tercer Ciclo: {len(materias_por_ciclo['tercer_ciclo'])}")

            return materias_por_ciclo
        else:
            print(f"⚠️ No se encontró archivo base: {archivo_base}")
            return None

    async def enriquecer_materias_completo(self):
        """Ejecuta el proceso completo de enriquecimiento"""
        print("🚀 INICIANDO FASE 5: ENRIQUECIMIENTO DE MATERIAS")
        print("=" * 60)

        # Cargar materias base
        print("📂 Cargando materias base...")
        materias_base = self.cargar_materias_base()

        if materias_base:
            print(
                f"   ✅ Cargadas: {materias_base['metadata']['total_materias']} materias base"
            )
            self.materias_enriquecidas = materias_base.copy()
        else:
            print("   ⚠️ No se encontraron materias base, continuando sin ellas")

        # Extraer información adicional
        await self.extraer_informacion_obligatorias()

        # Generar reporte
        self.generar_reporte_enriquecimiento()

        # Guardar resultados
        self.guardar_resultados_enriquecidos()

        print("\n✅ FASE 5 - PASO 1 COMPLETADO")
        print("=" * 60)

    def generar_reporte_enriquecimiento(self):
        """Genera reporte del proceso de enriquecimiento"""
        print("\n📊 REPORTE DE ENRIQUECIMIENTO")
        print("-" * 40)

        metadata = self.materias_enriquecidas["metadata"]
        patrones = metadata.get("patrones_encontrados", {})

        print(f"Fecha: {metadata.get('fecha_enriquecimiento', 'N/A')}")
        print(f"Fuente: {metadata.get('fuente_enriquecimiento', 'N/A')}")
        print()
        print("Patrones encontrados:")
        print(f"  • Cuatrimestres: {len(patrones.get('cuatrimestres', []))}")
        print(f"  • Veranos: {len(patrones.get('veranos', []))}")
        print(f"  • Códigos: {len(patrones.get('codigos', []))}")
        print(f"  • Departamentos: {len(patrones.get('departamentos', []))}")

    def guardar_resultados_enriquecidos(self):
        """Guarda los resultados enriquecidos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_enriquecido = f"materias_lcd_enriquecidas_{timestamp}.json"

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        ruta_completa = os.path.join(data_dir, archivo_enriquecido)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(self.materias_enriquecidas, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Resultados enriquecidos guardados en: {ruta_completa}")
        return ruta_completa


async def main():
    """Función principal"""
    enriquecedor = EnriquecedorMateriasObligatorias()
    await enriquecedor.enriquecer_materias_completo()


if __name__ == "__main__":
    asyncio.run(main())
