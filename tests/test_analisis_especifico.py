#!/usr/bin/env python3
"""
Test específico para buscar Análisis Matemático
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios

def buscar_analisis_matematico():
    """Buscar específicamente materias de análisis matemático"""
    print("Buscando materias de Analisis Matematico...")
    
    # Cargar sistema
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Buscar todas las materias que contengan "analisis"
    print("\n=== Materias disponibles con 'analisis' ===")
    materias_analisis = []
    
    for doc in sistema.documentos:
        nombre = doc['metadatos']['materia_nombre'].lower()
        if 'analisis' in nombre or 'análisis' in nombre:
            materias_analisis.append(doc['metadatos']['materia_nombre'])
            print(f"- {doc['metadatos']['materia_nombre']} ({doc['metadatos']['departamento_codigo']})")
    
    print(f"\nTotal materias con 'analisis': {len(materias_analisis)}")
    
    # Probar diferentes consultas
    consultas = [
        "analisis matematico",
        "análisis matemático I",
        "Análisis Matemático I",
        "cuando se dicta analisis matematico",
        "horarios de analisis matematico"
    ]
    
    for consulta in consultas:
        print(f"\n=== Consulta: '{consulta}' ===")
        
        respuestas = sistema.buscar_similares_horarios(consulta, k=5)
        
        for i, (doc, score) in enumerate(respuestas[:3], 1):
            nombre = doc['metadatos']['materia_nombre']
            dept = doc['metadatos']['departamento_codigo']
            tiene_horarios = doc['metadatos'].get('tiene_horarios', False)
            horarios_mark = "🕐" if tiene_horarios else "❌"
            
            # Mostrar sin emoji si hay problemas de encoding
            print(f"  {i}. [{score:.3f}] {nombre} ({dept}) - Horarios: {tiene_horarios}")
            
            # Mostrar días si tiene horarios
            if tiene_horarios and doc['metadatos'].get('dias_semana'):
                dias = ', '.join(doc['metadatos']['dias_semana'])
                print(f"      Días: {dias}")

if __name__ == "__main__":
    buscar_analisis_matematico()