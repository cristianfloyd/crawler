#!/usr/bin/env python3
"""
Scraper de Horarios - Departamento de Computación
Extrae horarios reales de materias de DC desde WordPress

Autor: Sistema RAG MVP
Fecha: 2025-07-26
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScraperHorariosDC:
    """Scraper especializado para horarios del Departamento de Computación"""

    def __init__(self):
        self.base_url = "https://www.dc.uba.ar/"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Patrones regex para parsing de horarios
        self.patrones_horarios = {
            # "Martes y Viernes de 9 a 11"
            "dias_rango": re.compile(
                r"((?:\w+(?:\s+y\s+\w+)*)+)\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})",
                re.IGNORECASE,
            ),
            # "Lunes de 17 a 22"
            "dia_rango": re.compile(
                r"(\w+)\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})", re.IGNORECASE
            ),
            # "miércoles de 19 a 22"
            "dia_rango_minuscula": re.compile(
                r"(\w+)\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})", re.IGNORECASE
            ),
            # "Jueves de 9 a 12 y de 13 a 16"
            "dia_doble_rango": re.compile(
                r"(\w+)\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})\s+y\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})",
                re.IGNORECASE,
            ),
        }

        # Mapeo de días
        self.dias_normalizados = {
            "lunes": "lunes",
            "martes": "martes",
            "miércoles": "miércoles",
            "miercoles": "miércoles",
            "jueves": "jueves",
            "viernes": "viernes",
            "sábado": "sábado",
            "sabado": "sábado",
            "domingo": "domingo",
        }

        # Tipos de actividades académicas
        self.tipos_actividad = {
            "teórica": "teoria",
            "teorica": "teoria",
            "práctica": "practica",
            "practica": "practica",
            "laboratorio": "laboratorio",
            "teórico-práctico": "teorico_practico",
            "teorico-practico": "teorico_practico",
            "teórico/práctica": "teorico_practico",
        }

        # Estadísticas
        self.stats = {
            "materias_procesadas": 0,
            "horarios_extraidos": 0,
            "errores_parsing": 0,
            "materias_encontradas": [],
            "errores": [],
        }

    def obtener_horarios_2c_2025(self) -> Optional[str]:
        """Obtiene el HTML de horarios del 2do cuatrimestre 2025"""
        # URL específica que sabemos que tiene los horarios
        url_horarios = "https://www.dc.uba.ar/ya-se-encuentran-publicadas-las-materias-del-primer-cuatrimestre-de-2025/"

        try:
            logger.info(f"Obteniendo horarios de: {url_horarios}")
            response = self.session.get(url_horarios, timeout=30)
            response.raise_for_status()

            # Verificar que la página contenga información de horarios
            indicadores_tabla = [
                "días y horarios",
                "MATERIA",
                "PERÍODO",
                "TIPO",
                "Profesores",
            ]

            texto_minuscula = response.text.lower()
            encontrado = any(
                indicador.lower() in texto_minuscula for indicador in indicadores_tabla
            )
            if not encontrado:
                logger.error("La página no contiene la tabla de horarios esperada")
                return None

            logger.info(f"HTML obtenido exitosamente ({len(response.text)} caracteres)")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Error al obtener HTML: {e}")
            return None

    def buscar_url_horarios_periodo(
        self, periodo: str = "2025", cuatrimestre: str = "2"
    ) -> Optional[str]:
        """Busca dinámicamente la URL de horarios para un período específico"""
        try:
            # Primero buscar en la página principal de cursada
            url_cursada = "https://www.dc.uba.ar/cursada-de-grado/"
            response = self.session.get(url_cursada)
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar links que contengan palabras clave del período
            keywords = [
                f"segundo cuatrimestre {periodo}",
                f"2c {periodo}",
                f"2do cuatrimestre {periodo}",
            ]

            for link in soup.find_all("a", href=True):
                texto_link = link.get_text().lower()
                href = link.get("href")

                for keyword in keywords:
                    if keyword in texto_link:
                        url_completa = urljoin(self.base_url, href)
                        logger.info(f"URL de horarios encontrada: {url_completa}")
                        return url_completa

            # Si no encontramos, usar la URL conocida como fallback
            logger.warning("No se encontró URL dinámica, usando URL conocida")
            return "https://www.dc.uba.ar/ya-se-encuentran-publicadas-las-materias-del-segundo-cuatrimestre-de-2025/"

        except Exception as e:
            logger.error(f"Error buscando URL de horarios: {e}")
            return None

    def extraer_horarios_de_tabla(self, html: str) -> List[Dict]:
        """Extrae horarios de la tabla HTML de DC"""
        soup = BeautifulSoup(html, "html.parser")
        materias_horarios = []

        # Buscar la tabla HTML directamente
        tabla = soup.find("table")
        if tabla:
            logger.info("Tabla HTML encontrada")
            return self._procesar_tabla_html(tabla)

        # Si no hay tabla HTML, buscar en el contenido de texto
        logger.info("No se encontró tabla HTML, buscando en contenido de texto")

        # Buscar patrones en el texto que indiquen estructura de tabla
        contenido = soup.get_text()
        lineas = contenido.split("\n")

        # Buscar líneas que contengan información de materias
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if not linea:
                continue

            # Buscar líneas que tengan formato de materia: nombre + información adicional
            if self._es_linea_materia(linea):
                try:
                    materia_info = self._procesar_linea_materia(linea, i)
                    if materia_info:
                        materias_horarios.append(materia_info)
                        self.stats["materias_procesadas"] += 1
                        if len(materias_horarios) < 5:  # Debug: mostrar primeras 5
                            logger.info(f"Materia extraída: {materia_info['nombre']}")
                except Exception as e:
                    logger.error(f"Error procesando línea {i}: {e}")
                    self.stats["errores_parsing"] += 1

        logger.info(f"Extraídas {len(materias_horarios)} materias con horarios")
        return materias_horarios

    def _procesar_tabla_html(self, tabla) -> List[Dict]:
        """Procesa una tabla HTML real"""
        materias_horarios = []
        filas = tabla.find_all("tr")

        for i, fila in enumerate(filas[1:]):  # Skip header
            celdas = fila.find_all(["td", "th"])
            if len(celdas) >= 5:
                partes = [celda.get_text().strip() for celda in celdas]
                try:
                    materia_info = self._procesar_fila_tabla(partes)
                    if materia_info:
                        materias_horarios.append(materia_info)
                        self.stats["materias_procesadas"] += 1
                except Exception as e:
                    logger.error(f"Error procesando fila HTML: {e}")
                    self.stats["errores_parsing"] += 1

        return materias_horarios

    def _es_linea_materia(self, linea: str) -> bool:
        """Determina si una línea contiene información de una materia"""
        # Patrones que indican que es una línea de materia
        indicadores = [
            "LCC",
            "LCD",  # Códigos de carrera
            "Álgebra",
            "Algoritmos",
            "Análisis",
            "Organización",
            "Sistemas",
            "Programación",
            "Paradigmas",
            "Bases de Datos",
            "Redes",
            "Machine Learning",
            "Software",
            "Computación",
        ]

        return (
            any(indicador.lower() in linea.lower() for indicador in indicadores)
            and len(linea) > 20
        )

    def _procesar_linea_materia(self, linea: str, linea_num: int) -> Optional[Dict]:
        """Procesa una línea de texto que contiene información de materia"""
        # Buscar patrones de horarios en la línea
        patrones_horario = [
            r"(\w+)\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})",  # "Lunes de 9 a 12"
            r"(\w+)\s+y\s+(\w+)\s+de\s+(\d{1,2})\s+a\s+(\d{1,2})",  # "Lunes y Miércoles de 9 a 12"
        ]

        # Extraer nombre de materia (generalmente al inicio)
        palabras = linea.split()
        if len(palabras) < 2:
            return None

        # El nombre suele estar al principio, buscar hasta encontrar algo que parezca horario
        nombre_candidato = ""
        for i, palabra in enumerate(palabras):
            if any(
                re.search(patron, " ".join(palabras[i:])) for patron in patrones_horario
            ):
                break
            nombre_candidato += " " + palabra

        nombre_materia = nombre_candidato.strip()
        if not nombre_materia or len(nombre_materia) < 5:
            return None

        # Extraer horarios
        resto_linea = linea[len(nombre_materia) :]
        horarios_estructurados = self._extraer_horarios_estructurados(resto_linea)

        # Generar información básica de la materia
        materia_id = self._generar_id_materia(nombre_materia, "1C 2025")

        return {
            "id": materia_id,
            "nombre": self._normalizar_nombre_materia(nombre_materia),
            "nombre_original": nombre_materia,
            "periodo": {
                "cuatrimestre": "1",
                "año": 2025,
                "codigo": "1C 2025",
            },
            "tipo_carrera": "Computación",
            "departamento": {
                "codigo": "DC",
                "nombre": "Departamento de Computación",
                "url_origen": "https://www.dc.uba.ar/",
            },
            "horarios": horarios_estructurados,
            "docentes": [],
            "observaciones": "",
            "metadata": {
                "fuente_url": "https://www.dc.uba.ar/ya-se-encuentran-publicadas-las-materias-del-primer-cuatrimestre-de-2025/",
                "fecha_extraccion": datetime.now().isoformat(),
                "departamento": "DC",
                "confiabilidad": "media",
                "tipo_dato": "horarios_reales",
                "linea_origen": linea_num,
            },
        }

    def _procesar_fila_tabla(self, partes: List[str]) -> Optional[Dict]:
        """Procesa una fila de la tabla de horarios con horarios separados por tipo"""
        if len(partes) < 5:
            return None

        materia_raw = partes[0].strip()
        periodo = partes[1].strip()
        tipo_carrera = partes[2].strip()
        profesores_raw = partes[3].strip()
        horarios_raw = partes[4].strip()
        observaciones = partes[5].strip() if len(partes) > 5 else ""

        # Filtrar filas vacías o headers
        if not materia_raw or materia_raw.upper() == "MATERIA" or len(materia_raw) < 3:
            return None

        # Normalizar nombre de materia
        nombre_materia = self._normalizar_nombre_materia(materia_raw)

        # Extraer horarios por tipo (nueva estructura)
        horarios_por_tipo = self._extraer_horarios_estructurados(horarios_raw)

        # Extraer profesores
        profesores = self._extraer_profesores(profesores_raw)

        # Generar ID único
        materia_id = self._generar_id_materia(nombre_materia, periodo)

        materia_info = {
            "id": materia_id,
            "nombre": nombre_materia,
            "nombre_original": materia_raw,
            "periodo": {
                "cuatrimestre": "2" if "2C" in periodo else "1",
                "año": 2025,
                "codigo": periodo,
            },
            "tipo_carrera": tipo_carrera,
            "departamento": {
                "codigo": "DC",
                "nombre": "Departamento de Computación",
                "url_origen": "https://www.dc.uba.ar/",
            },
            # Nueva estructura de horarios por tipo
            "horarios": {
                "teorica": horarios_por_tipo["teorica"],
                "practica": horarios_por_tipo["practica"],
                "laboratorio": horarios_por_tipo["laboratorio"],
            },
            "docentes": profesores,
            "observaciones": observaciones,
            "metadata": {
                "fuente_url": "https://www.dc.uba.ar/ya-se-encuentran-publicadas-las-materias-del-segundo-cuatrimestre-de-2025/",
                "fecha_extraccion": datetime.now().isoformat(),
                "departamento": "DC",
                "confiabilidad": "alta",
                "tipo_dato": "horarios_reales",
            },
        }

        self.stats["materias_encontradas"].append(nombre_materia)
        return materia_info

    def _normalizar_nombre_materia(self, nombre_raw: str) -> str:
        """Normaliza el nombre de una materia"""
        # Limpiar espacios múltiples
        nombre = re.sub(r"\s+", " ", nombre_raw.strip())

        # Extraer el nombre principal antes del primer "/"
        if "/" in nombre:
            nombre = nombre.split("/")[0].strip()

        # Remover indicadores de turno al final
        nombre = re.sub(r"\s+(TM|TN|TT)$", "", nombre)
        nombre = re.sub(r"\s+(Turno\s+\w+)$", "", nombre, flags=re.IGNORECASE)
        nombre = re.sub(r"\s+(Labo\s+\w+)$", "", nombre, flags=re.IGNORECASE)

        return nombre.strip()

    def _extraer_horarios_estructurados(self, horarios_raw: str) -> Dict:
        """Extrae horarios estructurados del texto divididos por tipo de actividad"""
        horarios = {"teorica": "", "practica": "", "laboratorio": ""}

        if not horarios_raw or horarios_raw.strip() == "":
            return horarios

        # Dividir por tipos de actividad (Teórica:, Práctica:, Laboratorio:)
        # Patrón mejorado para capturar los diferentes tipos
        patron_actividades = (
            r"\b(Teórica|Práctica|Laboratorio|Teórico-práctico|Teórico/Práctica)\s*:\s*"
        )

        # Dividir el texto por los tipos de actividad
        partes = re.split(patron_actividades, horarios_raw, flags=re.IGNORECASE)

        if len(partes) == 1:
            # No hay tipos específicos, colocar todo en teórica
            horarios["teorica"] = horarios_raw.strip()
            return horarios

        # Procesar cada tipo de actividad encontrado
        i = 1  # Empezar desde 1 porque partes[0] es el texto antes del primer tipo
        while i < len(partes) - 1:
            tipo_actividad = partes[i].strip().lower()
            contenido_horario = partes[i + 1].strip()

            # Limpiar el contenido (remover <br> tags si existen)
            contenido_horario = re.sub(r"<br\s*/?>", " ", contenido_horario)
            contenido_horario = re.sub(r"\s+", " ", contenido_horario).strip()

            # Mapear el tipo de actividad a la columna correspondiente
            if tipo_actividad in ["teórica", "teorica"]:
                horarios["teorica"] = contenido_horario
            elif tipo_actividad in [
                "teórico-práctico",
                "teorico-practico",
                "teórico/práctica",
                "teorico/practica",
            ]:
                # Los tipos combinados van en teórica
                horarios["teorica"] = contenido_horario
            elif tipo_actividad in ["práctica", "practica"]:
                horarios["practica"] = contenido_horario
            elif tipo_actividad in ["laboratorio"]:
                horarios["laboratorio"] = contenido_horario

            i += 2  # Avanzar al siguiente tipo

        return horarios

    def _parsear_texto_horario(self, texto: str, tipo_actividad: str) -> List[Dict]:
        """Parsea texto de horario específico"""
        eventos = []

        # Patrón: "Jueves de 9 a 12 y de 13 a 16"
        match_doble = self.patrones_horarios["dia_doble_rango"].search(texto)
        if match_doble:
            dia, hora1_inicio, hora1_fin, hora2_inicio, hora2_fin = match_doble.groups()
            dia_normalizado = self._normalizar_dia(dia)

            if dia_normalizado:
                eventos.append(
                    {
                        "dia": dia_normalizado,
                        "hora_inicio": f"{int(hora1_inicio):02d}:00",
                        "hora_fin": f"{int(hora1_fin):02d}:00",
                        "tipo_actividad": tipo_actividad,
                    }
                )
                eventos.append(
                    {
                        "dia": dia_normalizado,
                        "hora_inicio": f"{int(hora2_inicio):02d}:00",
                        "hora_fin": f"{int(hora2_fin):02d}:00",
                        "tipo_actividad": tipo_actividad,
                    }
                )
            return eventos

        # Patrón: "Martes y Viernes de 9 a 11"
        match_dias = self.patrones_horarios["dias_rango"].search(texto)
        if match_dias:
            dias_texto, hora_inicio, hora_fin = match_dias.groups()
            dias = self._extraer_dias_multiples(dias_texto)

            for dia in dias:
                dia_normalizado = self._normalizar_dia(dia)
                if dia_normalizado:
                    eventos.append(
                        {
                            "dia": dia_normalizado,
                            "hora_inicio": f"{int(hora_inicio):02d}:00",
                            "hora_fin": f"{int(hora_fin):02d}:00",
                            "tipo_actividad": tipo_actividad,
                        }
                    )
            return eventos

        # Patrón: "Lunes de 17 a 22"
        match_dia = self.patrones_horarios["dia_rango"].search(texto)
        if match_dia:
            dia, hora_inicio, hora_fin = match_dia.groups()
            dia_normalizado = self._normalizar_dia(dia)

            if dia_normalizado:
                eventos.append(
                    {
                        "dia": dia_normalizado,
                        "hora_inicio": f"{int(hora_inicio):02d}:00",
                        "hora_fin": f"{int(hora_fin):02d}:00",
                        "tipo_actividad": tipo_actividad,
                    }
                )

        return eventos

    def _extraer_dias_multiples(self, texto_dias: str) -> List[str]:
        """Extrae múltiples días de un texto como 'Martes y Viernes'"""
        # Reemplazar conectores
        texto_limpio = texto_dias.replace(" y ", ",").replace(" e ", ",")
        dias = [dia.strip() for dia in texto_limpio.split(",")]
        return [dia for dia in dias if dia]

    def _normalizar_dia(self, dia: str) -> Optional[str]:
        """Normaliza un día de la semana"""
        dia_limpio = dia.lower().strip()
        return self.dias_normalizados.get(dia_limpio)

    def _extraer_profesores(self, profesores_raw: str) -> List[Dict]:
        """Extrae información de profesores"""
        if not profesores_raw or profesores_raw.strip() == "":
            return []

        profesores = []
        # Dividir por saltos de línea o nombres que empiecen con mayúscula
        nombres = re.split(r"\n+|(?=[A-Z][A-Z]+,)", profesores_raw)

        for nombre in nombres:
            nombre_limpio = nombre.strip()
            if nombre_limpio and len(nombre_limpio) > 2:
                profesores.append(
                    {
                        "nombre": nombre_limpio,
                        "rol": "profesor",  # Podríamos detectar roles específicos si hay patrones
                    }
                )

        return profesores

    def _generar_id_materia(self, nombre: str, periodo: str) -> str:
        """Genera ID único para una materia"""
        slug = re.sub(r"[^a-zA-Z0-9]", "_", nombre.lower())
        slug = re.sub(r"_+", "_", slug).strip("_")
        periodo_slug = periodo.lower().replace(" ", "_")
        return f"dc_horarios_{slug}_{periodo_slug}_{datetime.now().strftime('%Y%m%d')}"

    def validar_horarios_extraidos(self, materias_horarios: List[Dict]) -> Dict:
        """Valida los horarios extraídos con la nueva estructura"""
        stats_validacion = {
            "total_materias": len(materias_horarios),
            "materias_con_teorica": 0,
            "materias_con_practica": 0,
            "materias_con_laboratorio": 0,
            "materias_sin_horarios": 0,
            "tipos_horario_encontrados": {
                "teorica": 0,
                "practica": 0,
                "laboratorio": 0,
            },
            "errores_validacion": [],
        }

        for materia in materias_horarios:
            horarios = materia.get("horarios", {})

            tiene_horarios = False

            if horarios.get("teorica") and horarios["teorica"].strip():
                stats_validacion["materias_con_teorica"] += 1
                stats_validacion["tipos_horario_encontrados"]["teorica"] += 1
                tiene_horarios = True

            if horarios.get("practica") and horarios["practica"].strip():
                stats_validacion["materias_con_practica"] += 1
                stats_validacion["tipos_horario_encontrados"]["practica"] += 1
                tiene_horarios = True

            if horarios.get("laboratorio") and horarios["laboratorio"].strip():
                stats_validacion["materias_con_laboratorio"] += 1
                stats_validacion["tipos_horario_encontrados"]["laboratorio"] += 1
                tiene_horarios = True

            if not tiene_horarios:
                stats_validacion["materias_sin_horarios"] += 1
                stats_validacion["errores_validacion"].append(
                    f"Materia sin horarios: {materia.get('nombre', 'DESCONOCIDA')}"
                )

        return stats_validacion

    def guardar_horarios(
        self, materias_horarios: List[Dict], archivo_salida: str = None
    ) -> str:
        """Guarda los horarios extraídos"""
        if not archivo_salida:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_salida = f"horarios_dc_{timestamp}.json"

        # Preparar datos completos para guardar
        datos_completos = {
            "metadata": {
                "departamento": "DC",
                "fecha_extraccion": datetime.now().isoformat(),
                "total_materias": len(materias_horarios),
                "fuente": "https://www.dc.uba.ar/",
                "version_scraper": "1.0",
            },
            "estadisticas": self.stats,
            "horarios": materias_horarios,
        }

        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(datos_completos, f, ensure_ascii=False, indent=2)

        logger.info(f"Horarios guardados en: {archivo_salida}")
        return archivo_salida

    def ejecutar_scraping_completo(self) -> Dict:
        """Ejecuta el scraping completo de horarios DC"""
        logger.info("=== INICIANDO SCRAPING HORARIOS DC ===")

        try:
            # 1. Obtener HTML
            html = self.obtener_horarios_2c_2025()
            if not html:
                raise Exception("No se pudo obtener el HTML de horarios")

            # 2. Extraer horarios
            materias_horarios = self.extraer_horarios_de_tabla(html)
            if not materias_horarios:
                raise Exception("No se pudieron extraer horarios de la tabla")

            # 3. Validar datos
            stats_validacion = self.validar_horarios_extraidos(materias_horarios)

            # 4. Guardar resultados
            archivo_horarios = self.guardar_horarios(materias_horarios)

            # 5. Preparar resultado
            resultado = {
                "exito": True,
                "archivo_generado": archivo_horarios,
                "estadisticas": self.stats,
                "validacion": stats_validacion,
                "materias_horarios": materias_horarios,
            }

            logger.info("=== SCRAPING DC COMPLETADO EXITOSAMENTE ===")
            return resultado

        except Exception as e:
            logger.error(f"Error en scraping DC: {e}")
            return {"exito": False, "error": str(e), "estadisticas": self.stats}


def main():
    """Función principal"""
    print("SCRAPER HORARIOS DEPARTAMENTO DE COMPUTACION")
    print("=" * 55)

    try:
        # Crear scraper
        scraper = ScraperHorariosDC()

        # Ejecutar scraping
        resultado = scraper.ejecutar_scraping_completo()

        if resultado["exito"]:
            stats = resultado["estadisticas"]
            validacion = resultado["validacion"]

            print("\nSCRAPING COMPLETADO EXITOSAMENTE!")
            print(f"Archivo generado: {resultado['archivo_generado']}")

            print("\nESTADISTICAS:")
            print(f"   - Materias procesadas: {stats['materias_procesadas']}")
            print(f"   - Horarios extraidos: {stats['horarios_extraidos']}")
            print(f"   - Errores de parsing: {stats['errores_parsing']}")

            print("\nVALIDACION:")
            print(f"   - Total materias: {validacion['total_materias']}")
            print(f"   - Con horarios: {validacion['materias_con_horarios']}")
            print(f"   - Eventos de horario: {validacion['total_eventos_horario']}")
            print(f"   - Dias cubiertos: {', '.join(validacion['dias_cubiertos'])}")

            if validacion["errores_validacion"]:
                print("\nADVERTENCIAS:")
                for error in validacion["errores_validacion"][:3]:
                    print(f"   - {error}")

            print("\nHorarios reales de DC extraidos exitosamente!")

        else:
            print(f"\nERROR EN SCRAPING: {resultado['error']}")
            return 1

        return 0

    except Exception as e:
        print(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
