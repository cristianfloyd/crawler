#!/usr/bin/env python3
"""
Test Simple para Sistema RAG de Horarios
Prueba básica de funcionamiento
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios

def test_consulta_simple():
    """Test básico de consulta"""
    print("Iniciando test simple...")
    
    # Cargar sistema
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Prueba 1: Consulta con acentos
    print("\n=== Test 1: Consulta con acentos ===")
    consulta_con_acentos = "¿Cuándo se dicta Análisis Matemático?"
    print(f"Consulta original: {consulta_con_acentos}")
    
    consulta_normalizada = sistema.normalizar_consulta_horario(consulta_con_acentos)
    print(f"Consulta normalizada: {consulta_normalizada}")
    
    respuestas = sistema.buscar_similares_horarios(consulta_con_acentos, k=3)
    print(f"Respuestas encontradas: {len(respuestas)}")
    
    for i, (doc, score) in enumerate(respuestas[:2], 1):
        nombre = doc['metadatos']['materia_nombre']
        print(f"  {i}. [{score:.3f}] {nombre}")
    
    # Prueba 2: Consulta sin acentos
    print("\n=== Test 2: Consulta sin acentos ===")
    consulta_sin_acentos = "cuando se dicta analisis matematico"
    print(f"Consulta: {consulta_sin_acentos}")
    
    respuestas2 = sistema.buscar_similares_horarios(consulta_sin_acentos, k=3)
    print(f"Respuestas encontradas: {len(respuestas2)}")
    
    for i, (doc, score) in enumerate(respuestas2[:2], 1):
        nombre = doc['metadatos']['materia_nombre']
        print(f"  {i}. [{score:.3f}] {nombre}")
    
    print("\nTest completado!")

if __name__ == "__main__":
    test_consulta_simple()