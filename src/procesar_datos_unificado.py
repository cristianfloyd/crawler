#!/usr/bin/env python3
"""
Procesador Unificado de Datos de Horarios - Día 3
Limpieza, normalización y estructuración para RAG MVP

Procesa datos de:
- Departamento de Computación (DC)
- Departamento de Matemática (DM) 
- Instituto de Cálculo (IC)

Autor: Sistema RAG MVP
Fecha: 2025-07-27
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
from collections import defaultdict, Counter
from pathlib import Path
import unicodedata

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcesadorDatosUnificado:
    """Procesador unificado para datos de horarios de múltiples departamentos"""
    
    def __init__(self):
        # Archivos fuente
        self.archivos_fuente = {
            "DC": "horarios_dc_20250727_020723.json",
            "DM": "horarios_matematica_20250727_023346.json", 
            "IC": "horarios_instituto_calculo_20250727_024931.json"
        }
        
        # Estadísticas globales
        self.stats = {
            "total_materias": 0,
            "materias_por_departamento": {},
            "materias_con_horarios": 0,
            "materias_sin_horarios": 0,
            "horarios_normalizados": 0,
            "docentes_extraidos": 0,
            "duplicados_detectados": 0,
            "nombres_normalizados": 0,
            "errores_procesamiento": 0
        }
        
        # Datos procesados
        self.materias_unificadas = []
        self.duplicados_encontrados = []
        self.errores = []

    def cargar_datos_fuente(self) -> Dict[str, Dict]:
        """Carga todos los archivos JSON de los departamentos"""
        datos_fuente = {}
        
        for dept, archivo in self.archivos_fuente.items():
            try:
                logger.info(f"Cargando datos de {dept}: {archivo}")
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    datos_fuente[dept] = datos
                    
                    # Actualizar estadísticas
                    if 'horarios' in datos:
                        materias = datos['horarios']
                    elif 'materias_horarios' in datos:
                        materias = datos['materias_horarios']
                    else:
                        materias = datos.get('materias', [])
                    
                    cantidad = len(materias)
                    self.stats["materias_por_departamento"][dept] = cantidad
                    self.stats["total_materias"] += cantidad
                    
                    logger.info(f"✅ {dept}: {cantidad} materias cargadas")
                    
            except FileNotFoundError:
                logger.error(f"❌ Archivo no encontrado: {archivo}")
                self.errores.append(f"Archivo no encontrado: {archivo}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error JSON en {archivo}: {e}")
                self.errores.append(f"Error JSON en {archivo}: {e}")
        
        return datos_fuente

    def normalizar_materia_dc(self, materia: Dict) -> Dict:
        """Normaliza una materia del Departamento de Computación"""
        horarios_normalizados = []
        
        # DC tiene estructura de horarios por tipo (teorica, practica, laboratorio)
        if 'horarios' in materia and isinstance(materia['horarios'], dict):
            for tipo, contenido in materia['horarios'].items():
                if contenido and contenido.strip():
                    # Extraer horarios del texto
                    eventos = self._extraer_horarios_de_texto(contenido, tipo)
                    horarios_normalizados.extend(eventos)
        
        # Extraer docentes
        docentes_normalizados = []
        if 'docentes' in materia:
            docentes_normalizados = materia['docentes']
        
        return {
            "id": materia.get('id', ''),
            "nombre": materia.get('nombre', ''),
            "nombre_original": materia.get('nombre_original', ''),
            "nombre_normalizado": self._normalizar_nombre_sin_acentos(materia.get('nombre', '')),
            "departamento": {
                "codigo": "DC",
                "nombre": "Departamento de Computación",
                "url_origen": "https://www.dc.uba.ar/"
            },
            "periodo": materia.get('periodo', {}),
            "horarios": horarios_normalizados,
            "docentes": docentes_normalizados,
            "metadata": {
                **materia.get('metadata', {}),
                "fuente_original": "scraper_dc",
                "procesado": datetime.now().isoformat()
            }
        }

    def normalizar_materia_dm(self, materia: Dict) -> Dict:
        """Normaliza una materia del Departamento de Matemática"""
        horarios_normalizados = []
        docentes_normalizados = []
        
        # DM tiene estructura de comisiones
        if 'comisiones' in materia:
            for comision in materia['comisiones']:
                # Extraer horarios de cada comisión
                if 'horarios' in comision:
                    for horario in comision['horarios']:
                        horarios_normalizados.append({
                            "dia": horario.get('dia', ''),
                            "hora_inicio": horario.get('hora_inicio', ''),
                            "hora_fin": horario.get('hora_fin', ''),
                            "tipo_actividad": comision.get('tipo', 'general'),
                            "comision": comision.get('nombre', ''),
                            "aula": comision.get('aula', '')
                        })
                
                # Extraer docentes de cada comisión
                if 'docentes' in comision:
                    for docente in comision['docentes']:
                        if docente not in docentes_normalizados:
                            docentes_normalizados.append(docente)
        
        return {
            "id": materia.get('id', ''),
            "nombre": materia.get('nombre', ''),
            "nombre_original": materia.get('nombre_original', ''),
            "nombre_normalizado": self._normalizar_nombre_sin_acentos(materia.get('nombre', '')),
            "departamento": {
                "codigo": "DM", 
                "nombre": "Departamento de Matemática",
                "url_origen": "https://web.dm.uba.ar/"
            },
            "periodo": materia.get('periodo', {}),
            "horarios": horarios_normalizados,
            "docentes": docentes_normalizados,
            "metadata": {
                **materia.get('metadata', {}),
                "fuente_original": "scraper_dm",
                "procesado": datetime.now().isoformat()
            }
        }

    def normalizar_materia_ic(self, materia: Dict) -> Dict:
        """Normaliza una materia del Instituto de Cálculo"""
        horarios_normalizados = []
        
        # IC tiene horarios directamente como lista
        if 'horarios' in materia and isinstance(materia['horarios'], list):
            for horario in materia['horarios']:
                horarios_normalizados.append({
                    "dia": horario.get('dia', ''),
                    "hora_inicio": horario.get('hora_inicio', ''),
                    "hora_fin": horario.get('hora_fin', ''),
                    "tipo_actividad": "general",
                    "comision": "",
                    "aula": ""
                })
        
        return {
            "id": materia.get('id', ''),
            "nombre": materia.get('nombre', ''),
            "nombre_original": materia.get('nombre_original', ''),
            "nombre_normalizado": self._normalizar_nombre_sin_acentos(materia.get('nombre', '')),
            "departamento": {
                "codigo": "IC",
                "nombre": "Instituto de Cálculo", 
                "url_origen": "https://ic.fcen.uba.ar/"
            },
            "periodo": materia.get('periodo', {}),
            "horarios": horarios_normalizados,
            "docentes": materia.get('docentes', []),
            "metadata": {
                **materia.get('metadata', {}),
                "fuente_original": "scraper_ic",
                "procesado": datetime.now().isoformat()
            }
        }

    def _extraer_horarios_de_texto(self, texto: str, tipo_actividad: str = "general") -> List[Dict]:
        """Extrae horarios de texto libre (para DC)"""
        eventos = []
        
        # Patrones comunes de horarios
        patrones = [
            r'(\w+)\s+(?:y\s+(\w+)\s+)?de\s+(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)',
            r'(\w+)\s*:\s*(\d{1,2}(?::\d{2})?)\s+a\s+(\d{1,2}(?::\d{2})?)'
        ]
        
        for patron in patrones:
            matches = re.finditer(patron, texto, re.IGNORECASE)
            for match in matches:
                grupos = match.groups()
                if len(grupos) >= 3:
                    dia1 = self._normalizar_dia(grupos[0])
                    if dia1:
                        hora_inicio = self._normalizar_hora(grupos[-2])
                        hora_fin = self._normalizar_hora(grupos[-1])
                        
                        eventos.append({
                            "dia": dia1,
                            "hora_inicio": hora_inicio,
                            "hora_fin": hora_fin,
                            "tipo_actividad": tipo_actividad,
                            "comision": "",
                            "aula": ""
                        })
                        
                        # Si hay segundo día
                        if len(grupos) >= 4 and grupos[1]:
                            dia2 = self._normalizar_dia(grupos[1])
                            if dia2:
                                eventos.append({
                                    "dia": dia2,
                                    "hora_inicio": hora_inicio,
                                    "hora_fin": hora_fin,
                                    "tipo_actividad": tipo_actividad,
                                    "comision": "",
                                    "aula": ""
                                })
        
        return eventos

    def _normalizar_dia(self, dia: str) -> Optional[str]:
        """Normaliza un día de la semana"""
        if not dia:
            return None
            
        dia_limpio = dia.lower().strip()
        
        # Mapeo de días
        mapeo_dias = {
            'lunes': 'lunes', 'lu': 'lunes', 'l': 'lunes',
            'martes': 'martes', 'ma': 'martes', 'mar': 'martes',
            'miércoles': 'miércoles', 'miercoles': 'miércoles', 'mi': 'miércoles', 'mie': 'miércoles',
            'jueves': 'jueves', 'ju': 'jueves', 'jue': 'jueves',
            'viernes': 'viernes', 'vi': 'viernes', 'vie': 'viernes', 
            'sábado': 'sábado', 'sabado': 'sábado', 'sa': 'sábado', 'sab': 'sábado',
            'domingo': 'domingo', 'do': 'domingo', 'dom': 'domingo'
        }
        
        return mapeo_dias.get(dia_limpio)

    def _normalizar_hora(self, hora: str) -> str:
        """Normaliza una hora al formato HH:MM"""
        if not hora:
            return ""
            
        hora = hora.strip()
        if ':' in hora:
            return hora
        else:
            try:
                return f"{int(hora):02d}:00"
            except ValueError:
                return hora

    def detectar_duplicados(self, materias: List[Dict]) -> List[Dict]:
        """Detecta posibles materias duplicadas entre departamentos"""
        duplicados = []
        nombres_vistos = defaultdict(list)
        
        # Agrupar por nombres similares
        for i, materia in enumerate(materias):
            nombre_normalizado = self._normalizar_nombre_para_comparacion(materia['nombre'])
            nombres_vistos[nombre_normalizado].append((i, materia))
        
        # Identificar duplicados
        for nombre, materias_grupo in nombres_vistos.items():
            if len(materias_grupo) > 1:
                duplicados.append({
                    "nombre_normalizado": nombre,
                    "materias": materias_grupo,
                    "cantidad": len(materias_grupo)
                })
                self.stats["duplicados_detectados"] += len(materias_grupo) - 1
        
        return duplicados

    def _normalizar_nombre_sin_acentos(self, nombre: str) -> str:
        """Normaliza nombre eliminando acentos, ñ y caracteres especiales"""
        if not nombre:
            return ""
        
        # Convertir a minúsculas
        nombre = nombre.lower()
        
        # Remover acentos y normalizar caracteres Unicode
        nombre = unicodedata.normalize('NFD', nombre)
        nombre = ''.join(char for char in nombre if unicodedata.category(char) != 'Mn')
        
        # Reemplazar ñ por n
        nombre = nombre.replace('ñ', 'n')
        
        # Mantener solo letras, números y espacios
        nombre = re.sub(r'[^a-z0-9\s]', ' ', nombre)
        
        # Normalizar espacios múltiples
        nombre = re.sub(r'\s+', ' ', nombre).strip()
        
        return nombre

    def _normalizar_nombre_para_comparacion(self, nombre: str) -> str:
        """Normaliza nombre de materia para detección de duplicados"""
        # Aplicar normalización sin acentos
        nombre = self._normalizar_nombre_sin_acentos(nombre)
        
        # Remover palabras comunes que causan ruido
        palabras_ruido = ['i', 'ii', 'iii', 'iv', '1', '2', '3', '4', 'a', 'b', 'c']
        palabras = nombre.split()
        palabras_filtradas = [p for p in palabras if p not in palabras_ruido]
        
        return ' '.join(palabras_filtradas)

    def procesar_todos_los_datos(self) -> Dict:
        """Procesamiento principal: carga, normaliza y unifica todos los datos"""
        logger.info("=== INICIANDO PROCESAMIENTO UNIFICADO ===")
        
        # 1. Cargar datos fuente
        datos_fuente = self.cargar_datos_fuente()
        if not datos_fuente:
            logger.error("No se pudieron cargar datos fuente")
            return {"exito": False, "error": "No hay datos fuente"}
        
        # 2. Procesar cada departamento
        materias_procesadas = []
        
        for dept, datos in datos_fuente.items():
            logger.info(f"Procesando departamento: {dept}")
            
            # Obtener lista de materias según estructura
            if 'horarios' in datos:
                materias = datos['horarios']
            elif 'materias_horarios' in datos:
                materias = datos['materias_horarios']
            else:
                materias = datos.get('materias', [])
            
            # Normalizar según departamento
            for materia in materias:
                try:
                    if dept == "DC":
                        materia_normalizada = self.normalizar_materia_dc(materia)
                    elif dept == "DM":
                        materia_normalizada = self.normalizar_materia_dm(materia)
                    elif dept == "IC":
                        materia_normalizada = self.normalizar_materia_ic(materia)
                    else:
                        continue
                    
                    materias_procesadas.append(materia_normalizada)
                    
                    # Contar horarios y docentes
                    if materia_normalizada['horarios']:
                        self.stats["materias_con_horarios"] += 1
                        self.stats["horarios_normalizados"] += len(materia_normalizada['horarios'])
                    else:
                        self.stats["materias_sin_horarios"] += 1
                    
                    self.stats["docentes_extraidos"] += len(materia_normalizada['docentes'])
                    
                    # Contar nombres normalizados
                    if materia_normalizada.get('nombre_normalizado'):
                        self.stats["nombres_normalizados"] += 1
                    
                except Exception as e:
                    logger.error(f"Error procesando materia en {dept}: {e}")
                    self.stats["errores_procesamiento"] += 1
                    self.errores.append(f"{dept}: {str(e)}")
        
        # 3. Detectar duplicados
        logger.info("Detectando duplicados...")
        self.duplicados_encontrados = self.detectar_duplicados(materias_procesadas)
        
        # 4. Guardar resultados
        self.materias_unificadas = materias_procesadas
        archivo_salida = self.guardar_datos_procesados()
        
        # 5. Generar resultado
        resultado = {
            "exito": True,
            "archivo_generado": archivo_salida,
            "estadisticas": self.stats,
            "duplicados": self.duplicados_encontrados,
            "errores": self.errores,
            "materias_procesadas": len(materias_procesadas)
        }
        
        logger.info("=== PROCESAMIENTO COMPLETADO ===")
        return resultado

    def guardar_datos_procesados(self) -> str:
        """Guarda los datos procesados y unificados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = f"materias_unificadas_{timestamp}.json"
        
        datos_salida = {
            "metadata": {
                "fecha_procesamiento": datetime.now().isoformat(),
                "total_materias": len(self.materias_unificadas),
                "departamentos_procesados": list(self.archivos_fuente.keys()),
                "version_procesador": "1.0"
            },
            "estadisticas": self.stats,
            "duplicados_detectados": self.duplicados_encontrados,
            "errores": self.errores,
            "materias": self.materias_unificadas
        }
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos_salida, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Datos guardados en: {archivo_salida}")
        return archivo_salida

    def generar_reporte_procesamiento(self) -> str:
        """Genera un reporte detallado del procesamiento"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_reporte = f"reporte_procesamiento_{timestamp}.md"
        
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            f.write(f"# Reporte de Procesamiento de Datos\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## Estadísticas Generales\n\n")
            f.write(f"- **Total materias procesadas:** {self.stats['total_materias']}\n")
            f.write(f"- **Materias con horarios:** {self.stats['materias_con_horarios']}\n")
            f.write(f"- **Materias sin horarios:** {self.stats['materias_sin_horarios']}\n")
            f.write(f"- **Horarios normalizados:** {self.stats['horarios_normalizados']}\n")
            f.write(f"- **Docentes extraídos:** {self.stats['docentes_extraidos']}\n")
            f.write(f"- **Nombres normalizados:** {self.stats['nombres_normalizados']}\n")
            f.write(f"- **Duplicados detectados:** {self.stats['duplicados_detectados']}\n")
            f.write(f"- **Errores de procesamiento:** {self.stats['errores_procesamiento']}\n\n")
            
            f.write(f"## Por Departamento\n\n")
            for dept, cantidad in self.stats['materias_por_departamento'].items():
                f.write(f"- **{dept}:** {cantidad} materias\n")
            
            if self.duplicados_encontrados:
                f.write(f"\n## Duplicados Detectados\n\n")
                for dup in self.duplicados_encontrados:
                    f.write(f"- **{dup['nombre_normalizado']}:** {dup['cantidad']} versiones\n")
            
            if self.errores:
                f.write(f"\n## Errores\n\n")
                for error in self.errores:
                    f.write(f"- {error}\n")
        
        logger.info(f"Reporte guardado en: {archivo_reporte}")
        return archivo_reporte


def main():
    """Función principal"""
    print("PROCESADOR UNIFICADO DE DATOS DE HORARIOS")
    print("=" * 55)
    
    try:
        procesador = ProcesadorDatosUnificado()
        resultado = procesador.procesar_todos_los_datos()
        
        if resultado["exito"]:
            print("\n✅ PROCESAMIENTO COMPLETADO EXITOSAMENTE!")
            print(f"📁 Archivo generado: {resultado['archivo_generado']}")
            
            stats = resultado["estadisticas"]
            print(f"\n📊 ESTADÍSTICAS:")
            print(f"   - Total materias: {stats['total_materias']}")
            print(f"   - Con horarios: {stats['materias_con_horarios']}")
            print(f"   - Sin horarios: {stats['materias_sin_horarios']}")
            print(f"   - Horarios normalizados: {stats['horarios_normalizados']}")
            print(f"   - Docentes extraídos: {stats['docentes_extraidos']}")
            print(f"   - Nombres normalizados: {stats['nombres_normalizados']}")
            print(f"   - Duplicados detectados: {stats['duplicados_detectados']}")
            
            print(f"\n🏢 POR DEPARTAMENTO:")
            for dept, cantidad in stats['materias_por_departamento'].items():
                print(f"   - {dept}: {cantidad} materias")
            
            if resultado["duplicados"]:
                print(f"\n⚠️  DUPLICADOS DETECTADOS:")
                for dup in resultado["duplicados"][:5]:  # Mostrar primeros 5
                    print(f"   - '{dup['nombre_normalizado']}': {dup['cantidad']} versiones")
            
            # Generar reporte
            archivo_reporte = procesador.generar_reporte_procesamiento()
            print(f"\n📋 Reporte detallado: {archivo_reporte}")
            
        else:
            print(f"\n❌ ERROR EN PROCESAMIENTO: {resultado['error']}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit(main())