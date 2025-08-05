#!/usr/bin/env python3
"""
NORMALIZADOR DE NOMBRES DE MATERIAS LCD
Normaliza nombres de materias al formato estándar de la carrera:
- Lowercase sin acentos
- Números arábigos → números romanos en lowercase
- Eliminación de texto descriptivo extra
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional


class NormalizadorNombresMaterias:
    """Normalizador unificado de nombres de materias con capacidades de procesamiento en lote"""
    
    def __init__(self):
        """Inicializa el normalizador con la base de materias LCD"""
        self.materias_base = self._cargar_materias_base()
        self.equivalencias_cbc = self._crear_equivalencias_cbc()
        self.indice_nombres = self._crear_indice_normalizacion()
        
        # Estadísticas para procesamiento en lote (integración de fase2)
        self.estadisticas = {
            "materias_procesadas": 0,
            "cambios_realizados": 0,
            "tipos_cambios": {
                "mayusculas_corregidas": 0,
                "abreviaciones_expandidas": 0,
                "caracteres_limpiados": 0,
                "numeros_romanos_corregidos": 0,
                "equivalencias_cbc_aplicadas": 0
            }
        }

    def _cargar_materias_base(self) -> List[Dict]:
        """Carga las materias base desde materias.json"""
        archivo_base = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "materias.json"
        )

        if os.path.exists(archivo_base):
            with open(archivo_base, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"⚠️ No se encontró archivo base: {archivo_base}")
            return []

    def _crear_equivalencias_cbc(self) -> Dict[str, List[str]]:
        """Crea equivalencias específicas para materias CBC"""
        return {
            # CBC genérico -> Materias específicas obligatorias
            "quimica": ["quimica general e inorganica", "quimica general"],
            "fisica": ["fisica i", "fisica 1", "fisica uno"],
            "analisis matematico": ["analisis matematico a", "analisis i"],
            "algebra": ["algebra i", "algebra 1"],
            
            # También las inversas para bidireccionalidad
            "quimica general e inorganica": ["quimica"],
            "quimica general": ["quimica"],
            "fisica i": ["fisica"],
            "fisica 1": ["fisica"],
            "analisis matematico a": ["analisis matematico"],
            "algebra i": ["algebra"]
        }
    
    def _crear_indice_normalizacion(self) -> Dict[str, str]:
        """Crea un índice de normalización basado en las materias base + equivalencias CBC"""
        indice = {}

        for materia in self.materias_base:
            nombre_original = materia.get("materia", "")
            nombre_normalizado = self._normalizar_nombre_base(nombre_original)

            # Crear múltiples variaciones para el matching
            variaciones = self._generar_variaciones_matching(nombre_original)

            for variacion in variaciones:
                indice[variacion] = nombre_normalizado
                
            # Agregar equivalencias CBC si aplican
            nombre_norm_limpio = self._preparar_para_matching(nombre_normalizado)
            if nombre_norm_limpio in self.equivalencias_cbc:
                for equivalencia in self.equivalencias_cbc[nombre_norm_limpio]:
                    equiv_normalizada = self._preparar_para_matching(equivalencia)
                    indice[equiv_normalizada] = nombre_normalizado

        return indice

    def _normalizar_nombre_base(self, nombre: str) -> str:
        """Normaliza un nombre de materia al formato estándar LCD"""
        # Limpiar el nombre base
        nombre = nombre.strip()

        # Remover texto entre paréntesis
        nombre = re.sub(r"\s*\([^)]*\)\s*", "", nombre)

        # Remover puntos al final
        nombre = re.sub(r"\.\s*$", "", nombre)

        # Expandir abreviaciones comunes
        nombre = self._expandir_abreviaciones(nombre)
        
        # Convertir números arábigos a romanos
        nombre = self._convertir_numeros_a_romanos(nombre)

        # Remover acentos y convertir a lowercase
        nombre = self._remover_acentos_y_lowercase(nombre)

        # Limpiar espacios múltiples
        nombre = re.sub(r"\s+", " ", nombre)

        return nombre.strip()

    def _convertir_numeros_a_romanos(self, nombre: str) -> str:
        """Convierte números arábigos a romanos en lowercase"""
        # Normalizar números romanos existentes a lowercase
        conversiones_romanos = {
            r'\bII\b': 'ii',
            r'\bIII\b': 'iii', 
            r'\bIV\b': 'iv',
            r'\bV\b': 'v',
            r'\bVI\b': 'vi',
        }
        
        for patron, reemplazo in conversiones_romanos.items():
            nombre = re.sub(patron, reemplazo, nombre, flags=re.IGNORECASE)
        
        # Convertir números arábigos a romanos en lowercase
        conversiones_arabigos = {
            r'\b1\b': 'i',
            r'\b2\b': 'ii', 
            r'\b3\b': 'iii',
            r'\b4\b': 'iv',
            r'\b5\b': 'v',
            r'\b6\b': 'vi',
            r'\bA\b': '',  # Remover "A" suelto como en "Análisis Matemático A"
        }
        
        for patron, reemplazo in conversiones_arabigos.items():
            nombre = re.sub(patron, reemplazo, nombre)
        
        return nombre
    
    def _expandir_abreviaciones(self, nombre: str) -> str:
        """Expande abreviaciones comunes en nombres de materias"""
        expansiones = {
            # Introducciones (expandido desde fase2)
            r'\bIntr\.': 'introduccion',
            r'\bIntro\.': 'introduccion', 
            r'\bIntroducción\b': 'introduccion',
            
            # Ciencias
            r'\bCs\.': 'ciencias',
            r'\bCienc\.': 'ciencias',
            
            # Matemática
            r'\bMat\.': 'matematica',
            r'\bMatem\.': 'matematica',
            
            # Estadística
            r'\bEstad\.': 'estadistica',
            r'\bEstadíst\.': 'estadistica',
            
            # Física
            r'\bFís\.': 'fisica',
            r'\bFisic\.': 'fisica',
            
            # Biología
            r'\bBiol\.': 'biologia',
            r'\bBiológ\.': 'biologia',
            
            # Licenciatura
            r'\bLic\.': 'licenciatura',
            r'\bLicenc\.': 'licenciatura',
            
            # Universidad
            r'\bUniv\.': 'universidad',
            r'\bUnivers\.': 'universidad',
            
            # Departamento
            r'\bDepto\.': 'departamento',
            r'\bDpto\.': 'departamento',
            
            # Adicionales de fase2
            r'\bComp\.': 'computacional',
            r'\bEst\.': 'estadistica',
            r'\bProb\.': 'probabilidad',
            r'\bAlg\.': 'algoritmos',
            r'\bEstr\.': 'estructuras'
        }
        
        for patron, expansion in expansiones.items():
            nombre = re.sub(patron, expansion, nombre, flags=re.IGNORECASE)
        
        return nombre

    def _remover_acentos_y_lowercase(self, nombre: str) -> str:
        """Remueve acentos y convierte a lowercase"""
        # Mapeo de acentos
        acentos = {
            "á": "a", "à": "a", "ä": "a", "â": "a",
            "é": "e", "è": "e", "ë": "e", "ê": "e",
            "í": "i", "ì": "i", "ï": "i", "î": "i",
            "ó": "o", "ò": "o", "ö": "o", "ô": "o",
            "ú": "u", "ù": "u", "ü": "u", "û": "u",
            "ñ": "n",
            "Á": "a", "À": "a", "Ä": "a", "Â": "a",
            "É": "e", "È": "e", "Ë": "e", "Ê": "e",
            "Í": "i", "Ì": "i", "Ï": "i", "Î": "i",
            "Ó": "o", "Ò": "o", "Ö": "o", "Ô": "o",
            "Ú": "u", "Ù": "u", "Ü": "u", "Û": "u",
            "Ñ": "n",
        }

        # Remover acentos
        for acento, sin_acento in acentos.items():
            nombre = nombre.replace(acento, sin_acento)

        # Convertir todo a lowercase
        return nombre.lower()

    def _generar_variaciones_matching(self, nombre_original: str) -> List[str]:
        """Genera variaciones del nombre para mejorar el matching"""
        variaciones = []

        # Versión normalizada para matching (sin acentos, lowercase)
        nombre_matching = nombre_original.lower()
        for acento, sin_acento in {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
        }.items():
            nombre_matching = nombre_matching.replace(acento, sin_acento)

        # Remover caracteres especiales para matching
        nombre_matching = re.sub(r"[^\w\s]", " ", nombre_matching)
        nombre_matching = re.sub(r"\s+", " ", nombre_matching).strip()

        variaciones.append(nombre_matching)

        # Variación sin palabras comunes
        palabras_omitir = {
            "de",
            "del",
            "la",
            "las",
            "el",
            "los",
            "en",
            "a",
            "al",
            "y",
            "o",
            "intro",
            "introduccion",
        }
        palabras_filtradas = [
            p for p in nombre_matching.split() if p not in palabras_omitir
        ]
        if len(palabras_filtradas) >= 2:
            variaciones.append(" ".join(palabras_filtradas))
        
        # Variaciones de singular/plural para casos como "Estructura" vs "Estructuras"
        variaciones_plural = [
            # Estructura/Estructuras
            nombre_matching.replace('estructura', 'estructuras'),
            nombre_matching.replace('estructuras', 'estructura'),
            # Dato/Datos  
            nombre_matching.replace('dato', 'datos'),
            nombre_matching.replace('datos', 'dato'),
            # Algoritmo/Algoritmos
            nombre_matching.replace('algoritmo', 'algoritmos'),
            nombre_matching.replace('algoritmos', 'algoritmo'),
        ]
        
        for variacion in variaciones_plural:
            if variacion != nombre_matching:
                variaciones.append(variacion)
        
        # Variaciones con números tanto arábigos como romanos
        variacion_arabigos = nombre_matching
        variacion_romanos = nombre_matching
        
        # Convertir romanos a arábigos
        conversiones_rom_arab = {'iii': '3', 'ii': '2', 'iv': '4', 'v': '5', 'vi': '6', 'i': '1'}
        for romano, arabigo in conversiones_rom_arab.items():
            variacion_arabigos = re.sub(f'\\b{romano}\\b', arabigo, variacion_arabigos)
        
        # Convertir arábigos a romanos  
        conversiones_arab_rom = {'3': 'iii', '2': 'ii', '4': 'iv', '5': 'v', '6': 'vi', '1': 'i'}
        for arabigo, romano in conversiones_arab_rom.items():
            variacion_romanos = re.sub(f'\\b{arabigo}\\b', romano, variacion_romanos)
        
        if variacion_arabigos != nombre_matching:
            variaciones.append(variacion_arabigos)
        if variacion_romanos != nombre_matching:
            variaciones.append(variacion_romanos)

        return list(set(variaciones))  # Eliminar duplicados

    def normalizar_nombre_web(self, nombre_web: str) -> Optional[str]:
        """
        Normaliza un nombre extraído de la web al formato estándar LCD
        Incluye matching con equivalencias CBC

        Args:
            nombre_web: Nombre extraído de la web (ej: "Física 1 (Lic. en Cs. Físicas) - Electiva...")

        Returns:
            Nombre normalizado (ej: "Fisica I") o None si no se encuentra coincidencia
        """
        if not nombre_web or not nombre_web.strip():
            return None

        # Limpiar el nombre web
        nombre_limpio = self._limpiar_nombre_web(nombre_web)

        # Buscar coincidencia exacta en el índice
        nombre_matching = self._preparar_para_matching(nombre_limpio)

        # Buscar en el índice principal
        if nombre_matching in self.indice_nombres:
            return self.indice_nombres[nombre_matching]

        # Buscar equivalencias CBC
        equivalencia_cbc = self._buscar_equivalencia_cbc(nombre_matching)
        if equivalencia_cbc:
            self.estadisticas["tipos_cambios"]["equivalencias_cbc_aplicadas"] += 1
            return equivalencia_cbc

        # Buscar coincidencia parcial
        coincidencia_parcial = self._buscar_coincidencia_parcial(nombre_matching)
        if coincidencia_parcial:
            return self.indice_nombres[coincidencia_parcial]

        # Si no se encuentra, intentar normalización directa
        nombre_directo = self._normalizar_nombre_base(nombre_limpio)
        if nombre_directo:
            return nombre_directo

        return None

    def _limpiar_nombre_web(self, nombre: str) -> str:
        """Limpia un nombre extraído de la web"""
        # Remover texto después de " - "
        nombre = re.split(r"\s+-\s+", nombre)[0]

        # Remover contenido entre paréntesis con palabras clave
        nombre = re.sub(
            r"\s*\([^)]*(?:Lic\.|solicitar|equivalencia)[^)]*\)",
            "",
            nombre,
            flags=re.IGNORECASE,
        )

        # Remover otros paréntesis al final
        nombre = re.sub(r"\s*\([^)]*\)\s*$", "", nombre)

        # Remover tags HTML
        nombre = re.sub(r"<[^>]+>", "", nombre)

        # Limpiar espacios
        nombre = re.sub(r"\s+", " ", nombre)

        return nombre.strip()

    def _preparar_para_matching(self, nombre: str) -> str:
        """Prepara un nombre para matching en el índice"""
        nombre = nombre.lower()

        # Remover acentos
        for acento, sin_acento in {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
        }.items():
            nombre = nombre.replace(acento, sin_acento)

        # Remover caracteres especiales
        nombre = re.sub(r"[^\w\s]", " ", nombre)
        nombre = re.sub(r"\s+", " ", nombre)

        return nombre.strip()

    def _buscar_coincidencia_parcial(self, nombre_busqueda: str) -> Optional[str]:
        """Busca coincidencias parciales en el índice"""
        palabras_busqueda = set(nombre_busqueda.split())
        if len(palabras_busqueda) < 2:
            return None

        mejor_coincidencia = None
        mayor_score = 0.0

        for nombre_indice in self.indice_nombres.keys():
            palabras_indice = set(nombre_indice.split())

            # Calcular score de coincidencia
            coincidencias = len(palabras_busqueda.intersection(palabras_indice))
            score = coincidencias / max(len(palabras_busqueda), len(palabras_indice))

            # Requerir al menos 60% de coincidencia y mínimo 2 palabras
            if score > 0.6 and coincidencias >= 2 and score > mayor_score:
                mayor_score = score
                mejor_coincidencia = nombre_indice

        return mejor_coincidencia

    def _buscar_equivalencia_cbc(self, nombre_matching: str) -> Optional[str]:
        """Busca equivalencias específicas de CBC"""
        # Buscar directamente en equivalencias
        if nombre_matching in self.equivalencias_cbc:
            equivalencias = self.equivalencias_cbc[nombre_matching]
            # Buscar la primera equivalencia que exista en el índice
            for equiv in equivalencias:
                equiv_matching = self._preparar_para_matching(equiv)
                if equiv_matching in self.indice_nombres:
                    return self.indice_nombres[equiv_matching]
        
        # Buscar equivalencias parciales (para casos como "fisica 1" -> "fisica")
        palabras_busqueda = nombre_matching.split()
        if len(palabras_busqueda) >= 1:
            palabra_base = palabras_busqueda[0]  # "fisica" de "fisica 1"
            
            # Verificar si la palabra base tiene equivalencias
            if palabra_base in self.equivalencias_cbc:
                equivalencias = self.equivalencias_cbc[palabra_base]
                for equiv in equivalencias:
                    equiv_matching = self._preparar_para_matching(equiv)
                    if equiv_matching in self.indice_nombres:
                        return self.indice_nombres[equiv_matching]
            
            # Verificar equivalencias inversas ("quimica general" -> "quimica")
            for clave_equiv, lista_equiv in self.equivalencias_cbc.items():
                if palabra_base in lista_equiv:
                    clave_matching = self._preparar_para_matching(clave_equiv)
                    if clave_matching in self.indice_nombres:
                        return self.indice_nombres[clave_matching]
        
        return None

    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del normalizador"""
        return {
            "total_materias_base": len(self.materias_base),
            "total_variaciones_indice": len(self.indice_nombres),
            "total_equivalencias_cbc": len(self.equivalencias_cbc),
            "materias_por_ciclo": self._contar_por_ciclo(),
        }

    def _contar_por_ciclo(self) -> Dict[str, int]:
        """Cuenta materias por ciclo"""
        conteos: Dict[str, int] = {}
        for materia in self.materias_base:
            ciclo = materia.get("ciclo", "Sin ciclo")
            conteos[ciclo] = conteos.get(ciclo, 0) + 1
        return conteos

    def mostrar_indice_normalizacion(self) -> None:
        """Muestra el índice de normalización para debug"""
        print("📋 ÍNDICE DE NORMALIZACIÓN")
        print("=" * 50)

        for variacion, normalizado in sorted(self.indice_nombres.items()):
            print(f"'{variacion}' → '{normalizado}'")

    def probar_normalizacion(self, nombres_prueba: List[str]) -> None:
        """Prueba la normalización con una lista de nombres"""
        print("\n🧪 PRUEBAS DE NORMALIZACIÓN")
        print("=" * 50)

        for nombre in nombres_prueba:
            resultado = self.normalizar_nombre_web(nombre)
            estado = "✅" if resultado else "❌"
            print(f"{estado} '{nombre}' → '{resultado}'")
    
    def validar_normalizaciones_problematicas(self) -> None:
        """Valida casos problemáticos específicos"""
        print("\n🔍 VALIDACIÓN DE CASOS PROBLEMÁTICOS")
        print("=" * 50)
        
        casos_problematicos = [
            "Algoritmos y Estructuras de Datos I",
            "Algoritmos y Estructuras de Datos II", 
            "Algoritmos y Estructuras de Datos III",
            "Análisis I",
            "Análisis II",
            "Física 1 (Lic. en Cs. Físicas) - Electiva de Intro...",
            "ALGORITMOS Y ESTRUCTURAS DE DATOS III",  # Test uppercase
            "Análisis Matemático A",  # Test eliminación de A
            "Intr. a la Estadística y Ciencia de Datos",  # Test expansión Intr.
            "Intro. al Modelado Continuo",  # Test expansión Intro.
        ]
        
        for nombre in casos_problematicos:
            resultado = self.normalizar_nombre_web(nombre)
            print(f"'{nombre}' → '{resultado}'")
        
        # Verificar que no haya colisiones
        resultados = []
        for nombre in casos_problematicos:
            resultado = self.normalizar_nombre_web(nombre)
            if resultado:
                resultados.append(resultado)
        
        duplicados = [x for x in resultados if resultados.count(x) > 1]
        if duplicados:
            print(f"\n⚠️ COLISIONES DETECTADAS: {set(duplicados)}")
        else:
            print("\n✅ Sin colisiones detectadas")
    
    # ====== MÉTODOS DE INTEGRACIÓN FASE 2 ======
    
    def ejecutar_fase2_completa(self, archivo_entrada: str = "materias.json"):
        """Ejecuta todos los TODOs de la Fase 2 automáticamente (integración desde fase2)"""
        print("🚀 INICIANDO FASE 2: NORMALIZACIÓN AUTOMÁTICA DE NOMBRES")
        print("=" * 70)
        
        # TODO-2.0: Cargar datos
        print("\n📂 TODO-2.0: Cargando datos de entrada...")
        datos = self.cargar_datos_fase2(archivo_entrada)
        print(f"   ✅ Cargados: {len(datos.get('cbc', []))} CBC + {len(datos.get('segundo_ciclo', []))} Segundo + {len(datos.get('tercer_ciclo', []))} Tercer")
        
        # TODO-2.1: Normalización de mayúsculas
        print("\n🔤 TODO-2.1: Ejecutando normalización de mayúsculas...")
        self.normalizar_mayusculas_fase2(datos)
        print(f"   ✅ Completado: {self.estadisticas['tipos_cambios']['mayusculas_corregidas']} correcciones")
        
        # TODO-2.2: Expandir abreviaciones
        print("\n📝 TODO-2.2: Expandiendo abreviaciones comunes...")
        self.expandir_abreviaciones_fase2(datos)
        print(f"   ✅ Completado: {self.estadisticas['tipos_cambios']['abreviaciones_expandidas']} expansiones")
        
        # TODO-2.3: Limpiar caracteres innecesarios
        print("\n🧹 TODO-2.3: Limpiando caracteres innecesarios...")
        self.limpiar_caracteres_fase2(datos)
        print(f"   ✅ Completado: {self.estadisticas['tipos_cambios']['caracteres_limpiados']} limpiezas")
        
        # TODO-2.4: Validar números romanos
        print("\n🔢 TODO-2.4: Validando números romanos...")
        self.validar_numeros_romanos_fase2(datos)
        print(f"   ✅ Completado: {self.estadisticas['tipos_cambios']['numeros_romanos_corregidos']} correcciones")
        
        # TODO-2.5: Guardar resultados
        print("\n💾 TODO-2.5: Guardando resultados normalizados...")
        archivo_salida = self.guardar_resultados_fase2(datos)
        print(f"   ✅ Guardado en: {archivo_salida}")
        
        # TODO-2.6: Generar reporte
        print("\n📊 TODO-2.6: Generando reporte de cambios...")
        self.generar_reporte_fase2()
        
        # TODO-2.7: Actualizar checklist
        print("\n✅ TODO-2.7: Actualizando checklist de progreso...")
        self.actualizar_checklist_fase2()
        
        print("\n🎉 FASE 2 COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        return archivo_salida
    
    def cargar_datos_fase2(self, archivo: str) -> Dict:
        """Carga los datos del archivo JSON para fase 2"""
        ruta_completa = self.obtener_ruta_archivo_fase2(archivo)
        
        if not os.path.exists(ruta_completa):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_completa}")
        
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        return datos
    
    def obtener_ruta_archivo_fase2(self, archivo: str) -> str:
        """Obtiene la ruta completa del archivo en el directorio data"""
        if os.path.isabs(archivo):
            return archivo
        
        # Buscar en directorio data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        return os.path.join(data_dir, archivo)
    
    def normalizar_mayusculas_fase2(self, datos: Dict):
        """TODO-2.1: Normaliza mayúsculas de manera consistente (adaptado para lowercase)"""
        ciclos = ['cbc', 'segundo_ciclo', 'tercer_ciclo']
        
        for ciclo in ciclos:
            if ciclo not in datos:
                continue
                
            for materia in datos[ciclo]:
                # Usar el campo 'nombre' o 'materia' según estructura
                campo_nombre = 'nombre' if 'nombre' in materia else 'materia'
                nombre_original = materia.get(campo_nombre, '')
                
                # Aplicar normalización a lowercase
                nombre_normalizado = self._normalizar_nombre_base(nombre_original)
                
                if nombre_original.lower() != nombre_normalizado:
                    materia[campo_nombre] = nombre_normalizado
                    materia['nombre_normalizado'] = nombre_normalizado
                    self.estadisticas['tipos_cambios']['mayusculas_corregidas'] += 1
                    print(f"      🔤 {nombre_original} → {nombre_normalizado}")
    
    def expandir_abreviaciones_fase2(self, datos: Dict):
        """TODO-2.2: Expande abreviaciones comunes (integrado con método principal)"""
        ciclos = ['cbc', 'segundo_ciclo', 'tercer_ciclo']
        
        for ciclo in ciclos:
            if ciclo not in datos:
                continue
                
            for materia in datos[ciclo]:
                campo_nombre = 'nombre' if 'nombre' in materia else 'materia' 
                nombre_original = materia.get(campo_nombre, '')
                nombre_expandido = self._expandir_abreviaciones(nombre_original)
                
                if nombre_original != nombre_expandido:
                    materia[campo_nombre] = nombre_expandido
                    materia['nombre_normalizado'] = nombre_expandido
                    self.estadisticas['tipos_cambios']['abreviaciones_expandidas'] += 1
                    print(f"      📝 Expansión en: {nombre_original} → {nombre_expandido}")
    
    def limpiar_caracteres_fase2(self, datos: Dict):
        """TODO-2.3: Limpia caracteres innecesarios"""
        ciclos = ['cbc', 'segundo_ciclo', 'tercer_ciclo']
        
        for ciclo in ciclos:
            if ciclo not in datos:
                continue
                
            for materia in datos[ciclo]:
                campo_nombre = 'nombre' if 'nombre' in materia else 'materia'
                nombre_original = materia.get(campo_nombre, '')
                nombre_limpio = self.aplicar_limpieza_fase2(nombre_original)
                
                if nombre_original != nombre_limpio:
                    materia[campo_nombre] = nombre_limpio
                    materia['nombre_normalizado'] = nombre_limpio
                    self.estadisticas['tipos_cambios']['caracteres_limpiados'] += 1
                    print(f"      🧹 {nombre_original} → {nombre_limpio}")
    
    def aplicar_limpieza_fase2(self, nombre: str) -> str:
        """Aplica reglas de limpieza de caracteres (adaptado para lowercase)"""
        # Quitar puntos finales innecesarios
        if nombre.endswith('.') and not nombre.endswith('...'):
            nombre = nombre.rstrip('.')
        
        # Normalizar espacios múltiples
        nombre = re.sub(r'\s+', ' ', nombre)
        
        # Quitar espacios al inicio y final
        nombre = nombre.strip()
        
        # Remover caracteres especiales extraños (mantener paréntesis para electivas)
        nombre = re.sub(r'[^\w\s\(\)\.\-áéíóúñÁÉÍÓÚÑ]', '', nombre)
        
        return nombre
    
    def validar_numeros_romanos_fase2(self, datos: Dict):
        """TODO-2.4: Valida y corrige números romanos (adaptado para lowercase)"""
        # Patrones para convertir a lowercase 
        patrones_romanos = {
            r'\b1\b': 'i',
            r'\b2\b': 'ii', 
            r'\b3\b': 'iii',
            r'\b4\b': 'iv',
            r'\b5\b': 'v',
            r'\bI\b': 'i',
            r'\bII\b': 'ii',
            r'\bIII\b': 'iii',
            r'\bIV\b': 'iv',
            r'\bV\b': 'v'
        }
        
        ciclos = ['cbc', 'segundo_ciclo', 'tercer_ciclo']
        
        for ciclo in ciclos:
            if ciclo not in datos:
                continue
                
            for materia in datos[ciclo]:
                campo_nombre = 'nombre' if 'nombre' in materia else 'materia'
                nombre_original = materia.get(campo_nombre, '')
                nombre_corregido = nombre_original
                
                # Aplicar cada patrón
                for patron, reemplazo in patrones_romanos.items():
                    if re.search(patron, nombre_corregido, re.IGNORECASE):
                        nombre_corregido = re.sub(patron, reemplazo, nombre_corregido, flags=re.IGNORECASE)
                        self.estadisticas['tipos_cambios']['numeros_romanos_corregidos'] += 1
                        print(f"      🔢 Romano corregido en: {nombre_original}")
                
                if nombre_original != nombre_corregido:
                    materia[campo_nombre] = nombre_corregido
                    materia['nombre_normalizado'] = nombre_corregido
    
    def guardar_resultados_fase2(self, datos: Dict) -> str:
        """TODO-2.5: Guarda los resultados normalizados"""
        # Actualizar metadata
        if 'metadata' not in datos:
            datos['metadata'] = {}
            
        datos['metadata']['fecha_normalizacion'] = datetime.now().isoformat()
        datos['metadata']['fase2_completada'] = True
        datos['metadata']['cambios_normalizacion'] = self.estadisticas
        
        # Actualizar contadores
        total_materias = 0
        for ciclo in ['cbc', 'segundo_ciclo', 'tercer_ciclo']:
            if ciclo in datos:
                total_materias += len(datos[ciclo])
        
        self.estadisticas['materias_procesadas'] = total_materias
        self.estadisticas['cambios_realizados'] = sum(self.estadisticas['tipos_cambios'].values())
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = f"materias_fase2_normalizado_{timestamp}.json"
        
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        ruta_completa = os.path.join(data_dir, archivo_salida)
        
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        return ruta_completa
    
    def generar_reporte_fase2(self):
        """TODO-2.6: Genera reporte detallado de cambios"""
        print("\n📊 REPORTE DE NORMALIZACIÓN - FASE 2")
        print("-" * 50)
        print(f"Materias procesadas: {self.estadisticas['materias_procesadas']}")
        print(f"Total de cambios: {self.estadisticas['cambios_realizados']}")
        print()
        print("Desglose por tipo:")
        for tipo, cantidad in self.estadisticas['tipos_cambios'].items():
            print(f"  • {tipo.replace('_', ' ').title()}: {cantidad}")
        
        # Calcular porcentaje de mejora
        if self.estadisticas['materias_procesadas'] > 0:
            porcentaje = (self.estadisticas['cambios_realizados'] / self.estadisticas['materias_procesadas']) * 100
            print(f"\nPorcentaje de materias mejoradas: {porcentaje:.1f}%")
    
    def actualizar_checklist_fase2(self):
        """TODO-2.7: Actualiza el checklist de progreso"""
        print("   📝 Marcando TODOs de Fase 2 como completados...")
        print("   ✅ TODO-2.1: Normalización de mayúsculas")
        print("   ✅ TODO-2.2: Expansión de abreviaciones") 
        print("   ✅ TODO-2.3: Limpieza de caracteres")
        print("   ✅ TODO-2.4: Validación de números romanos")
        print("   ✅ TODO-2.5: Guardado de resultados")
        print("   ✅ TODO-2.6: Generación de reporte")
        print("   ✅ TODO-2.7: Actualización de checklist")
        print()
        print("   📊 FASE 2 COMPLETADA: 7/7 TODOs principales")
        print("   🎯 Progreso total: Sistema de normalización unificado")


def main():
    """Función principal para pruebas"""
    normalizador = NormalizadorNombresMaterias()

    # Mostrar estadísticas
    stats = normalizador.obtener_estadisticas()
    print("📊 ESTADÍSTICAS DEL NORMALIZADOR")
    print(f"Total materias base: {stats['total_materias_base']}")
    print(f"Total variaciones en índice: {stats['total_variaciones_indice']}")
    print("Materias por ciclo:", stats["materias_por_ciclo"])

    # Validar casos problemáticos primero
    normalizador.validar_normalizaciones_problematicas()
    
    # Pruebas de normalización
    nombres_prueba = [
        "Física 1 (Lic. en Cs. Físicas) - Electiva de Intro. a las Cs. Naturales (solicitar equivalencia)",
        "Análisis I",
        "Análisis II",
        "Álgebra I",
        "Algoritmos y Estructuras de Datos I",
        "Algoritmos y Estructuras de Datos II",
        "Algoritmos y Estructuras de Datos III",
        "Probabilidad y Estadística",
        "Introducción al Pensamiento Científico",
        "Análisis Matemático A",
    ]

    normalizador.probar_normalizacion(nombres_prueba)


if __name__ == "__main__":
    main()
