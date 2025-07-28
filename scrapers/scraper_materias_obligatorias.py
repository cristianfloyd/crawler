#!/usr/bin/env python3
"""
Scraper para Materias Obligatorias - Licenciatura en Datos
Extrae información de https://lcd.exactas.uba.ar/materias-obligatorias/

Autor: Sistema RAG MVP
Fecha: 2025-07-26
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
import time
from urllib.parse import urljoin

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScraperMateriasObligatorias:
    """Scraper especializado para materias obligatorias de LCD"""
    
    def __init__(self):
        self.base_url = "https://lcd.exactas.uba.ar/materias-obligatorias/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Mapeo de departamentos a códigos
        self.departamentos_map = {
            "Departamento de Matemática": "DM",
            "Departamento de Computación": "DC",
            "Departamento de Física": "DF", 
            "Instituto de Cálculo": "IC",
            "Departamento de Fisiología, Biología Molecular y Celular": "FB",
            "Departamento de Ciencias de la Atmósfera y los Océanos": "AT",
            "Departamento de Química Inorgánica, Analítica y Química Física": "QI"
        }
        
        # Mapeo de períodos
        self.periodos_map = {
            "Verano 2025": {"año": 2025, "cuatrimestre": "verano"},
            "1er cuatrimestre 2025": {"año": 2025, "cuatrimestre": "1"},
            "2do cuatrimestre 2025": {"año": 2025, "cuatrimestre": "2"}
        }
    
    def obtener_html(self) -> Optional[str]:
        """Obtiene el HTML de la página de materias obligatorias"""
        try:
            logger.info(f"Obteniendo HTML de: {self.base_url}")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            # Verificar que es la página correcta
            if "Materias Obligatorias" not in response.text:
                logger.error("La página no contiene el título esperado")
                return None
                
            logger.info(f"HTML obtenido exitosamente ({len(response.text)} caracteres)")
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener HTML: {e}")
            return None
    
    def extraer_materias_por_periodo(self, html: str) -> Dict[str, List[Dict]]:
        """Extrae materias organizadas por período académico"""
        soup = BeautifulSoup(html, 'html.parser')
        materias_por_periodo = {}
        
        # Buscar todas las secciones con h2 (períodos)
        secciones = soup.find_all('h2')
        
        for seccion in secciones:
            titulo_periodo = seccion.get_text().strip()
            
            # Filtrar solo períodos válidos de 2025
            if "2025" not in titulo_periodo:
                continue
                
            logger.info(f"Procesando período: {titulo_periodo}")
            
            # Buscar la tabla que sigue al h2
            tabla = seccion.find_next('table', class_='table')
            if not tabla:
                logger.warning(f"No se encontró tabla para período: {titulo_periodo}")
                continue
            
            materias = self._extraer_materias_de_tabla(tabla, titulo_periodo)
            materias_por_periodo[titulo_periodo] = materias
            
            logger.info(f"Extraídas {len(materias)} materias para {titulo_periodo}")
        
        return materias_por_periodo
    
    def _extraer_materias_de_tabla(self, tabla, periodo: str) -> List[Dict]:
        """Extrae materias de una tabla HTML específica"""
        materias = []
        filas = tabla.find_all('tr')[1:]  # Saltar header
        
        for i, fila in enumerate(filas):
            try:
                celdas = fila.find_all('td')
                if len(celdas) < 3:
                    continue
                
                nombre_raw = celdas[0].get_text().strip()
                departamento_raw = celdas[1].get_text().strip()
                
                # Extraer URL del link
                link_element = celdas[2].find('a')
                url_horarios = link_element.get('href') if link_element else None
                
                # Crear objeto materia
                materia = self._crear_objeto_materia(
                    nombre_raw, departamento_raw, periodo, url_horarios, i
                )
                
                if materia:
                    materias.append(materia)
                    
            except Exception as e:
                logger.error(f"Error procesando fila {i} en {periodo}: {e}")
                continue
        
        return materias
    
    def _crear_objeto_materia(self, nombre_raw: str, departamento_raw: str, 
                            periodo: str, url_horarios: Optional[str], index: int) -> Optional[Dict]:
        """Crea un objeto materia estructurado"""
        try:
            # Limpiar y normalizar nombre
            nombre_limpio = self._limpiar_nombre_materia(nombre_raw)
            
            # Identificar tipo de materia
            tipo_materia = self._identificar_tipo_materia(nombre_raw)
            
            # Mapear departamento
            codigo_dept = self._mapear_departamento(departamento_raw)
            
            # Obtener información del período
            info_periodo = self.periodos_map.get(periodo, {})
            
            # Generar ID único
            materia_id = self._generar_id(nombre_limpio, info_periodo, index)
            
            # Procesar URL de horarios
            url_horarios_completa = self._procesar_url_horarios(url_horarios)
            
            materia = {
                "id": materia_id,
                "nombre": nombre_limpio,
                "nombre_original": nombre_raw,
                "tipo": tipo_materia,
                "departamento": {
                    "nombre": departamento_raw,
                    "codigo": codigo_dept,
                    "url_horarios": url_horarios_completa
                },
                "periodo": {
                    "año": info_periodo.get("año", 2025),
                    "cuatrimestre": info_periodo.get("cuatrimestre", "1"),
                    "periodo_completo": periodo
                },
                "horarios": {
                    "clases": [],
                    "consultas": [],
                    "examenes": {}
                },
                "correlativas": {
                    "para_cursar": [],
                    "para_rendir": []
                },
                "docentes": [],
                "creditos": None,
                "carga_horaria": {},
                "programa": {
                    "url": None,
                    "temas": []
                },
                "metadata": {
                    "fuente_url": self.base_url,
                    "fecha_scraping": datetime.now().isoformat(),
                    "version": "2025.1",
                    "confiabilidad": "alta",
                    "requiere_enriquecimiento": True
                }
            }
            
            return materia
            
        except Exception as e:
            logger.error(f"Error creando objeto materia para '{nombre_raw}': {e}")
            return None
    
    def _limpiar_nombre_materia(self, nombre_raw: str) -> str:
        """Limpia y normaliza el nombre de la materia"""
        # Eliminar espacios extra
        nombre = re.sub(r'\s+', ' ', nombre_raw.strip())
        
        # Eliminar texto entre paréntesis al final (especificaciones de carrera)
        nombre = re.sub(r'\s*\([^)]*\)\s*$', '', nombre)
        
        # Eliminar indicadores de equivalencia
        nombre = re.sub(r'\s*-\s*Electiva.*$', '', nombre)
        nombre = re.sub(r'\s*-\s*solicitar equivalencia.*$', '', nombre, flags=re.IGNORECASE)
        
        return nombre.strip()
    
    def _identificar_tipo_materia(self, nombre_raw: str) -> str:
        """Identifica el tipo de materia basado en el nombre"""
        nombre_lower = nombre_raw.lower()
        
        if "electiva" in nombre_lower:
            return "electiva"
        elif "tesis" in nombre_lower:
            return "tesis"
        else:
            return "obligatoria"
    
    def _mapear_departamento(self, departamento_raw: str) -> Optional[str]:
        """Mapea el nombre del departamento a su código"""
        # Buscar coincidencia exacta
        if departamento_raw in self.departamentos_map:
            return self.departamentos_map[departamento_raw]
        
        # Buscar coincidencia parcial
        for dept_nombre, codigo in self.departamentos_map.items():
            if dept_nombre.lower() in departamento_raw.lower():
                return codigo
        
        logger.warning(f"Departamento no mapeado: {departamento_raw}")
        return None
    
    def _generar_id(self, nombre: str, periodo: Dict, index: int) -> str:
        """Genera un ID único para la materia"""
        # Crear slug del nombre
        slug = re.sub(r'[^a-zA-Z0-9]', '_', nombre.lower())
        slug = re.sub(r'_+', '_', slug).strip('_')
        
        año = periodo.get("año", 2025)
        cuatri = periodo.get("cuatrimestre", "1")
        
        return f"lcd_obligatoria_{slug}_{año}_{cuatri}_{index:02d}"
    
    def _procesar_url_horarios(self, url_raw: Optional[str]) -> Optional[str]:
        """Procesa y valida URL de horarios"""
        if not url_raw:
            return None
        
        # Si es URL relativa, convertir a absoluta
        if url_raw.startswith('/'):
            url_completa = urljoin("https://lcd.exactas.uba.ar", url_raw)
        elif url_raw.startswith('http'):
            url_completa = url_raw
        else:
            url_completa = urljoin(self.base_url, url_raw)
        
        return url_completa
    
    def validar_materias_extraidas(self, materias_por_periodo: Dict) -> Dict[str, any]:
        """Valida la calidad de los datos extraídos"""
        total_materias = sum(len(materias) for materias in materias_por_periodo.values())
        
        stats = {
            "total_materias": total_materias,
            "total_periodos": len(materias_por_periodo),
            "periodos_detectados": list(materias_por_periodo.keys()),
            "materias_por_periodo": {p: len(m) for p, m in materias_por_periodo.items()},
            "departamentos_unicos": set(),
            "tipos_materia": {"obligatoria": 0, "electiva": 0, "tesis": 0},
            "urls_horarios": {"con_url": 0, "sin_url": 0},
            "errores": []
        }
        
        # Análisis detallado
        for periodo, materias in materias_por_periodo.items():
            for materia in materias:
                # Departamentos
                if materia.get("departamento", {}).get("codigo"):
                    stats["departamentos_unicos"].add(materia["departamento"]["codigo"])
                
                # Tipos
                tipo = materia.get("tipo", "desconocido")
                if tipo in stats["tipos_materia"]:
                    stats["tipos_materia"][tipo] += 1
                
                # URLs
                if materia.get("departamento", {}).get("url_horarios"):
                    stats["urls_horarios"]["con_url"] += 1
                else:
                    stats["urls_horarios"]["sin_url"] += 1
                
                # Validaciones
                if not materia.get("nombre"):
                    stats["errores"].append(f"Materia sin nombre en {periodo}")
        
        stats["departamentos_unicos"] = list(stats["departamentos_unicos"])
        return stats
    
    def guardar_resultados(self, materias_por_periodo: Dict, stats: Dict):
        """Guarda los resultados en archivos JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar materias estructuradas
        archivo_materias = f"materias_obligatorias_{timestamp}.json"
        with open(archivo_materias, 'w', encoding='utf-8') as f:
            json.dump(materias_por_periodo, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Materias guardadas en: {archivo_materias}")
        
        # Guardar estadísticas
        archivo_stats = f"stats_obligatorias_{timestamp}.json"
        with open(archivo_stats, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Estadísticas guardadas en: {archivo_stats}")
        
        return archivo_materias, archivo_stats
    
    def ejecutar_scraping_completo(self) -> bool:
        """Ejecuta el proceso completo de scraping"""
        logger.info("=== INICIANDO SCRAPING MATERIAS OBLIGATORIAS ===")
        
        try:
            # 1. Obtener HTML
            html = self.obtener_html()
            if not html:
                logger.error("No se pudo obtener el HTML")
                return False
            
            # 2. Extraer materias
            materias_por_periodo = self.extraer_materias_por_periodo(html)
            if not materias_por_periodo:
                logger.error("No se extrajeron materias")
                return False
            
            # 3. Validar datos
            stats = self.validar_materias_extraidas(materias_por_periodo)
            
            # 4. Mostrar resumen
            logger.info(f"=== RESUMEN DE EXTRACCIÓN ===")
            logger.info(f"Total materias: {stats['total_materias']}")
            logger.info(f"Períodos: {stats['total_periodos']}")
            logger.info(f"Departamentos: {len(stats['departamentos_unicos'])}")
            logger.info(f"URLs con horarios: {stats['urls_horarios']['con_url']}")
            
            # 5. Guardar resultados
            archivo_materias, archivo_stats = self.guardar_resultados(materias_por_periodo, stats)
            
            logger.info("=== SCRAPING COMPLETADO EXITOSAMENTE ===")
            return True
            
        except Exception as e:
            logger.error(f"Error en scraping completo: {e}")
            return False

def main():
    """Función principal"""
    scraper = ScraperMateriasObligatorias()
    
    print("🕷️  SCRAPER MATERIAS OBLIGATORIAS - LCD")
    print("=====================================")
    
    exito = scraper.ejecutar_scraping_completo()
    
    if exito:
        print("\n✅ Scraping completado exitosamente!")
        print("📁 Revisa los archivos JSON generados")
    else:
        print("\n❌ Error en el scraping")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())