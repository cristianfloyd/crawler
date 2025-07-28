#!/usr/bin/env python3
"""
Configuración de Rutas del Proyecto MVP RAG Horarios
Centraliza todas las rutas según la estructura establecida en el checklist
"""

import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent

# Directorios principales
DESCUBRIMIENTO_DIR = BASE_DIR / "descubrimiento"
SCRAPERS_DIR = BASE_DIR / "scrapers"
DATOS_DIR = BASE_DIR / "datos"
RAG_SISTEMA_DIR = BASE_DIR / "rag_sistema_con_horarios"
TESTS_DIR = BASE_DIR / "tests"
REPORTES_DIR = BASE_DIR / "reportes"
DOCS_DIR = BASE_DIR / "docs"
TEMPORALES_DIR = BASE_DIR / "temporales"

# Subdirectorios de datos
DATOS_RAW_DIR = DATOS_DIR / "raw"
DATOS_PROCESADOS_DIR = DATOS_DIR / "procesados"
DATOS_ESQUEMAS_DIR = DATOS_DIR / "esquemas"

# Archivos principales de datos raw
HORARIOS_DC_FILE = DATOS_RAW_DIR / "horarios_dc_20250727_020723.json"
HORARIOS_MATEMATICA_FILE = DATOS_RAW_DIR / "horarios_matematica_20250727_023346.json"
HORARIOS_INSTITUTO_FILE = DATOS_RAW_DIR / "horarios_instituto_calculo_20250727_024931.json"

# Archivos procesados
MATERIAS_UNIFICADAS_FILE = DATOS_PROCESADOS_DIR / "materias_unificadas_20250727_030943.json"
MATERIAS_NORMALIZADAS_FILE = DATOS_PROCESADOS_DIR / "materias_normalizadas.json"

# Sistema RAG
RAG_DOCUMENTOS_FILE = RAG_SISTEMA_DIR / "documentos_horarios.json"
RAG_INDICE_FILE = RAG_SISTEMA_DIR / "indice_horarios.faiss"
RAG_METADATOS_FILE = RAG_SISTEMA_DIR / "metadatos_horarios.json"

# Archivos de descubrimiento
INVENTARIO_SITIOS_FILE = DESCUBRIMIENTO_DIR / "inventario_sitios.json"
SITIOS_PRIORITARIOS_FILE = DESCUBRIMIENTO_DIR / "sitios_prioritarios_mvp.json"

def ensure_directories():
    """Crea todos los directorios necesarios si no existen"""
    dirs = [
        DESCUBRIMIENTO_DIR, SCRAPERS_DIR, DATOS_DIR, RAG_SISTEMA_DIR,
        TESTS_DIR, REPORTES_DIR, DOCS_DIR, TEMPORALES_DIR,
        DATOS_RAW_DIR, DATOS_PROCESADOS_DIR, DATOS_ESQUEMAS_DIR
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        
def get_relative_path(file_path: Path) -> str:
    """Retorna la ruta relativa desde el directorio base"""
    return str(file_path.relative_to(BASE_DIR))

if __name__ == "__main__":
    ensure_directories()
    print("Estructura de directorios creada/verificada exitosamente")