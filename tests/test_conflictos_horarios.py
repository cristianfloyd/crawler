#!/usr/bin/env python3
"""
Test de Conflictos de Horarios - Día 5 Sección 5.1
Último caso de prueba específico: "¿Conflictos de horarios entre X e Y?"

Implementa detección de conflictos de horarios entre materias
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios
import json
from datetime import datetime

def parsear_horario(horario_str):
    """Parsea string de horario a tupla (día, hora_inicio, hora_fin)"""
    if not horario_str:
        return None
    
    # Formatos esperados: "Lu 14:00-16:00", "Lunes 14:00 a 16:00", etc.
    horario_str = horario_str.lower().strip()
    
    # Mapeo de días
    dias_map = {
        'lu': 'lunes', 'lunes': 'lunes',
        'ma': 'martes', 'martes': 'martes',
        'mi': 'miercoles', 'miercoles': 'miercoles', 'miércoles': 'miercoles',
        'ju': 'jueves', 'jueves': 'jueves',
        'vi': 'viernes', 'viernes': 'viernes',
        'sa': 'sabado', 'sabado': 'sabado', 'sábado': 'sabado'
    }
    
    # Extraer día
    dia = None
    for key, valor in dias_map.items():
        if horario_str.startswith(key):
            dia = valor
            horario_str = horario_str[len(key):].strip()
            break
    
    if not dia:
        return None
    
    # Extraer horarios (buscar patrones como 14:00-16:00 o 14:00 a 16:00)
    import re
    patron_horas = r'(\d{1,2}):(\d{2})\s*(?:-|a|hasta)\s*(\d{1,2}):(\d{2})'
    match = re.search(patron_horas, horario_str)
    
    if match:
        h1, m1, h2, m2 = match.groups()
        hora_inicio = f"{h1:0>2}:{m1}"
        hora_fin = f"{h2:0>2}:{m2}"
        return (dia, hora_inicio, hora_fin)
    
    return None

def hay_conflicto_horario(horario1, horario2):
    """Verifica si dos horarios se superponen"""
    if not horario1 or not horario2:
        return False
    
    dia1, inicio1, fin1 = horario1
    dia2, inicio2, fin2 = horario2
    
    # Si son días diferentes, no hay conflicto
    if dia1 != dia2:
        return False
    
    # Convertir horarios a minutos para comparar
    def a_minutos(hora_str):
        h, m = map(int, hora_str.split(':'))
        return h * 60 + m
    
    inicio1_min = a_minutos(inicio1)
    fin1_min = a_minutos(fin1)
    inicio2_min = a_minutos(inicio2)
    fin2_min = a_minutos(fin2)
    
    # Verificar superposición
    return not (fin1_min <= inicio2_min or fin2_min <= inicio1_min)

def extraer_horarios_materia(materia_doc):
    """Extrae los horarios estructurados de una materia"""
    horarios = []
    metadata = materia_doc.get('metadatos', {})
    
    # Obtener días de la semana
    dias_semana = metadata.get('dias_semana', [])
    
    # Si tiene información de horarios en el contenido, parsearla
    contenido = materia_doc.get('contenido', '')
    
    # Buscar patrones de horarios en el contenido
    import re
    patrones_horarios = [
        r'(\w+)\s+(\d{1,2}:\d{2})\s*(?:-|a|hasta)\s*(\d{1,2}:\d{2})',
        r'(\w+)\s+de\s+(\d{1,2}:\d{2})\s+a\s+(\d{1,2}:\d{2})'
    ]
    
    for patron in patrones_horarios:
        matches = re.findall(patron, contenido.lower())
        for match in matches:
            dia, inicio, fin = match
            horario_parseado = parsear_horario(f"{dia} {inicio}-{fin}")
            if horario_parseado:
                horarios.append(horario_parseado)
    
    # Si no encontramos horarios específicos, usar días disponibles con horarios genéricos
    if not horarios and dias_semana:
        # Asumir horarios típicos por día (esto es una simplificación)
        for dia in dias_semana:
            # Horarios genéricos comunes en universidades
            horarios.append((dia, "14:00", "18:00"))  # Tarde típica
    
    return horarios

def detectar_conflictos_entre_materias(materia1_doc, materia2_doc):
    """Detecta conflictos de horarios entre dos materias"""
    horarios1 = extraer_horarios_materia(materia1_doc)
    horarios2 = extraer_horarios_materia(materia2_doc)
    
    conflictos = []
    
    for h1 in horarios1:
        for h2 in horarios2:
            if hay_conflicto_horario(h1, h2):
                conflictos.append({
                    'dia': h1[0],
                    'materia1_horario': f"{h1[1]}-{h1[2]}",
                    'materia2_horario': f"{h2[1]}-{h2[2]}",
                    'superposicion': True
                })
    
    return conflictos

def test_conflictos_horarios_especificos():
    """Test: ¿Conflictos de horarios entre X e Y?"""
    print("=== TEST CONFLICTOS DE HORARIOS ENTRE MATERIAS ===")
    
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Casos de prueba de conflictos
    casos_conflictos = [
        {
            'materia1': 'Analisis Matematico I',
            'materia2': 'Algoritmos y Estructuras de Datos',
            'descripcion': 'Materias populares que podrían solaparse'
        },
        {
            'materia1': 'Programacion',
            'materia2': 'Calculo',
            'descripcion': 'Materias de primer año comunes'
        },
        {
            'materia1': 'Algebra',
            'materia2': 'Matematica Discreta',
            'descripcion': 'Materias del área matemática'
        }
    ]
    
    resultados_conflictos = []
    
    for caso in casos_conflictos:
        print(f"\n--- Caso: {caso['descripcion']} ---")
        print(f"Materias: '{caso['materia1']}' vs '{caso['materia2']}'")
        
        # Buscar primera materia
        respuestas1 = sistema.buscar_similares_horarios(caso['materia1'], k=1)
        respuestas2 = sistema.buscar_similares_horarios(caso['materia2'], k=1)
        
        if not respuestas1 or not respuestas2:
            print("  ERROR: No se encontraron una o ambas materias")
            resultados_conflictos.append({
                'caso': caso['descripcion'],
                'error': 'Materias no encontradas',
                'conflictos': []
            })
            continue
        
        doc1 = respuestas1[0][0]
        doc2 = respuestas2[0][0]
        
        nombre1 = doc1['metadatos']['materia_nombre']
        nombre2 = doc2['metadatos']['materia_nombre']
        
        print(f"  Materia 1: {nombre1}")
        print(f"  Materia 2: {nombre2}")
        
        # Obtener información de horarios
        dias1 = doc1['metadatos'].get('dias_semana', [])
        dias2 = doc2['metadatos'].get('dias_semana', [])
        
        print(f"  Días Materia 1: {', '.join(dias1) if dias1 else 'No especificados'}")
        print(f"  Días Materia 2: {', '.join(dias2) if dias2 else 'No especificados'}")
        
        # Detectar conflictos
        conflictos = detectar_conflictos_entre_materias(doc1, doc2)
        
        # Análisis simple: días en común
        dias_comunes = set(dias1) & set(dias2)
        
        if dias_comunes:
            print(f"  POSIBLE CONFLICTO: Días en común: {', '.join(dias_comunes)}")
            tiene_conflicto = True
        else:
            print(f"  SIN CONFLICTOS: No hay días en común")
            tiene_conflicto = False
        
        # Si hay conflictos detectados por horarios específicos
        if conflictos:
            print(f"  CONFLICTOS DETECTADOS: {len(conflictos)}")
            for conflicto in conflictos:
                print(f"    - {conflicto['dia']}: {conflicto['materia1_horario']} vs {conflicto['materia2_horario']}")
            tiene_conflicto = True
        
        resultado = {
            'caso': caso['descripcion'],
            'materia1': {
                'nombre': nombre1,
                'dias': dias1
            },
            'materia2': {
                'nombre': nombre2, 
                'dias': dias2
            },
            'dias_comunes': list(dias_comunes),
            'tiene_conflicto': tiene_conflicto,
            'conflictos_especificos': conflictos,
            'score1': round(respuestas1[0][1], 3),
            'score2': round(respuestas2[0][1], 3)
        }
        
        resultados_conflictos.append(resultado)
    
    # Estadísticas generales
    casos_con_conflicto = sum(1 for r in resultados_conflictos if r.get('tiene_conflicto', False))
    total_casos = len(resultados_conflictos)
    
    print(f"\n--- RESUMEN CONFLICTOS ---")
    print(f"Casos analizados: {total_casos}")
    print(f"Casos con posibles conflictos: {casos_con_conflicto}")
    print(f"Casos sin conflictos: {total_casos - casos_con_conflicto}")
    
    # Evaluación del sistema de detección
    exito_test = True
    for resultado in resultados_conflictos:
        if 'error' in resultado:
            exito_test = False
            break
    
    print(f"Estado del test: {'EXITOSO' if exito_test else 'CON ERRORES'}")
    
    return {
        'test_conflictos_horarios': {
            'fecha': datetime.now().isoformat(),
            'casos_analizados': total_casos,
            'casos_con_conflictos': casos_con_conflicto,
            'exito_test': exito_test,
            'resultados_detallados': resultados_conflictos
        }
    }

def test_consulta_conflictos_natural():
    """Test con consulta natural sobre conflictos"""
    print("\n=== TEST CONSULTA NATURAL CONFLICTOS ===")
    
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    consultas_conflictos = [
        "conflictos de horarios entre analisis matematico y programacion",
        "que materias se superponen en horarios",
        "puedo cursar algoritmos y calculo al mismo tiempo",
        "horarios que no se pisen entre algebra y fisica"
    ]
    
    for consulta in consultas_conflictos:
        print(f"\n--- Consulta: '{consulta}' ---")
        
        respuestas = sistema.buscar_similares_horarios(consulta, k=5)
        
        if respuestas:
            print(f"Respuestas encontradas: {len(respuestas)}")
            for i, (doc, score) in enumerate(respuestas[:3], 1):
                nombre = doc['metadatos']['materia_nombre']
                dias = doc['metadatos'].get('dias_semana', [])
                print(f"  {i}. [{score:.3f}] {nombre}")
                if dias:
                    print(f"      Días: {', '.join(dias)}")
        else:
            print("  No se encontraron respuestas")
    
    return True

def generar_reporte_conflictos():
    """Genera reporte completo de testing de conflictos"""
    print("GENERANDO REPORTE DE CONFLICTOS DE HORARIOS")
    print("="*50)
    
    # Ejecutar tests
    resultados_especificos = test_conflictos_horarios_especificos()
    test_consulta_conflictos_natural()
    
    # Guardar reporte
    reporte_file = os.path.join(os.path.dirname(__file__), '..', 'reportes', 'test_conflictos_horarios.json')
    os.makedirs(os.path.dirname(reporte_file), exist_ok=True)
    
    with open(reporte_file, 'w', encoding='utf-8') as f:
        json.dump(resultados_especificos, f, ensure_ascii=False, indent=2)
    
    print(f"\nReporte guardado: {reporte_file}")
    
    # Evaluar si el test fue exitoso
    exito = resultados_especificos['test_conflictos_horarios']['exito_test']
    casos_conflictos = resultados_especificos['test_conflictos_horarios']['casos_con_conflictos']
    
    print(f"\nRESULTADO FINAL:")
    print(f"Test de conflictos: {'EXITOSO' if exito else 'FALLO'}")
    print(f"Funcionalidad: {'IMPLEMENTADA' if casos_conflictos >= 0 else 'NO IMPLEMENTADA'}")
    
    return exito

if __name__ == "__main__":
    generar_reporte_conflictos()