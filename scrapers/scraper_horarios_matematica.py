#!/usr/bin/env python3
"""
Scraper de Horarios - Departamento de Matemática
Extrae horarios reales de materias del Depto de Matemática desde su sitio web

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


class ScraperHorariosMat:
    """Scraper especializado para horarios del Departamento de Matemática"""

    def __init__(self):
        self.base_url = "https://web.dm.uba.ar/"
        self.url_horarios = "https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=2"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # Patrones regex para parsing de horarios
        self.patrones_horarios = {
            # "Ma y Vi: 9 a 11"
            "dias_dos_rango": re.compile(
                r"(\w+)\s+y\s+(\w+):\s*(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)",
                re.IGNORECASE,
            ),
            # "Lu y Ju: 17:30 a 19:30"
            "dias_dos_rango_minutos": re.compile(
                r"(\w+)\s+y\s+(\w+):\s*(\d{1,2}:\d{2})\s+a\s+(\d{1,2}:\d{2})",
                re.IGNORECASE,
            ),
            # "Ju: 9 a 13"
            "dia_simple_rango": re.compile(
                r"(\w+):\s*(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)",
                re.IGNORECASE,
            ),
            # "Ma: 14 a 19"
            "dia_simple_rango_largo": re.compile(
                r"(\w+):\s*(\d{1,2})\s+a\s+(\d{1,2})",
                re.IGNORECASE,
            ),
        }

        # Mapeo de días abreviados
        self.dias_normalizados = {
            "lu": "lunes",
            "ma": "martes", 
            "mi": "miércoles",
            "ju": "jueves",
            "vi": "viernes",
            "sa": "sábado",
            "do": "domingo",
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

        # Mapeo de tipos de clases
        self.tipos_clase = {
            "fondoT": "teorica",
            "fondoP": "practica", 
            "fondoL": "laboratorio",
            "fondoA": "teorico_practico"
        }

        # Estadísticas
        self.stats = {
            "materias_procesadas": 0,
            "comisiones_extraidas": 0,
            "errores_parsing": 0,
            "materias_encontradas": [],
            "errores": [],
        }

    def obtener_html_horarios(self) -> Optional[str]:
        """Obtiene el HTML de horarios de Matemática"""
        try:
            logger.info(f"Obteniendo horarios de: {self.url_horarios}")
            response = self.session.get(self.url_horarios, timeout=30)
            response.raise_for_status()

            # Verificar que la página contenga las tablas de horarios
            indicadores = ["<table class=\"horarios\">", "caption>", "diayhora"]
            texto_contenido = response.text.lower()
            
            encontrado = any(indicador.lower() in texto_contenido for indicador in indicadores)
            if not encontrado:
                logger.error("La página no contiene las tablas de horarios esperadas")
                return None

            logger.info(f"HTML obtenido exitosamente ({len(response.text)} caracteres)")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Error al obtener HTML: {e}")
            return None

    def extraer_horarios_de_html(self, html: str) -> List[Dict]:
        """Extrae horarios del HTML de Matemática"""
        soup = BeautifulSoup(html, "html.parser")
        materias_horarios = []

        # Buscar todas las tablas de horarios
        tablas = soup.find_all("table", class_="horarios")
        logger.info(f"Encontradas {len(tablas)} tablas de horarios")

        for tabla in tablas:
            try:
                materia_info = self._procesar_tabla_materia(tabla)
                if materia_info:
                    materias_horarios.append(materia_info)
                    self.stats["materias_procesadas"] += 1
                    self.stats["materias_encontradas"].append(materia_info["nombre"])
                    
                    if len(materias_horarios) <= 5:  # Debug: mostrar primeras 5
                        logger.info(f"Materia extraída: {materia_info['nombre']} ({len(materia_info['comisiones'])} comisiones)")
                        
            except Exception as e:
                logger.error(f"Error procesando tabla: {e}")
                self.stats["errores_parsing"] += 1

        logger.info(f"Extraídas {len(materias_horarios)} materias con horarios")
        return materias_horarios

    def _procesar_tabla_materia(self, tabla) -> Optional[Dict]:
        """Procesa una tabla de materia individual"""
        # Extraer nombre de materia del caption
        caption = tabla.find("caption")
        if not caption:
            return None
            
        nombre_materia = caption.get_text().strip()
        if not nombre_materia or len(nombre_materia) < 3:
            return None

        # Procesar todas las filas de comisiones
        comisiones = []
        filas = tabla.find_all("tr")
        
        for fila in filas:
            comision = self._procesar_fila_comision(fila)
            if comision:
                comisiones.append(comision)
                self.stats["comisiones_extraidas"] += 1

        if not comisiones:
            return None

        # Generar información de la materia
        materia_id = self._generar_id_materia(nombre_materia, "2C 2025")
        
        return {
            "id": materia_id,
            "nombre": self._normalizar_nombre_materia(nombre_materia),
            "nombre_original": nombre_materia,
            "periodo": {
                "cuatrimestre": "2",
                "año": 2025,
                "codigo": "2C 2025",
            },
            "departamento": {
                "codigo": "DM",
                "nombre": "Departamento de Matemática",
                "url_origen": "https://web.dm.uba.ar/",
            },
            "comisiones": comisiones,
            "metadata": {
                "fuente_url": self.url_horarios,
                "fecha_extraccion": datetime.now().isoformat(),
                "departamento": "DM",
                "confiabilidad": "alta",
                "tipo_dato": "horarios_reales",
            },
        }

    def _procesar_fila_comision(self, fila) -> Optional[Dict]:
        """Procesa una fila individual de comisión"""
        celdas = fila.find_all("td")
        if len(celdas) < 4:
            return None

        tipo_celda = celdas[0]
        horario_celda = celdas[1]
        docente_celda = celdas[2]
        aula_celda = celdas[3]

        # Extraer tipo de comisión
        tipo_clase = self._extraer_tipo_clase(tipo_celda)
        if not tipo_clase:
            return None

        # Extraer nombre de comisión
        nombre_comision = tipo_celda.get_text().strip()
        
        # Extraer horarios
        horarios_raw = horario_celda.get_text().strip()
        horarios_estructurados = self._extraer_horarios_estructurados(horarios_raw)

        # Extraer docentes
        docentes_raw = docente_celda.get_text().strip()
        docentes = self._extraer_docentes(docentes_raw)

        # Extraer aula
        aula_raw = aula_celda.get_text().strip()
        aula = aula_raw.replace("Aula:", "").strip() if aula_raw else ""

        return {
            "nombre": nombre_comision,
            "tipo": tipo_clase,
            "horarios": horarios_estructurados,
            "docentes": docentes,
            "aula": aula if aula else None,
            "horarios_raw": horarios_raw
        }

    def _extraer_tipo_clase(self, celda) -> Optional[str]:
        """Extrae el tipo de clase de la celda"""
        clases_css = celda.get("class", [])
        for clase in clases_css:
            if clase in self.tipos_clase:
                return self.tipos_clase[clase]
        return None

    def _extraer_horarios_estructurados(self, horarios_raw: str) -> List[Dict]:
        """Extrae horarios estructurados del texto"""
        if not horarios_raw or horarios_raw.strip() == "":
            return []

        eventos = []
        
        # Patrón: "Ma y Vi: 9 a 11" o "Lu y Ju: 17:30 a 19:30"
        match_dos_dias = self.patrones_horarios["dias_dos_rango"].search(horarios_raw)
        if not match_dos_dias:
            match_dos_dias = self.patrones_horarios["dias_dos_rango_minutos"].search(horarios_raw)
            
        if match_dos_dias:
            dia1, dia2, hora_inicio, hora_fin = match_dos_dias.groups()
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

        # Patrón: "Ju: 9 a 13" o "Ma: 14 a 19"
        match_un_dia = self.patrones_horarios["dia_simple_rango"].search(horarios_raw)
        if not match_un_dia:
            match_un_dia = self.patrones_horarios["dia_simple_rango_largo"].search(horarios_raw)
            
        if match_un_dia:
            dia, hora_inicio, hora_fin = match_un_dia.groups()
            dia_norm = self._normalizar_dia(dia)
            hora_inicio_norm = self._normalizar_hora(hora_inicio)
            hora_fin_norm = self._normalizar_hora(hora_fin)
            
            if dia_norm and hora_inicio_norm and hora_fin_norm:
                eventos.append({
                    "dia": dia_norm,
                    "hora_inicio": hora_inicio_norm,
                    "hora_fin": hora_fin_norm
                })

        return eventos

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
        # Dividir por separadores comunes
        nombres = re.split(r"\s*-\s*|\s*,\s*", docentes_raw.strip())
        
        for nombre in nombres:
            nombre_limpio = nombre.strip()
            if nombre_limpio and len(nombre_limpio) > 2:
                docentes.append({
                    "nombre": nombre_limpio,
                    "rol": "profesor"
                })

        return docentes

    def _normalizar_nombre_materia(self, nombre_raw: str) -> str:
        """Normaliza el nombre de una materia"""
        # Limpiar espacios múltiples
        nombre = re.sub(r"\s+", " ", nombre_raw.strip())
        
        # Remover indicadores de modalidad al final
        nombre = re.sub(r"\s+\([^)]+\)$", "", nombre)
        nombre = re.sub(r"\s+-\s+[A-Z\s]+\([^)]+\)$", "", nombre)
        
        return nombre.strip()

    def _generar_id_materia(self, nombre: str, periodo: str) -> str:
        """Genera ID único para una materia"""
        slug = re.sub(r"[^a-zA-Z0-9]", "_", nombre.lower())
        slug = re.sub(r"_+", "_", slug).strip("_")
        periodo_slug = periodo.lower().replace(" ", "_")
        return f"dm_horarios_{slug}_{periodo_slug}_{datetime.now().strftime('%Y%m%d')}"

    def validar_horarios_extraidos(self, materias_horarios: List[Dict]) -> Dict:
        """Valida los horarios extraídos"""
        stats_validacion = {
            "total_materias": len(materias_horarios),
            "total_comisiones": 0,
            "comisiones_con_horarios": 0,
            "comisiones_sin_horarios": 0,
            "tipos_comision": {
                "teorica": 0,
                "practica": 0,
                "laboratorio": 0,
                "teorico_practico": 0
            },
            "dias_cubiertos": set(),
            "errores_validacion": [],
        }

        for materia in materias_horarios:
            comisiones = materia.get("comisiones", [])
            stats_validacion["total_comisiones"] += len(comisiones)
            
            for comision in comisiones:
                tipo_comision = comision.get("tipo", "")
                if tipo_comision in stats_validacion["tipos_comision"]:
                    stats_validacion["tipos_comision"][tipo_comision] += 1
                
                horarios = comision.get("horarios", [])
                if horarios:
                    stats_validacion["comisiones_con_horarios"] += 1
                    for horario in horarios:
                        dia = horario.get("dia")
                        if dia:
                            stats_validacion["dias_cubiertos"].add(dia)
                else:
                    stats_validacion["comisiones_sin_horarios"] += 1
                    stats_validacion["errores_validacion"].append(
                        f"Comisión sin horarios: {materia.get('nombre', 'DESCONOCIDA')} - {comision.get('nombre', 'SIN_NOMBRE')}"
                    )

        stats_validacion["dias_cubiertos"] = list(stats_validacion["dias_cubiertos"])
        return stats_validacion

    def guardar_horarios(self, materias_horarios: List[Dict], archivo_salida: str = None) -> str:
        """Guarda los horarios extraídos"""
        if not archivo_salida:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_salida = f"horarios_matematica_{timestamp}.json"

        # Preparar datos completos para guardar
        datos_completos = {
            "metadata": {
                "departamento": "DM",
                "fecha_extraccion": datetime.now().isoformat(),
                "total_materias": len(materias_horarios),
                "fuente": "https://web.dm.uba.ar/",
                "version_scraper": "1.0",
                "periodo": "2C 2025"
            },
            "estadisticas": self.stats,
            "horarios": materias_horarios,
        }

        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(datos_completos, f, ensure_ascii=False, indent=2)

        logger.info(f"Horarios guardados en: {archivo_salida}")
        return archivo_salida

    def ejecutar_scraping_completo(self) -> Dict:
        """Ejecuta el scraping completo de horarios de Matemática"""
        logger.info("=== INICIANDO SCRAPING HORARIOS MATEMÁTICA ===")

        try:
            # 1. Obtener HTML
            html = self.obtener_html_horarios()
            if not html:
                raise Exception("No se pudo obtener el HTML de horarios")

            # 2. Extraer horarios
            materias_horarios = self.extraer_horarios_de_html(html)
            if not materias_horarios:
                raise Exception("No se pudieron extraer horarios")

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

            logger.info("=== SCRAPING MATEMÁTICA COMPLETADO EXITOSAMENTE ===")
            return resultado

        except Exception as e:
            logger.error(f"Error en scraping Matemática: {e}")
            return {"exito": False, "error": str(e), "estadisticas": self.stats}


def main():
    """Función principal"""
    print("SCRAPER HORARIOS DEPARTAMENTO DE MATEMÁTICA")
    print("=" * 55)

    try:
        # Crear scraper
        scraper = ScraperHorariosMat()

        # Ejecutar scraping
        resultado = scraper.ejecutar_scraping_completo()

        if resultado["exito"]:
            stats = resultado["estadisticas"]
            validacion = resultado["validacion"]

            print("\nSCRAPING COMPLETADO EXITOSAMENTE!")
            print(f"Archivo generado: {resultado['archivo_generado']}")

            print("\nESTADISTICAS:")
            print(f"   - Materias procesadas: {stats['materias_procesadas']}")
            print(f"   - Comisiones extraídas: {stats['comisiones_extraidas']}")
            print(f"   - Errores de parsing: {stats['errores_parsing']}")

            print("\nVALIDACION:")
            print(f"   - Total materias: {validacion['total_materias']}")
            print(f"   - Total comisiones: {validacion['total_comisiones']}")
            print(f"   - Con horarios: {validacion['comisiones_con_horarios']}")
            print(f"   - Sin horarios: {validacion['comisiones_sin_horarios']}")
            print(f"   - Días cubiertos: {', '.join(validacion['dias_cubiertos'])}")

            print(f"\nTipos de comisiones:")
            for tipo, cantidad in validacion['tipos_comision'].items():
                print(f"   - {tipo}: {cantidad}")

            if validacion["errores_validacion"]:
                print(f"\nADVERTENCIAS ({len(validacion['errores_validacion'])}):")
                for error in validacion["errores_validacion"][:5]:
                    print(f"   - {error}")

            print("\nHorarios de Matemática extraídos exitosamente!")

        else:
            print(f"\nERROR EN SCRAPING: {resultado['error']}")
            return 1

        return 0

    except Exception as e:
        print(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit(main())