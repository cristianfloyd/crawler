#!/usr/bin/env python3
"""
Procesador de Datos y Horarios - Día 3.1
Limpieza y normalización de datos para MVP RAG

Autor: Sistema RAG MVP
Fecha: 2025-07-26
"""

import json
import re
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple, Set
import logging
from collections import defaultdict
import difflib

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcesadorDatosHorarios:
    """Procesador para limpieza y normalización de datos de horarios"""
    
    def __init__(self):
        # Mapeos de normalización
        self.dias_normalizados = {
            # Versiones completas
            "lunes": "lunes", "martes": "martes", "miércoles": "miércoles", 
            "miercoles": "miércoles", "jueves": "jueves", "viernes": "viernes", 
            "sábado": "sábado", "sabado": "sábado", "domingo": "domingo",
            
            # Abreviaciones comunes
            "lun": "lunes", "lu": "lunes", "l": "lunes",
            "mar": "martes", "ma": "martes", "k": "martes",
            "mié": "miércoles", "mie": "miércoles", "mi": "miércoles", "m": "miércoles",
            "jue": "jueves", "ju": "jueves", "j": "jueves",
            "vie": "viernes", "vi": "viernes", "v": "viernes",
            "sáb": "sábado", "sab": "sábado", "sa": "sábado", "s": "sábado",
            "dom": "domingo", "do": "domingo", "d": "domingo",
            
            # Versiones en inglés (por si aparecen)
            "monday": "lunes", "tuesday": "martes", "wednesday": "miércoles",
            "thursday": "jueves", "friday": "viernes", "saturday": "sábado", "sunday": "domingo"
        }
        
        # Patrones regex para horarios
        self.patrones_horarios = {
            # Formato HH:MM - HH:MM
            "rango_completo": re.compile(r"(\d{1,2}):(\d{2})\s*[-–—]\s*(\d{1,2}):(\d{2})"),
            # Formato HH - HH (sin minutos)
            "rango_simple": re.compile(r"(\d{1,2})\s*[-–—]\s*(\d{1,2})"),
            # Formato HH:MM
            "hora_simple": re.compile(r"(\d{1,2}):(\d{2})"),
            # Formato de 24hs con texto
            "hora_con_texto": re.compile(r"(\d{1,2}):(\d{2})\s*(hs?|horas?)?"),
            # Formatos de mañana/tarde/noche
            "modalidad_tiempo": re.compile(r"(mañana|tarde|noche|vespertino|matutino)", re.IGNORECASE)
        }
        
        # Patrones para aulas
        self.patrones_aulas = {
            "pabellon": re.compile(r"pab(?:ellón|ellon)?\s*(\d+)", re.IGNORECASE),
            "aula": re.compile(r"aula\s*(\d+)", re.IGNORECASE),
            "laboratorio": re.compile(r"lab(?:oratorio)?\s*(\w+)", re.IGNORECASE),
            "salon": re.compile(r"sal(?:ón|on)?\s*(\w+)", re.IGNORECASE)
        }
        
        # Sinónimos de materias para detectar duplicados
        self.sinonimos_materias = {
            "algoritmos": ["algo", "algorit", "algoritm", "alg"],
            "estructuras": ["estruct", "estr", "struct"],
            "datos": ["data", "dat"],
            "análisis": ["analisis", "anal", "anál"],
            "álgebra": ["algebra", "alg", "álg"],
            "matemática": ["matematica", "mat", "matem"],
            "estadística": ["estadistica", "estad", "est"],
            "probabilidad": ["prob", "proba"],
            "computación": ["computacion", "comp", "comput"],
            "introducción": ["introduccion", "intro", "intr"]
        }
        
        # Estadísticas de procesamiento
        self.stats = {
            "materias_procesadas": 0,
            "duplicados_detectados": 0,
            "horarios_normalizados": 0,
            "dias_normalizados": 0,
            "nombres_normalizados": 0,
            "errores": []
        }
    
    def procesar_archivo_completo(self, archivo_materias: str) -> Dict:
        """Procesa un archivo completo de materias"""
        logger.info(f"Iniciando procesamiento de: {archivo_materias}")
        
        try:
            # Cargar datos
            with open(archivo_materias, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Procesar cada período
            datos_normalizados = {}
            todas_las_materias = []
            
            for periodo, materias in datos.items():
                logger.info(f"Procesando período: {periodo}")
                materias_normalizadas = []
                
                for materia in materias:
                    materia_normalizada = self.normalizar_materia(materia)
                    materias_normalizadas.append(materia_normalizada)
                    todas_las_materias.append(materia_normalizada)
                    self.stats["materias_procesadas"] += 1
                
                datos_normalizados[periodo] = materias_normalizadas
            
            # Detectar y resolver duplicados
            logger.info("Detectando duplicados...")
            datos_sin_duplicados = self.detectar_duplicados(datos_normalizados)
            
            # Validar integridad
            logger.info("Validando integridad...")
            reporte_integridad = self.validar_integridad(datos_sin_duplicados)
            
            # Preparar resultado final
            resultado = {
                "datos_normalizados": datos_sin_duplicados,
                "estadisticas": self.stats,
                "reporte_integridad": reporte_integridad,
                "metadata": {
                    "fecha_procesamiento": datetime.now().isoformat(),
                    "archivo_origen": archivo_materias,
                    "version_procesador": "3.1.0"
                }
            }
            
            logger.info("Procesamiento completado exitosamente")
            return resultado
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {e}")
            self.stats["errores"].append(str(e))
            raise
    
    def normalizar_materia(self, materia: Dict) -> Dict:
        """Normaliza una materia individual"""
        materia_normalizada = materia.copy()
        
        try:
            # 1. Normalizar nombre de materia
            nombre_normalizado = self.normalizar_nombre_materia(materia["nombre"])
            materia_normalizada["nombre_normalizado"] = nombre_normalizado
            
            # 2. Normalizar horarios (si existen)
            if materia.get("horarios"):
                horarios_normalizados = self.normalizar_horarios(materia["horarios"])
                materia_normalizada["horarios"] = horarios_normalizados
            
            # 3. Normalizar departamento
            departamento_normalizado = self.normalizar_departamento(materia["departamento"])
            materia_normalizada["departamento"] = departamento_normalizado
            
            # 4. Agregar palabras clave para búsqueda
            palabras_clave = self.generar_palabras_clave(materia_normalizada)
            materia_normalizada["palabras_clave"] = palabras_clave
            
            # 5. Agregar metadata de normalización
            materia_normalizada["normalizacion"] = {
                "fecha": datetime.now().isoformat(),
                "cambios_realizados": self._detectar_cambios(materia, materia_normalizada),
                "confiabilidad_normalizacion": "alta"
            }
            
            return materia_normalizada
            
        except Exception as e:
            logger.error(f"Error normalizando materia {materia.get('nombre', 'UNKNOWN')}: {e}")
            self.stats["errores"].append(f"Error en {materia.get('id', 'UNKNOWN')}: {str(e)}")
            return materia  # Devolver original si falla
    
    def normalizar_nombre_materia(self, nombre: str) -> str:
        """Normaliza el nombre de una materia"""
        if not nombre:
            return ""
        
        # Limpiar espacios y caracteres especiales
        nombre_limpio = re.sub(r'\s+', ' ', nombre.strip())
        
        # Normalizar acentos comunes
        nombre_limpio = nombre_limpio.replace('Análisis', 'Análisis')
        nombre_limpio = nombre_limpio.replace('Álgebra', 'Álgebra')
        nombre_limpio = nombre_limpio.replace('Introducción', 'Introducción')
        nombre_limpio = nombre_limpio.replace('Optimización', 'Optimización')
        
        # Normalizar numeración romana y arábiga
        nombre_limpio = re.sub(r'\bI\b', '1', nombre_limpio)
        nombre_limpio = re.sub(r'\bII\b', '2', nombre_limpio)
        nombre_limpio = re.sub(r'\bIII\b', '3', nombre_limpio)
        nombre_limpio = re.sub(r'\bIV\b', '4', nombre_limpio)
        
        # Capitalizar apropiadamente
        palabras = nombre_limpio.split()
        palabras_capitalizadas = []
        
        preposiciones = {'de', 'del', 'la', 'las', 'el', 'los', 'en', 'a', 'al', 'y', 'e', 'o', 'u'}
        
        for i, palabra in enumerate(palabras):
            if i == 0 or palabra.lower() not in preposiciones:
                palabras_capitalizadas.append(palabra.capitalize())
            else:
                palabras_capitalizadas.append(palabra.lower())
        
        self.stats["nombres_normalizados"] += 1
        return ' '.join(palabras_capitalizadas)
    
    def normalizar_horarios(self, horarios: Dict) -> Dict:
        """Normaliza información de horarios"""
        horarios_normalizados = {
            "clases": [],
            "consultas": [], 
            "examenes": {}
        }
        
        # Normalizar clases
        if horarios.get("clases"):
            for clase in horarios["clases"]:
                clase_normalizada = self.normalizar_evento_horario(clase)
                if clase_normalizada:
                    horarios_normalizados["clases"].append(clase_normalizada)
        
        # Normalizar consultas
        if horarios.get("consultas"):
            for consulta in horarios["consultas"]:
                consulta_normalizada = self.normalizar_evento_horario(consulta)
                if consulta_normalizada:
                    horarios_normalizados["consultas"].append(consulta_normalizada)
        
        # Normalizar exámenes
        if horarios.get("examenes"):
            examenes_normalizados = {}
            for tipo, fecha in horarios["examenes"].items():
                if fecha:
                    fecha_normalizada = self.normalizar_fecha(fecha)
                    if fecha_normalizada:
                        examenes_normalizados[tipo] = fecha_normalizada
            horarios_normalizados["examenes"] = examenes_normalizados
        
        if any(horarios_normalizados.values()):
            self.stats["horarios_normalizados"] += 1
        
        return horarios_normalizados
    
    def normalizar_evento_horario(self, evento: Dict) -> Optional[Dict]:
        """Normaliza un evento de horario (clase o consulta)"""
        if not evento:
            return None
        
        evento_normalizado = {}
        
        # Normalizar día
        if evento.get("dia"):
            dia_normalizado = self.normalizar_dia(evento["dia"])
            if dia_normalizado:
                evento_normalizado["dia"] = dia_normalizado
                self.stats["dias_normalizados"] += 1
        
        # Normalizar horas
        if evento.get("hora_inicio"):
            hora_inicio = self.normalizar_hora(evento["hora_inicio"])
            if hora_inicio:
                evento_normalizado["hora_inicio"] = hora_inicio
        
        if evento.get("hora_fin"):
            hora_fin = self.normalizar_hora(evento["hora_fin"])
            if hora_fin:
                evento_normalizado["hora_fin"] = hora_fin
        
        # Normalizar aula
        if evento.get("aula"):
            aula_normalizada = self.normalizar_aula(evento["aula"])
            evento_normalizado["aula"] = aula_normalizada
        
        # Copiar otros campos
        for campo in ["modalidad", "docente", "observaciones"]:
            if evento.get(campo):
                evento_normalizado[campo] = evento[campo]
        
        return evento_normalizado if evento_normalizado else None
    
    def normalizar_dia(self, dia: str) -> Optional[str]:
        """Normaliza un día de la semana"""
        if not dia:
            return None
        
        dia_limpio = dia.lower().strip()
        
        # Remover caracteres especiales
        dia_limpio = re.sub(r'[^\w\s]', '', dia_limpio)
        
        return self.dias_normalizados.get(dia_limpio)
    
    def normalizar_hora(self, hora: str) -> Optional[str]:
        """Normaliza una hora al formato HH:MM"""
        if not hora:
            return None
        
        hora_str = str(hora).strip()
        
        # Patrón HH:MM
        match = self.patrones_horarios["hora_simple"].search(hora_str)
        if match:
            horas, minutos = match.groups()
            horas = int(horas)
            minutos = int(minutos)
            
            # Validar rangos
            if 0 <= horas <= 23 and 0 <= minutos <= 59:
                return f"{horas:02d}:{minutos:02d}"
        
        # Patrón solo horas (asumir :00)
        match = re.search(r'^(\d{1,2})$', hora_str)
        if match:
            horas = int(match.group(1))
            if 0 <= horas <= 23:
                return f"{horas:02d}:00"
        
        return None
    
    def normalizar_aula(self, aula: str) -> str:
        """Normaliza información de aula"""
        if not aula:
            return ""
        
        aula_normalizada = aula.strip()
        
        # Normalizar pabellón
        match = self.patrones_aulas["pabellon"].search(aula_normalizada)
        if match:
            numero = match.group(1)
            aula_normalizada = re.sub(self.patrones_aulas["pabellon"], f"Pabellón {numero}", aula_normalizada)
        
        # Normalizar aula
        match = self.patrones_aulas["aula"].search(aula_normalizada)
        if match:
            numero = match.group(1)
            aula_normalizada = re.sub(self.patrones_aulas["aula"], f"Aula {numero}", aula_normalizada)
        
        return aula_normalizada
    
    def normalizar_fecha(self, fecha: str) -> Optional[str]:
        """Normaliza una fecha al formato ISO"""
        if not fecha:
            return None
        
        # Intentar parsear diferentes formatos
        formatos = [
            "%Y-%m-%d",
            "%d/%m/%Y", 
            "%d-%m-%Y",
            "%Y/%m/%d"
        ]
        
        for formato in formatos:
            try:
                fecha_obj = datetime.strptime(fecha, formato)
                return fecha_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return None
    
    def normalizar_departamento(self, departamento: Dict) -> Dict:
        """Normaliza información de departamento"""
        dept_normalizado = departamento.copy()
        
        # Normalizar nombre completo
        if dept_normalizado.get("nombre"):
            nombre = dept_normalizado["nombre"]
            # Eliminar redundancias
            nombre = re.sub(r'\s*,\s*', ', ', nombre)  # Espacios en comas
            dept_normalizado["nombre"] = nombre.strip()
        
        # Validar código de departamento
        if dept_normalizado.get("codigo"):
            codigo = dept_normalizado["codigo"].upper().strip()
            dept_normalizado["codigo"] = codigo
        
        return dept_normalizado
    
    def generar_palabras_clave(self, materia: Dict) -> List[str]:
        """Genera palabras clave para búsqueda"""
        palabras_clave = set()
        
        # Del nombre
        nombre = materia.get("nombre_normalizado", materia.get("nombre", ""))
        palabras_nombre = re.findall(r'\b\w{3,}\b', nombre.lower())
        palabras_clave.update(palabras_nombre)
        
        # Del departamento
        if materia.get("departamento", {}).get("codigo"):
            palabras_clave.add(materia["departamento"]["codigo"].lower())
        
        # Del tipo
        if materia.get("tipo"):
            palabras_clave.add(materia["tipo"])
        
        # De sinónimos
        for palabra in list(palabras_clave):
            for sinonimo_grupo, sinonimos in self.sinonimos_materias.items():
                if palabra in sinonimos or palabra == sinonimo_grupo:
                    palabras_clave.add(sinonimo_grupo)
                    palabras_clave.update(sinonimos)
        
        return sorted(list(palabras_clave))
    
    def detectar_duplicados(self, datos: Dict) -> Dict:
        """Detecta y resuelve duplicados entre períodos"""
        logger.info("Analizando duplicados...")
        
        # Agrupar materias por nombre normalizado
        materias_por_nombre = defaultdict(list)
        
        for periodo, materias in datos.items():
            for materia in materias:
                nombre_key = materia.get("nombre_normalizado", materia.get("nombre", "")).lower()
                materias_por_nombre[nombre_key].append((periodo, materia))
        
        # Identificar duplicados
        duplicados = {}
        for nombre, instancias in materias_por_nombre.items():
            if len(instancias) > 1:
                duplicados[nombre] = instancias
                self.stats["duplicados_detectados"] += 1
        
        # Resolver duplicados (mantener la más completa)
        datos_sin_duplicados = {}
        materias_procesadas = set()
        
        for periodo, materias in datos.items():
            materias_filtradas = []
            
            for materia in materias:
                materia_id = materia.get("id")
                if materia_id not in materias_procesadas:
                    # Verificar si es duplicado
                    nombre_key = materia.get("nombre_normalizado", materia.get("nombre", "")).lower()
                    
                    if nombre_key in duplicados:
                        # Seleccionar la mejor instancia
                        mejor_instancia = self._seleccionar_mejor_instancia(duplicados[nombre_key])
                        if mejor_instancia[1]["id"] == materia_id:
                            materias_filtradas.append(materia)
                            # Marcar todas las instancias como procesadas
                            for _, inst in duplicados[nombre_key]:
                                materias_procesadas.add(inst["id"])
                    else:
                        materias_filtradas.append(materia)
                        materias_procesadas.add(materia_id)
            
            datos_sin_duplicados[periodo] = materias_filtradas
        
        logger.info(f"Duplicados detectados y resueltos: {len(duplicados)}")
        return datos_sin_duplicados
    
    def _seleccionar_mejor_instancia(self, instancias: List[Tuple]) -> Tuple:
        """Selecciona la mejor instancia entre duplicados"""
        # Criteria: más información de horarios, más reciente, más completa
        mejor = instancias[0]
        mejor_score = self._calcular_score_completitud(mejor[1])
        
        for instancia in instancias[1:]:
            score = self._calcular_score_completitud(instancia[1])
            if score > mejor_score:
                mejor = instancia
                mejor_score = score
        
        return mejor
    
    def _calcular_score_completitud(self, materia: Dict) -> int:
        """Calcula score de completitud de una materia"""
        score = 0
        
        # Horarios
        if materia.get("horarios", {}).get("clases"):
            score += 3
        if materia.get("horarios", {}).get("consultas"):
            score += 2
        
        # Correlativas
        if materia.get("correlativas", {}).get("para_cursar"):
            score += 2
        
        # Docentes
        if materia.get("docentes"):
            score += 1
        
        # URL de horarios
        if materia.get("departamento", {}).get("url_horarios"):
            score += 1
        
        return score
    
    def _detectar_cambios(self, original: Dict, normalizado: Dict) -> List[str]:
        """Detecta qué cambios se realizaron durante la normalización"""
        cambios = []
        
        if original.get("nombre") != normalizado.get("nombre_normalizado"):
            cambios.append("nombre_normalizado")
        
        if original.get("horarios") != normalizado.get("horarios"):
            cambios.append("horarios_normalizados")
        
        if "palabras_clave" in normalizado:
            cambios.append("palabras_clave_generadas")
        
        return cambios
    
    def validar_integridad(self, datos: Dict) -> Dict:
        """Valida la integridad de los datos procesados"""
        reporte = {
            "total_materias": 0,
            "materias_con_horarios": 0,
            "materias_sin_horarios": 0,
            "departamentos_unicos": set(),
            "periodos_validos": 0,
            "errores_integridad": [],
            "warnings": []
        }
        
        for periodo, materias in datos.items():
            reporte["periodos_validos"] += 1
            
            for materia in materias:
                reporte["total_materias"] += 1
                
                # Verificar campos obligatorios
                if not materia.get("nombre") and not materia.get("nombre_normalizado"):
                    reporte["errores_integridad"].append(f"Materia sin nombre: {materia.get('id')}")
                
                if not materia.get("departamento", {}).get("codigo"):
                    reporte["warnings"].append(f"Materia sin código de departamento: {materia.get('id')}")
                else:
                    reporte["departamentos_unicos"].add(materia["departamento"]["codigo"])
                
                # Verificar horarios
                horarios = materia.get("horarios", {})
                if horarios.get("clases") or horarios.get("consultas"):
                    reporte["materias_con_horarios"] += 1
                else:
                    reporte["materias_sin_horarios"] += 1
        
        reporte["departamentos_unicos"] = list(reporte["departamentos_unicos"])
        return reporte
    
    def guardar_datos_normalizados(self, datos_procesados: Dict, archivo_salida: str):
        """Guarda los datos normalizados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not archivo_salida:
            archivo_salida = f"materias_normalizadas_{timestamp}.json"
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos_procesados, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Datos normalizados guardados en: {archivo_salida}")
        return archivo_salida

def main():
    """Función principal"""
    print("🔄 PROCESADOR DE DATOS Y HORARIOS - DÍA 3.1")
    print("=" * 50)
    
    # Archivo de entrada (ajustar según sea necesario)
    archivo_entrada = "materias_obligatorias_20250726_195319.json"
    
    try:
        # Crear procesador
        procesador = ProcesadorDatosHorarios()
        
        # Procesar datos
        print(f"📁 Procesando archivo: {archivo_entrada}")
        datos_procesados = procesador.procesar_archivo_completo(archivo_entrada)
        
        # Guardar resultados
        archivo_salida = procesador.guardar_datos_normalizados(
            datos_procesados, 
            "materias_normalizadas.json"
        )
        
        # Mostrar estadísticas
        stats = datos_procesados["estadisticas"]
        integridad = datos_procesados["reporte_integridad"]
        
        print("\n📊 ESTADÍSTICAS DE PROCESAMIENTO:")
        print(f"✅ Materias procesadas: {stats['materias_procesadas']}")
        print(f"✅ Nombres normalizados: {stats['nombres_normalizados']}")
        print(f"✅ Horarios normalizados: {stats['horarios_normalizados']}")
        print(f"✅ Días normalizados: {stats['dias_normalizados']}")
        print(f"⚠️  Duplicados detectados: {stats['duplicados_detectados']}")
        
        print("\n🔍 REPORTE DE INTEGRIDAD:")
        print(f"📚 Total materias: {integridad['total_materias']}")
        print(f"🕐 Con horarios: {integridad['materias_con_horarios']}")
        print(f"🏢 Departamentos: {len(integridad['departamentos_unicos'])}")
        print(f"❌ Errores: {len(integridad['errores_integridad'])}")
        
        if integridad['errores_integridad']:
            print("\n🚨 ERRORES DETECTADOS:")
            for error in integridad['errores_integridad'][:5]:  # Mostrar máximo 5
                print(f"   • {error}")
        
        print(f"\n✅ Datos normalizados guardados en: {archivo_salida}")
        print("🎉 Procesamiento completado exitosamente!")
        
        return 0
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {archivo_entrada}")
        print("💡 Asegúrate de que el archivo existe en el directorio actual")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())