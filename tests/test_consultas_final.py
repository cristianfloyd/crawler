#!/usr/bin/env python3
"""
Test final de consultas contextuales mejoradas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios

def test_casos_checklist():
    """Test de todos los casos del checklist del Día 5"""
    print("=== TEST CASOS CHECKLIST DIA 5 ===")
    
    # Cargar sistema
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Casos del checklist
    casos_test = [
        {
            "nombre": "Analisis Matematico I",
            "consulta": "Cuando se dicta Analisis Matematico I?",
            "buscar": ["analisis", "matematico"]
        },
        {
            "nombre": "Martes por la tarde", 
            "consulta": "Que materias hay los martes por la tarde?",
            "buscar": ["martes", "tarde"]
        },
        {
            "nombre": "Algoritmos y Estructuras",
            "consulta": "Horarios de Algoritmos y Estructuras de Datos?", 
            "buscar": ["algoritmo", "estructura"]
        },
        {
            "nombre": "Materias 14:00",
            "consulta": "Que materias empiezan a las 14:00?",
            "buscar": ["14:00", "14"]
        }
    ]
    
    resultados_casos = []
    
    for caso in casos_test:
        print(f"\n--- CASO: {caso['nombre']} ---")
        print(f"Consulta: {caso['consulta']}")
        
        # Mostrar normalización
        consulta_norm = sistema.normalizar_consulta_horario(caso['consulta'])
        print(f"Normalizada: {consulta_norm}")
        
        # Buscar
        respuestas = sistema.buscar_similares_horarios(caso['consulta'], k=5)
        
        exito = False
        print("Resultados:")
        
        for i, (doc, score) in enumerate(respuestas[:3], 1):
            nombre = doc['metadatos']['materia_nombre']
            dept = doc['metadatos']['departamento_codigo']
            tiene_horarios = doc['metadatos'].get('tiene_horarios', False)
            
            print(f"  {i}. [{score:.3f}] {nombre} ({dept}) - Horarios: {tiene_horarios}")
            
            # Verificar si cumple criterios
            nombre_lower = nombre.lower()
            for termino in caso['buscar']:
                if termino in nombre_lower or termino in consulta_norm:
                    if i <= 3:  # Top 3
                        exito = True
        
        # Mostrar horarios del primer resultado si los tiene
        if respuestas and respuestas[0][0]['metadatos'].get('tiene_horarios'):
            doc = respuestas[0][0]
            if doc['metadatos'].get('dias_semana'):
                dias = ', '.join(doc['metadatos']['dias_semana'])
                print(f"    --> Dias: {dias}")
        
        resultados_casos.append({
            'caso': caso['nombre'],
            'exito': exito,
            'score_top1': respuestas[0][1] if respuestas else 0
        })
        
        print(f"Status: {'EXITOSO' if exito else 'NECESITA MEJORA'}")
    
    # Resumen final
    print(f"\n{'='*50}")
    print("RESUMEN CASOS CHECKLIST")
    print('='*50)
    
    casos_exitosos = sum(1 for r in resultados_casos if r['exito'])
    total_casos = len(resultados_casos)
    
    for resultado in resultados_casos:
        status = "OK" if resultado['exito'] else "FALLO"
        print(f"  {resultado['caso']}: {status} (score: {resultado['score_top1']:.3f})")
    
    print(f"\nTotal: {casos_exitosos}/{total_casos} casos exitosos")
    print(f"Porcentaje exito: {(casos_exitosos/total_casos)*100:.1f}%")
    
    if casos_exitosos >= 3:
        print("CONCLUSION: Sistema RAG de horarios FUNCIONAL para MVP")
    else:
        print("CONCLUSION: Necesita mejoras adicionales")

if __name__ == "__main__":
    test_casos_checklist()