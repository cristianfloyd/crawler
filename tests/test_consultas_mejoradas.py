#!/usr/bin/env python3
"""
Test de consultas contextuales mejoradas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios

def test_consultas_mejoradas():
    """Test de consultas contextuales mejoradas"""
    print("Testing consultas contextuales mejoradas...")
    
    # Cargar sistema
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Consultas de prueba con análisis matemático
    consultas_test = [
        "cuando se dicta analisis matematico",
        "analisis matematico horarios",
        "que hora se dicta analisis matematico I",
        "horarios de analisis matematico",
        "analisis matematico I cuando",
        "cuando analisis matematico"
    ]
    
    print("\n=== Comparación de consultas ===")
    
    for consulta in consultas_test:
        print(f"\n--- Consulta: '{consulta}' ---")
        
        # Mostrar normalización
        consulta_normalizada = sistema.normalizar_consulta_horario(consulta)
        print(f"Normalizada: '{consulta_normalizada}'")
        
        # Buscar
        respuestas = sistema.buscar_similares_horarios(consulta, k=3)
        
        # Verificar si encuentra análisis matemático en top 3
        encontro_analisis = False
        for i, (doc, score) in enumerate(respuestas, 1):
            nombre = doc['metadatos']['materia_nombre'].lower()
            dept = doc['metadatos']['departamento_codigo']
            
            if 'analisis' in nombre and 'matematico' in nombre:
                print(f"  ✅ {i}. [{score:.3f}] {doc['metadatos']['materia_nombre']} ({dept})")
                encontro_analisis = True
            else:
                print(f"  {i}. [{score:.3f}] {doc['metadatos']['materia_nombre']} ({dept})")
        
        if not encontro_analisis:
            print("  ❌ No encontró análisis matemático en top 3")
    
    print("\n=== Test de otras materias específicas ===")
    
    # Test con otras materias
    otras_consultas = [
        "cuando se dicta algoritmos",
        "horarios de estructuras de datos", 
        "que hora programacion",
        "cuando matematica discreta"
    ]
    
    for consulta in otras_consultas:
        print(f"\n--- {consulta} ---")
        respuestas = sistema.buscar_similares_horarios(consulta, k=2)
        
        for i, (doc, score) in enumerate(respuestas, 1):
            nombre = doc['metadatos']['materia_nombre']
            dept = doc['metadatos']['departamento_codigo']
            print(f"  {i}. [{score:.3f}] {nombre} ({dept})")

if __name__ == "__main__":
    test_consultas_mejoradas()