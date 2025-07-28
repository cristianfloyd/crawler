#!/usr/bin/env python3
"""
Sistema de Embeddings Especializado para Horarios - Día 4
Adaptación del sistema RAG para consultas específicas de horarios

Autor: Sistema RAG MVP
Fecha: 2025-07-27
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from typing import List, Dict, Any, Tuple, Optional
import os
import re
from datetime import datetime, time
import logging
import unicodedata
try:
    from .config_paths import RAG_DOCUMENTOS_FILE, RAG_INDICE_FILE, RAG_METADATOS_FILE, RAG_SISTEMA_DIR
except ImportError:
    from config_paths import RAG_DOCUMENTOS_FILE, RAG_INDICE_FILE, RAG_METADATOS_FILE, RAG_SISTEMA_DIR

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SistemaEmbeddingsHorarios:
    """Sistema de embeddings especializado para consultas de horarios académicos"""
    
    def __init__(
        self,
        modelo_nombre: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        """
        Inicializa el sistema de embeddings para horarios
        
        Args:
            modelo_nombre: Modelo de sentence transformers para español
        """
        logger.info(f"🤖 Cargando modelo de embeddings para horarios: {modelo_nombre}")
        self.modelo = SentenceTransformer(modelo_nombre)
        self.dimension = self.modelo.get_sentence_embedding_dimension()
        self.index = None
        self.documentos = []
        self.metadata_horarios = {}
        
        # Mapeos para normalización de consultas
        self.dias_semana = {
            'lunes': 'lunes', 'lu': 'lunes', 'l': 'lunes',
            'martes': 'martes', 'ma': 'martes', 'mar': 'martes',
            'miercoles': 'miércoles', 'miércoles': 'miércoles', 'mi': 'miércoles',
            'jueves': 'jueves', 'ju': 'jueves', 'jue': 'jueves',
            'viernes': 'viernes', 'vi': 'viernes', 'vie': 'viernes',
            'sabado': 'sábado', 'sábado': 'sábado', 'sa': 'sábado',
            'domingo': 'domingo', 'do': 'domingo', 'dom': 'domingo'
        }

    def generar_texto_enriquecido(self, materia: Dict) -> str:
        """Genera texto enriquecido con información de horarios para embeddings"""
        textos = []
        
        # Información básica
        nombre = materia.get('nombre', '')
        nombre_normalizado = materia.get('nombre_normalizado', '')
        departamento = materia.get('departamento', {}).get('nombre', '')
        codigo_dept = materia.get('departamento', {}).get('codigo', '')
        
        textos.append(f"Materia: {nombre}")
        if nombre_normalizado and nombre_normalizado != nombre:
            textos.append(f"También conocida como: {nombre_normalizado}")
        textos.append(f"Departamento: {departamento} ({codigo_dept})")
        
        # Información de horarios
        horarios = materia.get('horarios', [])
        if horarios:
            textos.append("Horarios de cursada:")
            for horario in horarios:
                dia = horario.get('dia', '')
                inicio = horario.get('hora_inicio', '')
                fin = horario.get('hora_fin', '')
                tipo = horario.get('tipo_actividad', '')
                comision = horario.get('comision', '')
                aula = horario.get('aula', '')
                
                texto_horario = f"{dia} de {inicio} a {fin}"
                if tipo and tipo != 'general':
                    texto_horario += f" ({tipo})"
                if comision:
                    texto_horario += f" comisión {comision}"
                if aula:
                    texto_horario += f" en {aula}"
                
                textos.append(texto_horario)
        else:
            textos.append("Sin horarios de cursada definidos")
        
        # Información de docentes
        docentes = materia.get('docentes', [])
        if docentes:
            nombres_docentes = []
            for docente in docentes:
                if isinstance(docente, dict):
                    nombre_doc = docente.get('nombre', '')
                    rol = docente.get('rol', '')
                    if nombre_doc:
                        nombres_docentes.append(f"{nombre_doc} ({rol})" if rol else nombre_doc)
                elif isinstance(docente, str):
                    nombres_docentes.append(docente)
            
            if nombres_docentes:
                textos.append(f"Docentes: {', '.join(nombres_docentes)}")
        
        # Información de período
        periodo = materia.get('periodo', {})
        if periodo:
            info_periodo = []
            if periodo.get('cuatrimestre'):
                info_periodo.append(f"{periodo['cuatrimestre']}° cuatrimestre")
            if periodo.get('bimestre'):
                info_periodo.append(f"{periodo['bimestre']}° bimestre")
            if periodo.get('año'):
                info_periodo.append(f"año {periodo['año']}")
            
            if info_periodo:
                textos.append(f"Período: {' '.join(info_periodo)}")
        
        # Palabras clave para búsqueda
        palabras_clave = []
        
        # Días de la semana presentes
        dias_presentes = set()
        for horario in horarios:
            dia = horario.get('dia', '').lower()
            if dia in self.dias_semana.values():
                dias_presentes.add(dia)
        
        if dias_presentes:
            palabras_clave.extend([f"clases {dia}" for dia in dias_presentes])
            palabras_clave.extend([f"cursada {dia}" for dia in dias_presentes])
        
        # Rangos horarios
        for horario in horarios:
            inicio = horario.get('hora_inicio', '')
            fin = horario.get('hora_fin', '')
            if inicio and fin:
                palabras_clave.append(f"horario {inicio} {fin}")
                palabras_clave.append(f"de {inicio} a {fin}")
                
                # Identificar si es mañana, tarde o noche
                try:
                    hora_num = int(inicio.split(':')[0])
                    if 6 <= hora_num < 12:
                        palabras_clave.append("clases mañana")
                    elif 12 <= hora_num < 18:
                        palabras_clave.append("clases tarde")
                    elif 18 <= hora_num <= 23:
                        palabras_clave.append("clases noche")
                except:
                    pass
        
        if palabras_clave:
            textos.append(f"Términos de búsqueda: {', '.join(palabras_clave)}")
        
        return '\n'.join(textos)

    def crear_documentos_desde_materias(self, archivo_materias: str) -> List[Dict]:
        """Crea documentos RAG desde el archivo de materias unificadas"""
        logger.info(f"📚 Cargando materias desde: {archivo_materias}")
        
        with open(archivo_materias, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        materias = datos.get('materias', [])
        documentos = []
        
        for i, materia in enumerate(materias):
            # Generar texto enriquecido
            contenido = self.generar_texto_enriquecido(materia)
            
            # Crear metadatos enriquecidos
            metadatos = {
                'id': materia.get('id', f'materia_{i}'),
                'materia_nombre': materia.get('nombre', ''),
                'materia_normalizada': materia.get('nombre_normalizado', ''),
                'departamento_codigo': materia.get('departamento', {}).get('codigo', ''),
                'departamento_nombre': materia.get('departamento', {}).get('nombre', ''),
                'tiene_horarios': len(materia.get('horarios', [])) > 0,
                'cantidad_horarios': len(materia.get('horarios', [])),
                'docentes_count': len(materia.get('docentes', [])),
                'fuente_original': materia.get('metadata', {}).get('fuente_original', ''),
                'periodo': materia.get('periodo', {}),
                
                # Metadatos específicos para horarios
                'dias_semana': list(set([h.get('dia', '') for h in materia.get('horarios', []) if h.get('dia')])),
                'horas_inicio': [h.get('hora_inicio', '') for h in materia.get('horarios', []) if h.get('hora_inicio')],
                'horas_fin': [h.get('hora_fin', '') for h in materia.get('horarios', []) if h.get('hora_fin')],
                'tipos_actividad': list(set([h.get('tipo_actividad', '') for h in materia.get('horarios', []) if h.get('tipo_actividad')])),
            }
            
            documento = {
                'id': metadatos['id'],
                'contenido': contenido,
                'metadatos': metadatos,
                'materia_original': materia  # Mantener datos originales para referencia
            }
            
            documentos.append(documento)
        
        logger.info(f"✅ Creados {len(documentos)} documentos desde {len(materias)} materias")
        return documentos

    def crear_embeddings(self, documentos: List[Dict[str, Any]]) -> np.ndarray:
        """Crea embeddings optimizados para consultas de horarios"""
        logger.info(f"🔄 Generando embeddings para {len(documentos)} documentos de horarios...")

        textos = []
        for doc in documentos:
            # Usar contenido enriquecido directamente
            textos.append(doc['contenido'])

        # Generar embeddings en lotes para eficiencia
        embeddings = self.modelo.encode(
            textos, 
            batch_size=32, 
            show_progress_bar=True, 
            convert_to_numpy=True
        )

        return embeddings

    def crear_indice_faiss(self, embeddings: np.ndarray):
        """Crea índice FAISS optimizado para búsquedas de horarios"""
        logger.info(f"🗃️ Creando índice FAISS para horarios con {len(embeddings)} vectores")

        # Usar IndexFlatIP para similitud coseno
        self.index = faiss.IndexFlatIP(self.dimension)

        # Normalizar embeddings
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Agregar al índice
        self.index.add(embeddings_norm.astype(np.float32))

        logger.info(f"✅ Índice de horarios creado con {self.index.ntotal} vectores")

    def procesar_materias_unificadas(self, archivo_materias: str = "materias_unificadas_20250727_030943.json"):
        """Procesa materias unificadas para crear sistema RAG de horarios"""
        logger.info("📚 Procesando materias unificadas para sistema RAG de horarios...")
        
        # Crear documentos desde materias
        self.documentos = self.crear_documentos_desde_materias(archivo_materias)
        
        # Crear embeddings
        embeddings = self.crear_embeddings(self.documentos)
        
        # Crear índice FAISS
        self.crear_indice_faiss(embeddings)
        
        logger.info("✅ Sistema RAG de horarios procesado exitosamente")
        return self

    def normalizar_consulta_horario(self, consulta: str) -> str:
        """Normaliza consultas específicas de horarios"""
        # Primero normalizar sin acentos (igual que las materias)
        consulta_norm = self._normalizar_nombre_sin_acentos(consulta)
        
        # Normalizar días de la semana
        for variante, dia_norm in self.dias_semana.items():
            consulta_norm = re.sub(r'\b' + variante + r'\b', dia_norm, consulta_norm)
        
        # Mejorar consultas contextuales sin diluir el contenido original
        # Priorizar el contenido específico (nombres de materias) sobre las palabras contextuales
        
        # Reemplazar palabras contextuales por términos más específicos
        reemplazos_contextuales = {
            'cuando se dicta': 'horarios',
            'que hora': 'horarios',
            'se dicta': 'horarios',
            'dicta': 'horarios',
            'cursada': 'horarios',
            'clases': 'horarios'
        }
        
        for patron, reemplazo in reemplazos_contextuales.items():
            if patron in consulta_norm:
                consulta_norm = consulta_norm.replace(patron, reemplazo)
        
        # Solo expandir para términos temporales específicos (no generales)
        expansiones_especificas = {
            'manana': 'manana 09 10 11',
            'tarde': 'tarde 14 15 16 17', 
            'noche': 'noche 18 19 20 21'
        }
        
        for patron, expansion in expansiones_especificas.items():
            if patron in consulta_norm:
                consulta_norm = consulta_norm.replace(patron, expansion)
        
        return consulta_norm

    def buscar_por_horario_especifico(self, dia: str = "", hora_inicio: str = "", hora_fin: str = "") -> List[Dict]:
        """Busca materias por criterios específicos de horario"""
        resultados = []
        
        for doc in self.documentos:
            materia = doc['materia_original']
            horarios = materia.get('horarios', [])
            
            coincide = True
            
            for horario in horarios:
                if dia and horario.get('dia', '').lower() != dia.lower():
                    continue
                if hora_inicio and horario.get('hora_inicio', '') != hora_inicio:
                    continue
                if hora_fin and horario.get('hora_fin', '') != hora_fin:
                    continue
                
                # Si llegamos aquí, este horario coincide
                resultados.append({
                    'documento': doc,
                    'horario_coincidente': horario,
                    'score': 1.0  # Score máximo para coincidencia exacta
                })
                break
        
        return resultados

    def buscar_similares_horarios(self, consulta: str, k: int = 5, filtro_horarios: bool = True) -> List[Tuple[Dict[str, Any], float]]:
        """
        Busca documentos similares con optimización para consultas de horarios
        
        Args:
            consulta: Texto de la consulta
            k: Número de resultados
            filtro_horarios: Si True, prioriza materias con horarios
        """
        if self.index is None:
            raise ValueError("Debe procesar documentos primero")

        # Normalizar consulta para horarios
        consulta_normalizada = self.normalizar_consulta_horario(consulta)
        
        # Generar embedding de la consulta
        embedding_consulta = self.modelo.encode([consulta_normalizada], convert_to_numpy=True)
        embedding_consulta = embedding_consulta / np.linalg.norm(
            embedding_consulta, axis=1, keepdims=True
        )

        # Buscar más candidatos para filtrar después
        k_busqueda = k * 3 if filtro_horarios else k
        scores, indices = self.index.search(embedding_consulta.astype(np.float32), k_busqueda)

        # Procesar resultados
        resultados = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documentos):
                documento = self.documentos[idx]
                
                # Aplicar filtro de horarios si está habilitado
                if filtro_horarios and not documento['metadatos']['tiene_horarios']:
                    continue
                
                resultados.append((documento, float(score)))
                
                # Limitar a k resultados
                if len(resultados) >= k:
                    break

        return resultados

    def guardar_sistema_horarios(self, directorio: str = "rag_sistema_horarios"):
        """Guarda el sistema RAG especializado en horarios"""
        os.makedirs(directorio, exist_ok=True)

        # Guardar índice FAISS
        faiss.write_index(self.index, os.path.join(directorio, "indice_horarios.faiss"))

        # Guardar documentos
        with open(os.path.join(directorio, "documentos_horarios.json"), "w", encoding="utf-8") as f:
            json.dump(self.documentos, f, ensure_ascii=False, indent=2)

        # Guardar metadatos del sistema
        metadatos = {
            "tipo_sistema": "rag_horarios_academicos",
            "modelo_nombre": self.modelo.model_name if hasattr(self.modelo, "model_name") else "unknown",
            "dimension": self.dimension,
            "total_documentos": len(self.documentos),
            "total_vectores": self.index.ntotal if self.index else 0,
            "materias_con_horarios": sum(1 for d in self.documentos if d['metadatos']['tiene_horarios']),
            "fecha_creacion": datetime.now().isoformat(),
            "version": "1.0"
        }

        with open(os.path.join(directorio, "metadatos_horarios.json"), "w", encoding="utf-8") as f:
            json.dump(metadatos, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Sistema RAG de horarios guardado en: {directorio}")

    def cargar_sistema_horarios(self, directorio: str = None):
        """Carga sistema RAG de horarios previamente guardado"""
        if directorio is None:
            directorio = str(RAG_SISTEMA_DIR)
        
        logger.info(f"📂 Cargando sistema RAG de horarios desde: {directorio}")

        # Cargar índice FAISS
        self.index = faiss.read_index(str(RAG_INDICE_FILE))

        # Cargar documentos
        with open(str(RAG_DOCUMENTOS_FILE), "r", encoding="utf-8") as f:
            self.documentos = json.load(f)

        # Cargar metadatos
        with open(str(RAG_METADATOS_FILE), "r", encoding="utf-8") as f:
            metadatos = json.load(f)

        logger.info(f"✅ Sistema de horarios cargado: {metadatos['total_documentos']} documentos, {metadatos['materias_con_horarios']} con horarios")
        return self
    
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
        
        # Limpiar caracteres especiales pero mantener espacios y números
        nombre = re.sub(r'[^\w\s]', ' ', nombre)
        
        # Normalizar espacios múltiples
        nombre = re.sub(r'\s+', ' ', nombre).strip()
        
        return nombre


def test_sistema_horarios():
    """Función de prueba del sistema de horarios"""
    logger.info("🧪 Probando sistema de embeddings para horarios...")

    sistema = SistemaEmbeddingsHorarios()
    sistema.procesar_materias_unificadas()

    # Pruebas específicas de horarios
    consultas_test = [
        "¿Cuándo se dicta Análisis Matemático?",
        "¿Qué materias hay los lunes?",
        "¿Horarios de clases por la mañana?",
        "¿Materias los martes por la tarde?",
        "¿Qué se cursa los viernes?",
        "Algoritmos y Estructuras de Datos horarios",
        "Estadística cuándo se dicta",
        "Clases de noche",
        "Programación horarios"
    ]

    logger.info("\n🔍 Probando búsquedas especializadas en horarios:")
    for consulta in consultas_test:
        logger.info(f"\n❓ Consulta: '{consulta}'")
        resultados = sistema.buscar_similares_horarios(consulta, k=3)

        for i, (doc, score) in enumerate(resultados[:2], 1):
            nombre = doc['metadatos']['materia_nombre']
            tiene_horarios = "✅" if doc['metadatos']['tiene_horarios'] else "❌"
            logger.info(f"   {i}. [{score:.3f}] {tiene_horarios} {nombre}")
            
            # Mostrar horarios si los tiene
            if doc['metadatos']['tiene_horarios']:
                dias = ', '.join(doc['metadatos']['dias_semana'])
                logger.info(f"      📅 Días: {dias}")

    # Guardar sistema
    sistema.guardar_sistema_horarios()
    
    return sistema


def main():
    """Función principal para crear el sistema RAG de horarios"""
    logger.info("🚀 Iniciando creación del Sistema RAG especializado en Horarios")
    
    # Crear sistema de embeddings para horarios
    sistema = SistemaEmbeddingsHorarios()

    # Procesar materias unificadas
    sistema.procesar_materias_unificadas()

    # Guardar sistema
    sistema.guardar_sistema_horarios()

    # Realizar pruebas
    logger.info("\n" + "=" * 60)
    logger.info("🧪 REALIZANDO PRUEBAS DEL SISTEMA DE HORARIOS")
    logger.info("=" * 60)

    consultas_test = [
        "¿Cuándo se dicta Análisis Matemático I?",
        "¿Qué materias hay los lunes por la mañana?", 
        "¿Horarios de Algoritmos y Estructuras de Datos?",
        "¿Materias los viernes?",
        "¿Clases de estadística cuándo son?"
    ]

    for consulta in consultas_test:
        logger.info(f"\n❓ {consulta}")
        resultados = sistema.buscar_similares_horarios(consulta, k=3)

        for i, (doc, score) in enumerate(resultados, 1):
            nombre = doc['metadatos']['materia_nombre']
            dept = doc['metadatos']['departamento_codigo']
            tiene_horarios = "🕐" if doc['metadatos']['tiene_horarios'] else "❌"
            
            logger.info(f"   {i}. [{score:.3f}] {tiene_horarios} {nombre} ({dept})")
            
            if doc['metadatos']['tiene_horarios'] and doc['metadatos']['dias_semana']:
                dias = ', '.join(doc['metadatos']['dias_semana'])
                logger.info(f"      📅 {dias}")

    logger.info("\n✅ Sistema RAG de horarios creado exitosamente!")


if __name__ == "__main__":
    main()