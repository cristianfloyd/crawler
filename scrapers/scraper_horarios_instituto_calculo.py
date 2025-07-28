#!/usr/bin/env python3
"""
Scraper de Horarios - Instituto de Cálculo
Extrae horarios reales de materias del Instituto de Cálculo desde su sitio web

Autor: Sistema RAG MVP
Fecha: 2025-07-27
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


class ScraperHorariosIC:
    """Scraper especializado para horarios del Instituto de Cálculo"""

    def __init__(self):
        self.base_url = "https://ic.fcen.uba.ar/"
        self.url_materias = "https://ic.fcen.uba.ar/actividades-academicas/formacion/materias"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Patrones regex para parsing de horarios
        self.patrones_horarios = {
            # "Lunes y jueves de 12 a 16"
            "dos_dias_rango": re.compile(
                r"(\w+)\s+y\s+(\w+)\s+de\s+(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)",
                re.IGNORECASE,
            ),
            # "Miércoles de 9 a 13"
            "un_dia_rango": re.compile(
                r"(\w+)\s+de\s+(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)",
                re.IGNORECASE,
            ),
            # "Sábados de 9 a 14"
            "dia_plural_rango": re.compile(
                r"(\w+s)\s+de\s+(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)",
                re.IGNORECASE,
            ),
            # "Martes (aula 1108) y viernes (aula 1109) de 14 a 17"
            "dos_dias_aulas_rango": re.compile(
                r"(\w+)\s+\([^)]+\)\s+y\s+(\w+)\s+\([^)]+\)\s+de\s+(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)",
                re.IGNORECASE,
            ),
            # "viernes de 9 a 15 h"
            "dia_con_h": re.compile(
                r"(\w+)\s+de\s+(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)\s*h",
                re.IGNORECASE,
            ),
        }

        # Mapeo de días normalizados
        self.dias_normalizados = {
            "lunes": "lunes",
            "martes": "martes", 
            "miércoles": "miércoles",
            "miercoles": "miércoles",
            "jueves": "jueves",
            "viernes": "viernes",
            "sábados": "sábado",
            "sabados": "sábado",
            "sábado": "sábado",
            "sabado": "sábado",
            "domingo": "domingo",
        }

        # Estadísticas
        self.stats = {
            "materias_procesadas": 0,
            "materias_con_horarios": 0,
            "materias_sin_horarios": 0,
            "errores_parsing": 0,
            "materias_encontradas": [],
            "errores": [],
        }

    def obtener_html_materias(self) -> Optional[str]:
        """Obtiene el HTML de materias del Instituto de Cálculo"""
        try:
            logger.info(f"Obteniendo materias de: {self.url_materias}")
            response = self.session.get(self.url_materias, timeout=30)
            response.raise_for_status()

            # Verificar que la página contenga las materias
            indicadores = ["academicitem", "academictitle", "dateicon"]
            texto_contenido = response.text.lower()
            
            encontrado = any(indicador.lower() in texto_contenido for indicador in indicadores)
            if not encontrado:
                logger.error("La página no contiene las materias esperadas")
                return None

            logger.info(f"HTML obtenido exitosamente ({len(response.text)} caracteres)")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Error al obtener HTML: {e}")
            return None

    def extraer_materias_de_html(self, html: str) -> List[Dict]:
        """Extrae materias del HTML del Instituto de Cálculo"""
        soup = BeautifulSoup(html, "html.parser")
        materias_horarios = []

        # Buscar todas las materias (academicitem)
        materias = soup.find_all("a", class_="academicitem")
        logger.info(f"Encontradas {len(materias)} materias")

        for materia in materias:
            try:
                materia_info = self._procesar_materia_individual(materia)
                if materia_info:
                    materias_horarios.append(materia_info)
                    self.stats["materias_procesadas"] += 1
                    self.stats["materias_encontradas"].append(materia_info["nombre"])
                    
                    if materia_info["horarios"]:
                        self.stats["materias_con_horarios"] += 1
                    else:
                        self.stats["materias_sin_horarios"] += 1
                    
                    if len(materias_horarios) <= 5:  # Debug: mostrar primeras 5
                        logger.info(f"Materia extraída: {materia_info['nombre']}")
                        
            except Exception as e:
                logger.error(f"Error procesando materia: {e}")
                self.stats["errores_parsing"] += 1

        logger.info(f"Extraídas {len(materias_horarios)} materias")
        return materias_horarios

    def _procesar_materia_individual(self, materia_elem) -> Optional[Dict]:
        """Procesa una materia individual"""
        # Extraer título
        titulo_elem = materia_elem.find("div", class_="academictitle")
        if not titulo_elem:
            return None
            
        nombre_materia = titulo_elem.get_text().strip()
        if not nombre_materia or len(nombre_materia) < 3:
            return None

        # Extraer horarios - buscar el div que contiene "dateicon"
        horario_elem = materia_elem.find("div", class_=lambda x: x and "academicinfo" in x and "dateicon" in x)
        horarios_raw = horario_elem.get_text().strip() if horario_elem else ""
        horarios_estructurados = self._extraer_horarios_estructurados(horarios_raw)

        # Extraer docentes - buscar el div que contiene "teachericon"
        docente_elem = materia_elem.find("div", class_=lambda x: x and "academicinfo" in x and "teachericon" in x)
        docentes_raw = docente_elem.get_text().strip() if docente_elem else ""
        docentes = self._extraer_docentes(docentes_raw)

        # Extraer información de período
        periodo_info = self._extraer_periodo_info(nombre_materia)

        # Generar ID único
        materia_id = self._generar_id_materia(nombre_materia, periodo_info["codigo"])
        
        return {
            "id": materia_id,
            "nombre": self._normalizar_nombre_materia(nombre_materia),
            "nombre_original": nombre_materia,
            "periodo": periodo_info,
            "departamento": {
                "codigo": "IC",
                "nombre": "Instituto de Cálculo",
                "url_origen": "https://ic.fcen.uba.ar/",
            },
            "horarios": horarios_estructurados,
            "docentes": docentes,
            "metadata": {
                "fuente_url": self.url_materias,
                "fecha_extraccion": datetime.now().isoformat(),
                "departamento": "IC",
                "confiabilidad": "alta",
                "tipo_dato": "horarios_reales",
                "horarios_raw": horarios_raw,
            },
        }

    def _extraer_horarios_estructurados(self, horarios_raw: str) -> List[Dict]:
        """Extrae horarios estructurados del texto"""
        if not horarios_raw or horarios_raw.strip() == "":
            return []

        eventos = []
        
        # Intentar cada patrón en orden de especificidad
        
        # Patrón: "Martes (aula 1108) y viernes (aula 1109) de 14 a 17"
        match = self.patrones_horarios["dos_dias_aulas_rango"].search(horarios_raw)
        if match:
            dia1, dia2, hora_inicio, hora_fin = match.groups()
            return self._crear_eventos_dos_dias(dia1, dia2, hora_inicio, hora_fin)

        # Patrón: "Lunes y jueves de 12 a 16"
        match = self.patrones_horarios["dos_dias_rango"].search(horarios_raw)
        if match:
            dia1, dia2, hora_inicio, hora_fin = match.groups()
            return self._crear_eventos_dos_dias(dia1, dia2, hora_inicio, hora_fin)

        # Patrón: "viernes de 9 a 15 h"
        match = self.patrones_horarios["dia_con_h"].search(horarios_raw)
        if match:
            dia, hora_inicio, hora_fin = match.groups()
            return self._crear_evento_un_dia(dia, hora_inicio, hora_fin)

        # Patrón: "Sábados de 9 a 14"
        match = self.patrones_horarios["dia_plural_rango"].search(horarios_raw)
        if match:
            dia_plural, hora_inicio, hora_fin = match.groups()
            # Convertir plural a singular
            dia = dia_plural.rstrip('s')
            return self._crear_evento_un_dia(dia, hora_inicio, hora_fin)

        # Patrón: "Miércoles de 9 a 13"
        match = self.patrones_horarios["un_dia_rango"].search(horarios_raw)
        if match:
            dia, hora_inicio, hora_fin = match.groups()
            return self._crear_evento_un_dia(dia, hora_inicio, hora_fin)

        return eventos

    def _crear_eventos_dos_dias(self, dia1: str, dia2: str, hora_inicio: str, hora_fin: str) -> List[Dict]:
        """Crea eventos para dos días"""
        eventos = []
        
        dia1_norm = self._normalizar_dia(dia1)
        dia2_norm = self._normalizar_dia(dia2)
        hora_inicio_norm = self._normalizar_hora(hora_inicio)
        hora_fin_norm = self._normalizar_hora(hora_fin)
        
        if dia1_norm and hora_inicio_norm and hora_fin_norm:
            eventos.append({
                "dia": dia1_norm,
                "hora_inicio": hora_inicio_norm,
                "hora_fin": hora_fin_norm
            })
        
        if dia2_norm and hora_inicio_norm and hora_fin_norm:
            eventos.append({
                "dia": dia2_norm,
                "hora_inicio": hora_inicio_norm,
                "hora_fin": hora_fin_norm
            })
        
        return eventos

    def _crear_evento_un_dia(self, dia: str, hora_inicio: str, hora_fin: str) -> List[Dict]:
        """Crea evento para un día"""
        dia_norm = self._normalizar_dia(dia)
        hora_inicio_norm = self._normalizar_hora(hora_inicio)
        hora_fin_norm = self._normalizar_hora(hora_fin)
        
        if dia_norm and hora_inicio_norm and hora_fin_norm:
            return [{
                "dia": dia_norm,
                "hora_inicio": hora_inicio_norm,
                "hora_fin": hora_fin_norm
            }]
        
        return []

    def _normalizar_dia(self, dia: str) -> Optional[str]:
        """Normaliza un día de la semana"""
        dia_limpio = dia.lower().strip()
        return self.dias_normalizados.get(dia_limpio)

    def _normalizar_hora(self, hora: str) -> str:
        """Normaliza una hora al formato HH:MM"""
        hora = hora.strip()
        if ":" in hora:
            return hora  # Ya está en formato HH:MM
        else:
            return f"{int(hora):02d}:00"  # Convertir de H a HH:00

    def _extraer_docentes(self, docentes_raw: str) -> List[Dict]:
        """Extrae información de docentes"""
        if not docentes_raw or docentes_raw.strip() == "":
            return []

        docentes = []
        
        # Limpiar texto
        texto_limpio = docentes_raw.replace("(Auxiliares:", ", Auxiliares:")
        texto_limpio = texto_limpio.replace("(Auxiliar:", ", Auxiliar:")
        texto_limpio = re.sub(r"[()]", "", texto_limpio)
        
        # Dividir por separadores comunes
        nombres = re.split(r"\s*[,;]\s*|(?:Auxiliares?:\s*)", texto_limpio)
        
        for nombre in nombres:
            nombre_limpio = nombre.strip()
            if nombre_limpio and len(nombre_limpio) > 2 and "auxiliar" not in nombre_limpio.lower():
                # Determinar rol
                rol = "auxiliar" if any(keyword in docentes_raw.lower() for keyword in ["auxiliar", "auxiliares"]) else "profesor"
                
                docentes.append({
                    "nombre": nombre_limpio,
                    "rol": rol
                })

        return docentes

    def _extraer_periodo_info(self, nombre_materia: str) -> Dict:
        """Extrae información de período del nombre de la materia"""
        # Buscar patrones de período en el nombre
        patrones_periodo = [
            r"(\d+)(?:er|do)\s+cuatrimestre\s+(\d{4})",
            r"(\d+)(?:er|to)\s+bimestre\s+(\d{4})",
            r"(\d{4})"  # Solo año
        ]
        
        for patron in patrones_periodo:
            match = re.search(patron, nombre_materia, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    numero, año = match.groups()
                    if "cuatrimestre" in nombre_materia.lower():
                        return {
                            "cuatrimestre": numero,
                            "año": int(año),
                            "codigo": f"{numero}C {año}"
                        }
                    elif "bimestre" in nombre_materia.lower():
                        return {
                            "bimestre": numero,
                            "año": int(año),
                            "codigo": f"{numero}B {año}"
                        }
                else:
                    año = match.group(1)
                    return {
                        "año": int(año),
                        "codigo": año
                    }
        
        # Período por defecto
        return {
            "año": 2025,
            "codigo": "2025"
        }

    def _normalizar_nombre_materia(self, nombre_raw: str) -> str:
        """Normaliza el nombre de una materia"""
        # Limpiar espacios múltiples
        nombre = re.sub(r"\s+", " ", nombre_raw.strip())
        
        # Remover información de período al final
        nombre = re.sub(r"\s+\d+(?:er|do|to)\s+(?:cuatrimestre|bimestre)\s+\d{4}$", "", nombre, flags=re.IGNORECASE)
        nombre = re.sub(r"\s+\d{4}$", "", nombre)
        
        # Remover indicadores de carrera al final entre paréntesis
        nombre = re.sub(r"\s+\([^)]*\)$", "", nombre)
        
        return nombre.strip()

    def _generar_id_materia(self, nombre: str, periodo: str) -> str:
        """Genera ID único para una materia"""
        slug = re.sub(r"[^a-zA-Z0-9]", "_", nombre.lower())
        slug = re.sub(r"_+", "_", slug).strip("_")
        periodo_slug = periodo.lower().replace(" ", "_")
        return f"ic_horarios_{slug}_{periodo_slug}_{datetime.now().strftime('%Y%m%d')}"

    def validar_materias_extraidas(self, materias_horarios: List[Dict]) -> Dict:
        """Valida las materias extraídas"""
        stats_validacion = {
            "total_materias": len(materias_horarios),
            "materias_con_horarios": 0,
            "materias_sin_horarios": 0,
            "total_eventos_horario": 0,
            "dias_cubiertos": set(),
            "tipos_periodo": {},
            "errores_validacion": [],
        }

        for materia in materias_horarios:
            horarios = materia.get("horarios", [])
            
            if horarios:
                stats_validacion["materias_con_horarios"] += 1
                stats_validacion["total_eventos_horario"] += len(horarios)
                
                for horario in horarios:
                    dia = horario.get("dia")
                    if dia:
                        stats_validacion["dias_cubiertos"].add(dia)
            else:
                stats_validacion["materias_sin_horarios"] += 1
                stats_validacion["errores_validacion"].append(
                    f"Materia sin horarios: {materia.get('nombre', 'DESCONOCIDA')}"
                )
            
            # Contar tipos de período
            periodo_codigo = materia.get("periodo", {}).get("codigo", "DESCONOCIDO")
            if periodo_codigo not in stats_validacion["tipos_periodo"]:
                stats_validacion["tipos_periodo"][periodo_codigo] = 0
            stats_validacion["tipos_periodo"][periodo_codigo] += 1

        stats_validacion["dias_cubiertos"] = list(stats_validacion["dias_cubiertos"])
        return stats_validacion

    def guardar_materias(self, materias_horarios: List[Dict], archivo_salida: str = None) -> str:
        """Guarda las materias extraídas"""
        if not archivo_salida:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_salida = f"horarios_instituto_calculo_{timestamp}.json"

        # Preparar datos completos para guardar
        datos_completos = {
            "metadata": {
                "departamento": "IC",
                "fecha_extraccion": datetime.now().isoformat(),
                "total_materias": len(materias_horarios),
                "fuente": "https://ic.fcen.uba.ar/",
                "version_scraper": "1.0",
            },
            "estadisticas": self.stats,
            "horarios": materias_horarios,
        }

        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(datos_completos, f, ensure_ascii=False, indent=2)

        logger.info(f"Materias guardadas en: {archivo_salida}")
        return archivo_salida

    def ejecutar_scraping_completo(self) -> Dict:
        """Ejecuta el scraping completo de materias del Instituto de Cálculo"""
        logger.info("=== INICIANDO SCRAPING INSTITUTO DE CÁLCULO ===")

        try:
            # 1. Obtener HTML
            html = self.obtener_html_materias()
            if not html:
                raise Exception("No se pudo obtener el HTML de materias")

            # 2. Extraer materias
            materias_horarios = self.extraer_materias_de_html(html)
            if not materias_horarios:
                raise Exception("No se pudieron extraer materias")

            # 3. Validar datos
            stats_validacion = self.validar_materias_extraidas(materias_horarios)

            # 4. Guardar resultados
            archivo_materias = self.guardar_materias(materias_horarios)

            # 5. Preparar resultado
            resultado = {
                "exito": True,
                "archivo_generado": archivo_materias,
                "estadisticas": self.stats,
                "validacion": stats_validacion,
                "materias_horarios": materias_horarios,
            }

            logger.info("=== SCRAPING INSTITUTO DE CÁLCULO COMPLETADO EXITOSAMENTE ===")
            return resultado

        except Exception as e:
            logger.error(f"Error en scraping Instituto de Cálculo: {e}")
            return {"exito": False, "error": str(e), "estadisticas": self.stats}


def main():
    """Función principal"""
    print("SCRAPER HORARIOS INSTITUTO DE CÁLCULO")
    print("=" * 55)

    try:
        # Crear scraper
        scraper = ScraperHorariosIC()

        # Ejecutar scraping
        resultado = scraper.ejecutar_scraping_completo()

        if resultado["exito"]:
            stats = resultado["estadisticas"]
            validacion = resultado["validacion"]

            print("\nSCRAPING COMPLETADO EXITOSAMENTE!")
            print(f"Archivo generado: {resultado['archivo_generado']}")

            print("\nESTADISTICAS:")
            print(f"   - Materias procesadas: {stats['materias_procesadas']}")
            print(f"   - Con horarios: {stats['materias_con_horarios']}")
            print(f"   - Sin horarios: {stats['materias_sin_horarios']}")
            print(f"   - Errores de parsing: {stats['errores_parsing']}")

            print("\nVALIDACION:")
            print(f"   - Total materias: {validacion['total_materias']}")
            print(f"   - Con horarios: {validacion['materias_con_horarios']}")
            print(f"   - Sin horarios: {validacion['materias_sin_horarios']}")
            print(f"   - Eventos de horario: {validacion['total_eventos_horario']}")
            print(f"   - Días cubiertos: {', '.join(validacion['dias_cubiertos'])}")

            print(f"\nTipos de período:")
            for periodo, cantidad in validacion['tipos_periodo'].items():
                print(f"   - {periodo}: {cantidad} materias")

            if validacion["errores_validacion"]:
                print(f"\nADVERTENCIAS ({len(validacion['errores_validacion'])}):")
                for error in validacion["errores_validacion"][:5]:
                    print(f"   - {error}")

            print("\nMaterias del Instituto de Cálculo extraídas exitosamente!")

        else:
            print(f"\nERROR EN SCRAPING: {resultado['error']}")
            return 1

        return 0

    except Exception as e:
        print(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit(main())