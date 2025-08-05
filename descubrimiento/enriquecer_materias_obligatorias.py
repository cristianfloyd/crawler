#!/usr/bin/env python3
"""
FASE 5: Extractor de Materias Obligatorias LCD
Extrae materias obligatorias por cuatrimestre de https://lcd.exactas.uba.ar/materias-obligatorias/
Formato de salida: cuatrimestre -> materia -> departamento -> link
"""

import json
import re
import os
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai import CrawlerRunConfig, CacheMode
from datetime import datetime
from normalizador_nombres_materias import NormalizadorNombresMaterias


class ExtractorMateriasObligatorias:
    def __init__(self):
        self.url_obligatorias = "https://lcd.exactas.uba.ar/materias-obligatorias/"
        self.normalizador = NormalizadorNombresMaterias()
        self.materias_obligatorias = {
            "cuatrimestres": {
                "verano_2025": [],
                "primer_cuatrimestre_2025": [],
                "segundo_cuatrimestre_2025": [],
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fuente": self.url_obligatorias,
                "metodo": "crawl4ai_css_extraction_con_normalizador",
                "version": "fase5_v3_normalizador_integrado",
                "total_materias": 0,
            },
        }

    async def extraer_materias_obligatorias(self):
        """Extrae materias obligatorias organizadas por cuatrimestre"""
        print("🔍 FASE 5: Extrayendo materias obligatorias por cuatrimestre...")
        print(f"   📍 URL: {self.url_obligatorias}")

        # Esquema para extraer cuatrimestres y sus materias
        schema_cuatrimestres = {
            "name": "materias_por_cuatrimestre",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "secciones_cuatrimestre",
                    "selector": "h2, h3",
                    "type": "list",
                    "fields": [
                        {
                            "name": "titulo_cuatrimestre",
                            "selector": "self",
                            "type": "text",
                        },
                        {
                            "name": "materias",
                            "selector": "+ * table tr:not(:first-child), + table tr:not(:first-child)",
                            "type": "list",
                            "fields": [
                                {
                                    "name": "materia",
                                    "selector": "td:first-child",
                                    "type": "text",
                                },
                                {
                                    "name": "departamento",
                                    "selector": "td:nth-child(2)",
                                    "type": "text",
                                },
                                {
                                    "name": "enlace",
                                    "selector": "td:nth-child(3) a",
                                    "type": "attribute",
                                    "attribute": "href",
                                },
                            ],
                        },
                    ],
                },
                {"name": "contenido_html", "selector": "body", "type": "text"},
            ],
        }

        async with AsyncWebCrawler(
            verbose=False,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium",
        ) as crawler:

            extraction_strategy = JsonCssExtractionStrategy(schema_cuatrimestres)

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

                await self.procesar_datos_cuatrimestres(extracted_data)

            else:
                print(
                    "❌ No se pudo extraer contenido con CSS, intentando análisis HTML directo"
                )
                # Usar análisis alternativo
                await self.extraer_con_html_directo()

    async def procesar_datos_cuatrimestres(self, extracted_data):
        """Procesa los datos extraídos organizados por cuatrimestre"""
        print("🔄 Procesando datos por cuatrimestre...")

        # Manejar diferentes tipos de datos extraídos
        if isinstance(extracted_data, list):
            if not extracted_data:
                print(
                    "   ⚠️ No se extrajeron datos con CSS, intentando análisis HTML directo..."
                )
                await self.extraer_con_html_directo()
                return
            extracted_data = extracted_data[0]

        if not isinstance(extracted_data, dict):
            print(f"   ⚠️ Formato de datos inesperado: {type(extracted_data)}")
            await self.extraer_con_html_directo()
            return

        # Procesar secciones de cuatrimestre
        secciones = extracted_data.get("secciones_cuatrimestre", [])
        print(f"   📅 Secciones encontradas: {len(secciones)}")

        for seccion in secciones:
            titulo = seccion.get("titulo_cuatrimestre", "").strip()
            materias = seccion.get("materias", [])

            # Identificar cuatrimestre
            cuatrimestre_key = self.identificar_cuatrimestre(titulo)
            if cuatrimestre_key:
                print(f"   📚 Procesando {titulo}: {len(materias)} materias")
                self.procesar_materias_cuatrimestre(cuatrimestre_key, materias)

        # Si no se extraíeron datos con CSS, intentar análisis HTML
        contenido_html = extracted_data.get("contenido_html", "")
        if (
            sum(
                len(cuatrimestre)
                for cuatrimestre in self.materias_obligatorias["cuatrimestres"].values()
            )
            == 0
        ):
            print("   ⚠️ Extrayendo desde HTML directo...")
            await self.extraer_desde_html(contenido_html)

    def identificar_cuatrimestre(self, titulo):
        """Identifica el cuatrimestre según el título"""
        titulo_lower = titulo.lower()

        if "verano" in titulo_lower and "2025" in titulo:
            return "verano_2025"
        elif ("1er" in titulo_lower or "primer" in titulo_lower) and "2025" in titulo:
            return "primer_cuatrimestre_2025"
        elif ("2do" in titulo_lower or "segundo" in titulo_lower) and "2025" in titulo:
            return "segundo_cuatrimestre_2025"

        return None

    def procesar_materias_cuatrimestre(self, cuatrimestre_key, materias_raw):
        """Procesa las materias de un cuatrimestre específico"""
        materias_procesadas = []

        for materia_raw in materias_raw:
            materia = materia_raw.get("materia", "").strip()
            departamento = materia_raw.get("departamento", "").strip()
            enlace = materia_raw.get("enlace", "").strip()

            if materia and departamento:  # Solo agregar si tiene datos básicos
                # Usar el normalizador inteligente
                materia_normalizada = self.normalizador.normalizar_nombre_web(materia)
                
                # Solo agregar si se pudo normalizar correctamente
                if materia_normalizada and len(materia_normalizada) >= 3:
                    materia_data = {
                        "materia": materia_normalizada,
                        "materia_original": materia,  # Mantener original para debug
                        "departamento": self.limpiar_departamento(departamento),
                        "enlace": enlace if enlace else None,
                    }
                    materias_procesadas.append(materia_data)

        self.materias_obligatorias["cuatrimestres"][
            cuatrimestre_key
        ] = materias_procesadas
        print(
            f"     ✅ {cuatrimestre_key}: {len(materias_procesadas)} materias agregadas"
        )

    async def extraer_con_html_directo(self):
        """Extrae datos directamente del HTML si falla CSS"""
        print("🔄 Ejecutando extracción HTML directa...")

        async with AsyncWebCrawler(
            verbose=False,
            headless=True,
            always_by_pass_cache=True,
            browser_type="chromium",
        ) as crawler:

            result = await crawler.arun(url=self.url_obligatorias)

            if result and result.html:
                print("✅ HTML obtenido para análisis directo")
                await self.extraer_desde_html(result.html)

    async def extraer_desde_html(self, html_content):
        """Extrae materias desde HTML directo como fallback"""
        print("🔍 Analizando HTML para extraer materias...")

        # Buscar headers de cuatrimestre y sus tablas siguientes
        # Patrón: h2/h3 seguido de tabla
        patron_seccion = r"<h[23][^>]*>([^<]*(?:cuatrimestre|verano)[^<]*)</h[23]>.*?<table[^>]*>(.*?)</table>"
        secciones = re.findall(patron_seccion, html_content, re.DOTALL | re.IGNORECASE)

        print(f"   📅 Secciones encontradas: {len(secciones)}")

        for titulo, tabla_html in secciones:
            cuatrimestre_key = self.identificar_cuatrimestre(titulo.strip())
            if not cuatrimestre_key:
                continue

            # Extraer filas de la tabla (saltando header)
            filas = re.findall(r"<tr[^>]*>(.*?)</tr>", tabla_html, re.DOTALL)
            materias = []

            for i, fila in enumerate(filas):
                if i == 0:  # Saltar header
                    continue

                celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)
                if len(celdas) >= 2:
                    materia = re.sub(r"<[^>]+>", "", celdas[0]).strip()
                    departamento = re.sub(r"<[^>]+>", "", celdas[1]).strip()

                    # Buscar enlace en la tercera celda
                    enlace = None
                    if len(celdas) >= 3:
                        enlace_match = re.search(r'href="([^"]+)"', celdas[2])
                        if enlace_match:
                            enlace = enlace_match.group(1)

                    if materia and departamento:
                        # Usar el normalizador inteligente
                        materia_normalizada = self.normalizador.normalizar_nombre_web(materia)
                        
                        # Solo agregar si se pudo normalizar correctamente
                        if materia_normalizada and len(materia_normalizada) >= 3:
                            materias.append(
                                {
                                    "materia": materia_normalizada,
                                    "materia_original": materia,  # Mantener original para debug
                                    "departamento": self.limpiar_departamento(departamento),
                                    "enlace": enlace,
                                }
                            )

            self.materias_obligatorias["cuatrimestres"][cuatrimestre_key] = materias
            print(f"     ✅ {cuatrimestre_key}: {len(materias)} materias extraídas")


    def limpiar_departamento(self, departamento):
        """Limpia el nombre del departamento"""
        # Remover tags HTML residuales
        departamento = re.sub(r"<[^>]+>", "", departamento)
        # Limpiar espacios extra
        departamento = re.sub(r"\s+", " ", departamento)
        return departamento.strip()

    def guardar_materias_obligatorias(self):
        """Guarda las materias obligatorias en formato JSON"""
        # Actualizar metadata
        total_materias = sum(
            len(materias)
            for materias in self.materias_obligatorias["cuatrimestres"].values()
        )
        self.materias_obligatorias["metadata"]["total_materias"] = total_materias

        # Guardar archivo
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        archivo_salida = os.path.join(data_dir, "materias_obligatorias.json")

        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(self.materias_obligatorias, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Materias obligatorias guardadas en: {archivo_salida}")
        print(f"   📊 Total de materias: {total_materias}")

        return archivo_salida

    def enriquecer_materias_base(self):
        """Enriquece materias_lcd_descubiertas.json con información de materias obligatorias"""
        print("\n🔗 Enriqueciendo materias LCD descubiertas con datos de cuatrimestres...")

        # Cargar materias base
        materias_base = self.cargar_materias_base()
        if not materias_base:
            print("   ⚠️ No se pudieron cargar materias base")
            return None

        # Crear índice de materias obligatorias usando el normalizador
        indice_obligatorias = {}
        for cuatrimestre, materias in self.materias_obligatorias[
            "cuatrimestres"
        ].items():
            for materia in materias:
                # Usar el mismo normalizador para consistencia
                nombre_norm = self.normalizador._preparar_para_matching(materia["materia"])
                indice_obligatorias[nombre_norm] = {
                    "cuatrimestre": cuatrimestre,
                    "departamento": materia["departamento"],
                    "enlace": materia["enlace"],
                    "materia_normalizada": materia["materia"]  # Para debugging
                }

        # Enriquecer materias base
        materias_enriquecidas = 0
        matches_encontrados = []
        
        for materia in materias_base:
            # En materias_lcd_descubiertas.json el campo es 'nombre', no 'materia'
            nombre_materia = materia.get("nombre", materia.get("nombre_normalizado", ""))
            nombre_norm = self.normalizador._preparar_para_matching(nombre_materia)
            
            if nombre_norm in indice_obligatorias:
                info_obligatoria = indice_obligatorias[nombre_norm]
                materia["cuatrimestre_disponible"] = info_obligatoria["cuatrimestre"]
                materia["departamento_confirmado"] = info_obligatoria["departamento"]
                materia["enlace_horarios"] = info_obligatoria["enlace"]
                materia["es_obligatoria"] = True
                materias_enriquecidas += 1
                
                # Para debugging
                matches_encontrados.append({
                    "original": nombre_materia,
                    "match": info_obligatoria["materia_normalizada"],
                    "cuatrimestre": info_obligatoria["cuatrimestre"]
                })
            else:
                materia["es_obligatoria"] = False

        print(
            f"   ✅ Materias enriquecidas: {materias_enriquecidas}/{len(materias_base)}"
        )
        
        # Mostrar algunos matches para debugging
        if matches_encontrados:
            print(f"\n🔍 Ejemplos de matches encontrados:")
            for i, match in enumerate(matches_encontrados[:3]):
                print(f"   • '{match['original']}' → '{match['match']}' ({match['cuatrimestre']})")
            if len(matches_encontrados) > 3:
                print(f"   ... y {len(matches_encontrados) - 3} más")

        # Guardar materias enriquecidas (mantiene estructura por ciclos)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        
        # Reconstruir estructura por ciclos para el archivo enriquecido
        estructura_enriquecida = {
            "cbc": [],
            "segundo_ciclo": [],
            "tercer_ciclo": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "fuente_base": "materias_lcd_descubiertas.json",
                "fuente_enriquecimiento": "materias_obligatorias.json",
                "metodo": "fase5_enriquecimiento_cuatrimestres",
                "total_materias": len(materias_base),
                "materias_enriquecidas": materias_enriquecidas,
                "porcentaje_enriquecimiento": round((materias_enriquecidas/len(materias_base))*100, 1)
            }
        }
        
        # Separar materias enriquecidas por ciclo
        for materia in materias_base:
            ciclo = materia.get("ciclo", "sin_ciclo")
            if ciclo in estructura_enriquecida:
                estructura_enriquecida[ciclo].append(materia)
        
        archivo_enriquecido = os.path.join(data_dir, "materias_lcd_enriquecidas.json")

        with open(archivo_enriquecido, "w", encoding="utf-8") as f:
            json.dump(estructura_enriquecida, f, ensure_ascii=False, indent=2)

        print(f"   💾 Archivo enriquecido guardado: {archivo_enriquecido}")
        print(f"   📊 Porcentaje de enriquecimiento: {estructura_enriquecida['metadata']['porcentaje_enriquecimiento']}%")
        return archivo_enriquecido


    def generar_reporte_extraccion(self):
        """Genera reporte de la extracción realizada"""
        print("\n📊 REPORTE DE EXTRACCIÓN")
        print("-" * 40)

        total_materias = 0
        for cuatrimestre, materias in self.materias_obligatorias[
            "cuatrimestres"
        ].items():
            count = len(materias)
            total_materias += count
            print(f"   {cuatrimestre}: {count} materias")

        print(f"\nTotal materias extraídas: {total_materias}")
        print(f"Timestamp: {self.materias_obligatorias['metadata']['timestamp']}")
        print(f"Fuente: {self.materias_obligatorias['metadata']['fuente']}")

    def validar_datos_extraidos(self):
        """Valida los datos extraídos"""
        print("\n🔍 Validando datos extraídos...")

        errores = []
        total_materias = 0
        nombres_normalizados = []

        for cuatrimestre, materias in self.materias_obligatorias[
            "cuatrimestres"
        ].items():
            for i, materia in enumerate(materias):
                total_materias += 1

                # Validar campos requeridos
                if not materia.get("materia"):
                    errores.append(f"{cuatrimestre}[{i}]: Falta nombre de materia")
                if not materia.get("departamento"):
                    errores.append(f"{cuatrimestre}[{i}]: Falta departamento")

                # Validar longitud de nombres
                if len(materia.get("materia", "")) < 3:
                    errores.append(f"{cuatrimestre}[{i}]: Nombre muy corto")
                
                # Recopilar nombres para mostrar ejemplos de normalización
                if materia.get("materia_original") and materia.get("materia"):
                    original = materia["materia_original"]
                    normalizado = materia["materia"]
                    if original != normalizado:
                        nombres_normalizados.append((original, normalizado))

        if errores:
            print(f"   ⚠️ {len(errores)} errores encontrados:")
            for error in errores[:5]:  # Mostrar solo primeros 5
                print(f"     - {error}")
            if len(errores) > 5:
                print(f"     ... y {len(errores) - 5} más")
        else:
            print(f"   ✅ Todos los datos válidos ({total_materias} materias)")
        
        # Mostrar ejemplos de normalización
        if nombres_normalizados:
            print(f"\n🔄 Ejemplos de normalización con Normalizador Inteligente ({len(nombres_normalizados)} materias):")
            for i, (original, normalizado) in enumerate(nombres_normalizados[:3]):
                print(f"   • '{original}' → '{normalizado}'")
            if len(nombres_normalizados) > 3:
                print(f"   ... y {len(nombres_normalizados) - 3} más normalizadas")
            
            # Mostrar estadísticas del normalizador
            stats = self.normalizador.obtener_estadisticas()
            print(f"\n📊 Estadísticas del Normalizador:")
            print(f"   • Materias base: {stats['total_materias_base']}")
            print(f"   • Variaciones en índice: {stats['total_variaciones_indice']}")

        return len(errores) == 0

    def cargar_materias_base(self):
        """Carga las materias base desde materias_lcd_descubiertas.json"""
        archivo_base = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "materias_lcd_descubiertas.json"
        )

        if os.path.exists(archivo_base):
            with open(archivo_base, "r", encoding="utf-8") as f:
                datos_estructurados = json.load(f)

            # Convertir estructura por ciclos a lista plana para compatibilidad
            materias_lista = []
            
            # Procesar CBC
            for materia in datos_estructurados.get("cbc", []):
                materias_lista.append(materia)
            
            # Procesar segundo ciclo
            for materia in datos_estructurados.get("segundo_ciclo", []):
                materias_lista.append(materia)
            
            # Procesar tercer ciclo
            for materia in datos_estructurados.get("tercer_ciclo", []):
                materias_lista.append(materia)

            print(f"✅ Materias LCD descubiertas cargadas: {len(materias_lista)}")
            print(f"   📊 CBC: {len(datos_estructurados.get('cbc', []))} materias")
            print(f"   📊 Segundo Ciclo: {len(datos_estructurados.get('segundo_ciclo', []))} materias")
            print(f"   📊 Tercer Ciclo: {len(datos_estructurados.get('tercer_ciclo', []))} caminos")
            return materias_lista
        else:
            print(f"⚠️ No se encontró archivo base: {archivo_base}")
            print(f"   💡 Ejecutar primero: python descubrimiento/descubrir_materias_completo.py")
            return None

    async def ejecutar_extraccion_completa(self):
        """Ejecuta el proceso completo de extracción"""
        print("🚀 INICIANDO FASE 5: EXTRACCIÓN DE MATERIAS OBLIGATORIAS")
        print("=" * 60)
        print("🧠 Normalizador Inteligente integrado")
        
        # Mostrar estadísticas del normalizador
        stats = self.normalizador.obtener_estadisticas()
        print(f"   📋 {stats['total_materias_base']} materias base cargadas")
        print(f"   🔗 {stats['total_variaciones_indice']} variaciones para matching")
        print()

        # Extraer materias obligatorias
        await self.extraer_materias_obligatorias()

        # Validar datos
        datos_validos = self.validar_datos_extraidos()

        if datos_validos:
            # Guardar datos
            archivo_guardado = self.guardar_materias_obligatorias()

            # Generar reporte
            self.generar_reporte_extraccion()

            # Enriquecer materias base
            self.enriquecer_materias_base()

            print("\n✅ FASE 5 COMPLETADA EXITOSAMENTE")
            print("=" * 60)

            return archivo_guardado
        else:
            print("\n❌ FASE 5 COMPLETADA CON ERRORES")
            print("   Revisar datos extraídos antes de continuar")
            return None


async def main():
    """Función principal"""
    extractor = ExtractorMateriasObligatorias()
    await extractor.ejecutar_extraccion_completa()


if __name__ == "__main__":
    asyncio.run(main())
