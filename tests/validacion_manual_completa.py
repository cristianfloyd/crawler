#!/usr/bin/env python3
"""
Validación Manual Completa - Día 5 Sección 5.2
Verificación exhaustiva del sistema RAG según checklist

Tareas:
- Verificar accuracy de 20 consultas aleatorias
- Comparar respuestas con fuentes originales
- Identificar tipos de consultas que fallan
- Medir tiempos de respuesta
- Evaluar calidad de respuestas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios
import time
import json
from datetime import datetime
import random

def validacion_20_consultas_aleatorias():
    """5.2.1 - Verificar accuracy de 20 consultas aleatorias"""
    print("=== 5.2.1 VERIFICACION ACCURACY 20 CONSULTAS ALEATORIAS ===")
    
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # 20 consultas variadas para testing
    consultas_test = [
        # Consultas directas de materias
        "analisis matematico",
        "algoritmos y estructuras de datos", 
        "programacion",
        "calculo",
        "algebra",
        "fisica",
        "matematica discreta",
        "bases de datos",
        
        # Consultas contextuales
        "cuando se dicta programacion",
        "horarios de matematica",
        "que hora calculo",
        "cursada de algoritmos",
        
        # Consultas temporales
        "materias por la manana",
        "clases de tarde", 
        "que hay los lunes",
        "martes por la tarde",
        "miercoles a la manana",
        
        # Consultas específicas
        "materias a las 14:00",
        "clases que empiezan a las 10",
        "horarios instituto de calculo"
    ]
    
    resultados_accuracy = []
    
    print(f"Probando {len(consultas_test)} consultas aleatorias...")
    
    for i, consulta in enumerate(consultas_test, 1):
        print(f"\n--- Consulta {i}/20: '{consulta}' ---")
        
        inicio = time.time()
        respuestas = sistema.buscar_similares_horarios(consulta, k=3)
        tiempo_respuesta = time.time() - inicio
        
        # Evaluar accuracy básica
        tiene_resultados = len(respuestas) > 0
        score_promedio = sum(score for _, score in respuestas) / len(respuestas) if respuestas else 0
        mejor_score = respuestas[0][1] if respuestas else 0
        
        # Evaluar relevancia (heurística simple)
        palabras_consulta = consulta.lower().split()
        relevancia = 0
        
        if respuestas:
            mejor_respuesta = respuestas[0][0]
            nombre_materia = mejor_respuesta['metadatos']['materia_nombre'].lower()
            
            for palabra in palabras_consulta:
                if palabra in ['cuando', 'horarios', 'que', 'se', 'dicta', 'hay', 'los', 'por', 'la', 'a', 'las']:
                    continue  # Ignorar palabras contextuales
                if palabra in nombre_materia:
                    relevancia += 1
        
        accuracy = "ALTA" if mejor_score > 0.6 and relevancia > 0 else "MEDIA" if mejor_score > 0.4 else "BAJA"
        
        resultado = {
            'consulta': consulta,
            'tiene_resultados': tiene_resultados,
            'score_promedio': round(score_promedio, 3),
            'mejor_score': round(mejor_score, 3),
            'relevancia_palabras': relevancia,
            'accuracy': accuracy,
            'tiempo_ms': round(tiempo_respuesta * 1000, 1)
        }
        
        resultados_accuracy.append(resultado)
        
        print(f"  Score: {mejor_score:.3f} | Accuracy: {accuracy} | Tiempo: {tiempo_respuesta*1000:.1f}ms")
        if respuestas:
            print(f"  Top: {respuestas[0][0]['metadatos']['materia_nombre']}")
    
    # Estadísticas finales
    total_exitosas = sum(1 for r in resultados_accuracy if r['accuracy'] in ['ALTA', 'MEDIA'])
    alta_accuracy = sum(1 for r in resultados_accuracy if r['accuracy'] == 'ALTA')
    tiempo_promedio = sum(r['tiempo_ms'] for r in resultados_accuracy) / len(resultados_accuracy)
    
    print(f"\n--- RESUMEN ACCURACY 20 CONSULTAS ---")
    print(f"Consultas exitosas: {total_exitosas}/20 ({total_exitosas/20*100:.1f}%)")
    print(f"Accuracy alta: {alta_accuracy}/20 ({alta_accuracy/20*100:.1f}%)")
    print(f"Tiempo promedio: {tiempo_promedio:.1f}ms")
    
    return resultados_accuracy

def comparar_con_fuentes_originales():
    """5.2.2 - Comparar respuestas con fuentes originales"""
    print("\n=== 5.2.2 COMPARACION CON FUENTES ORIGINALES ===")
    
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Casos de verificación con fuentes conocidas
    casos_verificacion = [
        {
            'consulta': 'Algoritmos y Estructuras de Datos',
            'departamento_esperado': 'DC',
            'debe_tener_horarios': True,
            'fuente': 'https://www.dc.uba.ar/'
        },
        {
            'consulta': 'Analisis Matematico I',
            'departamento_esperado': 'DM', 
            'debe_tener_horarios': True,
            'fuente': 'https://web.dm.uba.ar/'
        },
        {
            'consulta': 'Calculo',
            'departamento_esperado': 'IC',
            'debe_tener_horarios': True,
            'fuente': 'https://ic.fcen.uba.ar/'
        }
    ]
    
    verificaciones = []
    
    for caso in casos_verificacion:
        print(f"\n--- Verificando: {caso['consulta']} ---")
        
        respuestas = sistema.buscar_similares_horarios(caso['consulta'], k=3)
        
        if respuestas:
            mejor_respuesta = respuestas[0][0]
            dept_encontrado = mejor_respuesta['metadatos']['departamento_codigo']
            tiene_horarios = mejor_respuesta['metadatos'].get('tiene_horarios', False)
            
            dept_correcto = dept_encontrado == caso['departamento_esperado']
            horarios_correcto = tiene_horarios == caso['debe_tener_horarios']
            
            verificacion = {
                'consulta': caso['consulta'],
                'materia_encontrada': mejor_respuesta['metadatos']['materia_nombre'],
                'departamento_esperado': caso['departamento_esperado'],
                'departamento_encontrado': dept_encontrado,
                'departamento_correcto': dept_correcto,
                'horarios_esperados': caso['debe_tener_horarios'],
                'horarios_encontrados': tiene_horarios,
                'horarios_correcto': horarios_correcto,
                'score': round(respuestas[0][1], 3),
                'fuente_original': caso['fuente']
            }
            
            print(f"  Materia: {mejor_respuesta['metadatos']['materia_nombre']}")
            print(f"  Departamento: {dept_encontrado} ({'✓' if dept_correcto else '✗'})")
            print(f"  Horarios: {tiene_horarios} ({'✓' if horarios_correcto else '✗'})")
            print(f"  Score: {respuestas[0][1]:.3f}")
            
        else:
            verificacion = {
                'consulta': caso['consulta'],
                'error': 'No se encontraron resultados'
            }
            print(f"  ERROR: No se encontraron resultados")
        
        verificaciones.append(verificacion)
    
    # Verificar que los datos están actualizados
    print(f"\n--- Verificación actualización de datos ---")
    total_documentos = len(sistema.documentos)
    con_horarios = sum(1 for doc in sistema.documentos if doc['metadatos'].get('tiene_horarios', False))
    
    print(f"Total documentos: {total_documentos}")
    print(f"Con horarios: {con_horarios}")
    print(f"Cobertura: {con_horarios/total_documentos*100:.1f}%")
    
    return verificaciones

def identificar_tipos_consultas_fallan():
    """5.2.3 - Identificar tipos de consultas que fallan"""
    print("\n=== 5.2.3 IDENTIFICAR TIPOS DE CONSULTAS QUE FALLAN ===")
    
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Consultas problemáticas para identificar fallas
    consultas_problematicas = [
        # Materias inexistentes
        ('Materia Inexistente XYZ', 'INEXISTENTE'),
        ('Programacion Cuantica Avanzada', 'INEXISTENTE'),
        
        # Consultas muy vagas
        ('materia', 'VAGA'),
        ('clase', 'VAGA'),
        ('cuando', 'VAGA'),
        
        # Consultas con errores tipográficos
        ('algoritnos', 'TIPOGRAFICO'),
        ('matematikca', 'TIPOGRAFICO'),
        ('analisis matematoco', 'TIPOGRAFICO'),
        
        # Consultas muy específicas sin datos
        ('que materias hay los sabados', 'SIN_DATOS'),
        ('clases a las 6 AM', 'SIN_DATOS'),
        ('materias online', 'SIN_DATOS'),
        
        # Consultas complejas
        ('materias que no tienen correlativas y se dictan los lunes', 'COMPLEJA'),
        ('diferencia entre analisis 1 y analisis 2', 'COMPLEJA'),
        
        # Consultas en otros idiomas
        ('mathematics analysis', 'IDIOMA'),
        ('algorithmes et structures', 'IDIOMA')
    ]
    
    tipos_fallas = {}
    consultas_analizadas = []
    
    for consulta, tipo_esperado in consultas_problematicas:
        print(f"\n--- Tipo {tipo_esperado}: '{consulta}' ---")
        
        inicio = time.time()
        respuestas = sistema.buscar_similares_horarios(consulta, k=3)
        tiempo = time.time() - inicio
        
        # Analizar respuesta
        if not respuestas:
            resultado = 'SIN_RESULTADOS'
        elif respuestas[0][1] < 0.3:
            resultado = 'SCORE_BAJO'
        elif respuestas[0][1] < 0.5:
            resultado = 'SCORE_MEDIO'
        else:
            resultado = 'SCORE_ALTO'
        
        analisis = {
            'consulta': consulta,
            'tipo_esperado': tipo_esperado,
            'resultado': resultado,
            'score_top': respuestas[0][1] if respuestas else 0,
            'tiempo_ms': round(tiempo * 1000, 1)
        }
        
        consultas_analizadas.append(analisis)
        
        if tipo_esperado not in tipos_fallas:
            tipos_fallas[tipo_esperado] = []
        tipos_fallas[tipo_esperado].append(resultado)
        
        print(f"  Resultado: {resultado}")
        if respuestas:
            print(f"  Score: {respuestas[0][1]:.3f}")
            print(f"  Top: {respuestas[0][0]['metadatos']['materia_nombre'][:50]}")
    
    # Resumen por tipo de falla
    print(f"\n--- RESUMEN TIPOS DE FALLAS ---")
    for tipo, resultados in tipos_fallas.items():
        problematicos = sum(1 for r in resultados if r in ['SIN_RESULTADOS', 'SCORE_BAJO'])
        total = len(resultados)
        print(f"{tipo}: {problematicos}/{total} problemáticas ({problematicos/total*100:.1f}%)")
    
    return consultas_analizadas

def medir_tiempos_respuesta_detallado():
    """5.2.4 - Medir tiempos de respuesta detallados"""
    print("\n=== 5.2.4 MEDICION DETALLADA TIEMPOS RESPUESTA ===")
    
    sistema = SistemaEmbeddingsHorarios()
    
    # Medir tiempo de carga inicial
    print("Midiendo tiempo de carga inicial...")
    inicio_carga = time.time()
    sistema.cargar_sistema_horarios()
    tiempo_carga = time.time() - inicio_carga
    
    print(f"Tiempo carga inicial: {tiempo_carga:.2f}s")
    
    # Consultas para benchmark
    consultas_benchmark = [
        'analisis matematico',
        'algoritmos estructuras datos',
        'programacion',
        'cuando se dicta calculo',
        'materias los lunes',
        'horarios por la tarde'
    ]
    
    tiempos = []
    
    print(f"\nMidiendo {len(consultas_benchmark)} consultas de benchmark...")
    
    for i, consulta in enumerate(consultas_benchmark, 1):
        # Múltiples ejecuciones para promedio
        tiempos_consulta = []
        
        for j in range(3):  # 3 ejecuciones por consulta
            inicio = time.time()
            respuestas = sistema.buscar_similares_horarios(consulta, k=5)
            tiempo = time.time() - inicio
            tiempos_consulta.append(tiempo * 1000)  # en ms
        
        tiempo_promedio = sum(tiempos_consulta) / len(tiempos_consulta)
        tiempo_min = min(tiempos_consulta)
        tiempo_max = max(tiempos_consulta)
        
        tiempos.append({
            'consulta': consulta,
            'promedio_ms': round(tiempo_promedio, 1),
            'min_ms': round(tiempo_min, 1),
            'max_ms': round(tiempo_max, 1),
            'resultados': len(respuestas)
        })
        
        print(f"  {i}. '{consulta}': {tiempo_promedio:.1f}ms (min: {tiempo_min:.1f}, max: {tiempo_max:.1f})")
    
    # Estadísticas generales
    tiempo_promedio_global = sum(t['promedio_ms'] for t in tiempos) / len(tiempos)
    tiempo_min_global = min(t['min_ms'] for t in tiempos)
    tiempo_max_global = max(t['max_ms'] for t in tiempos)
    
    print(f"\n--- ESTADISTICAS RENDIMIENTO ---")
    print(f"Tiempo carga inicial: {tiempo_carga:.2f}s")
    print(f"Tiempo promedio consulta: {tiempo_promedio_global:.1f}ms")
    print(f"Tiempo mínimo: {tiempo_min_global:.1f}ms")
    print(f"Tiempo máximo: {tiempo_max_global:.1f}ms")
    
    # Evaluación performance
    if tiempo_promedio_global < 500:
        evaluacion = "EXCELENTE"
    elif tiempo_promedio_global < 1000:
        evaluacion = "BUENO"
    elif tiempo_promedio_global < 2000:
        evaluacion = "ACEPTABLE"
    else:
        evaluacion = "NECESITA_MEJORA"
    
    print(f"Evaluación performance: {evaluacion}")
    
    return {
        'tiempo_carga_s': tiempo_carga,
        'tiempo_promedio_ms': tiempo_promedio_global,
        'tiempo_min_ms': tiempo_min_global,
        'tiempo_max_ms': tiempo_max_global,
        'evaluacion': evaluacion,
        'detalle_consultas': tiempos
    }

def evaluar_calidad_respuestas():
    """5.2.5 - Evaluar calidad de respuestas"""
    print("\n=== 5.2.5 EVALUACION CALIDAD RESPUESTAS ===")
    
    sistema = SistemaEmbeddingsHorarios()
    sistema.cargar_sistema_horarios()
    
    # Casos para evaluar calidad
    casos_calidad = [
        {
            'consulta': 'Analisis Matematico I',
            'criterios': ['debe_contener_analisis', 'debe_contener_matematico', 'debe_tener_horarios']
        },
        {
            'consulta': 'materias los martes',
            'criterios': ['debe_tener_horarios', 'debe_mencionar_dias']
        },
        {
            'consulta': 'programacion',
            'criterios': ['debe_ser_relevante', 'debe_tener_horarios']
        }
    ]
    
    evaluaciones = []
    
    for caso in casos_calidad:
        print(f"\n--- Evaluando: '{caso['consulta']}' ---")
        
        respuestas = sistema.buscar_similares_horarios(caso['consulta'], k=3)
        
        if not respuestas:
            evaluacion = {
                'consulta': caso['consulta'],
                'calidad': 'FALLO_SIN_RESULTADOS',
                'criterios_cumplidos': 0,
                'total_criterios': len(caso['criterios'])
            }
            print("  FALLO: Sin resultados")
            evaluaciones.append(evaluacion)
            continue
        
        mejor_respuesta = respuestas[0][0]
        score = respuestas[0][1]
        
        # Evaluar criterios
        criterios_cumplidos = 0
        
        nombre_materia = mejor_respuesta['metadatos']['materia_nombre'].lower()
        tiene_horarios = mejor_respuesta['metadatos'].get('tiene_horarios', False)
        dias_semana = mejor_respuesta['metadatos'].get('dias_semana', [])
        
        for criterio in caso['criterios']:
            cumple = False
            
            if criterio == 'debe_contener_analisis' and 'analisis' in nombre_materia:
                cumple = True
            elif criterio == 'debe_contener_matematico' and 'matematico' in nombre_materia:
                cumple = True
            elif criterio == 'debe_tener_horarios' and tiene_horarios:
                cumple = True
            elif criterio == 'debe_mencionar_dias' and dias_semana:
                cumple = True
            elif criterio == 'debe_ser_relevante' and score > 0.5:
                cumple = True
            
            if cumple:
                criterios_cumplidos += 1
            
            print(f"  {criterio}: {'✓' if cumple else '✗'}")
        
        # Calidad general
        porcentaje_criterios = criterios_cumplidos / len(caso['criterios'])
        
        if porcentaje_criterios >= 0.8 and score >= 0.6:
            calidad = 'ALTA'
        elif porcentaje_criterios >= 0.6 and score >= 0.4:
            calidad = 'MEDIA'
        else:
            calidad = 'BAJA'
        
        evaluacion = {
            'consulta': caso['consulta'],
            'materia_encontrada': mejor_respuesta['metadatos']['materia_nombre'],
            'score': round(score, 3),
            'criterios_cumplidos': criterios_cumplidos,
            'total_criterios': len(caso['criterios']),
            'porcentaje_criterios': round(porcentaje_criterios * 100, 1),
            'calidad': calidad
        }
        
        evaluaciones.append(evaluacion)
        
        print(f"  Materia: {mejor_respuesta['metadatos']['materia_nombre']}")
        print(f"  Score: {score:.3f}")
        print(f"  Criterios: {criterios_cumplidos}/{len(caso['criterios'])} ({porcentaje_criterios*100:.1f}%)")
        print(f"  Calidad: {calidad}")
    
    # Estadísticas finales de calidad
    alta_calidad = sum(1 for e in evaluaciones if e['calidad'] == 'ALTA')
    total_evaluaciones = len(evaluaciones)
    
    print(f"\n--- RESUMEN CALIDAD ---")
    print(f"Respuestas alta calidad: {alta_calidad}/{total_evaluaciones} ({alta_calidad/total_evaluaciones*100:.1f}%)")
    
    return evaluaciones

def generar_reporte_validacion_manual():
    """Genera reporte completo de validación manual"""
    print("="*60)
    print("INICIANDO VALIDACION MANUAL COMPLETA - SECCION 5.2")
    print("="*60)
    
    # Ejecutar todas las validaciones
    inicio_total = time.time()
    
    accuracy_results = validacion_20_consultas_aleatorias()
    verificacion_fuentes = comparar_con_fuentes_originales()
    analisis_fallas = identificar_tipos_consultas_fallan()
    tiempos_respuesta = medir_tiempos_respuesta_detallado()
    calidad_respuestas = evaluar_calidad_respuestas()
    
    tiempo_total = time.time() - inicio_total
    
    # Compilar reporte final
    reporte_completo = {
        'validacion_manual_seccion_5_2': {
            'fecha_validacion': datetime.now().isoformat(),
            'tiempo_total_validacion_s': round(tiempo_total, 2),
            
            'accuracy_20_consultas': {
                'total_consultas': len(accuracy_results),
                'consultas_exitosas': sum(1 for r in accuracy_results if r['accuracy'] in ['ALTA', 'MEDIA']),
                'porcentaje_exito': round(sum(1 for r in accuracy_results if r['accuracy'] in ['ALTA', 'MEDIA']) / len(accuracy_results) * 100, 1),
                'tiempo_promedio_ms': round(sum(r['tiempo_ms'] for r in accuracy_results) / len(accuracy_results), 1),
                'detalle': accuracy_results
            },
            
            'comparacion_fuentes_originales': {
                'verificaciones_realizadas': len(verificacion_fuentes),
                'verificaciones_exitosas': sum(1 for v in verificacion_fuentes if v.get('departamento_correcto', False) and v.get('horarios_correcto', False)),
                'detalle': verificacion_fuentes
            },
            
            'tipos_consultas_problematicas': {
                'consultas_analizadas': len(analisis_fallas),
                'tipos_identificados': list(set(a['tipo_esperado'] for a in analisis_fallas)),
                'detalle': analisis_fallas
            },
            
            'tiempos_respuesta': tiempos_respuesta,
            
            'calidad_respuestas': {
                'evaluaciones_realizadas': len(calidad_respuestas),
                'alta_calidad': sum(1 for e in calidad_respuestas if e['calidad'] == 'ALTA'),
                'porcentaje_alta_calidad': round(sum(1 for e in calidad_respuestas if e['calidad'] == 'ALTA') / len(calidad_respuestas) * 100, 1),
                'detalle': calidad_respuestas
            }
        }
    }
    
    # Guardar reporte
    reporte_file = os.path.join(os.path.dirname(__file__), '..', 'reportes', 'validacion_manual_seccion_5_2.json')
    os.makedirs(os.path.dirname(reporte_file), exist_ok=True)
    
    with open(reporte_file, 'w', encoding='utf-8') as f:
        json.dump(reporte_completo, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("VALIDACION MANUAL COMPLETADA")
    print(f"{'='*60}")
    print(f"Tiempo total: {tiempo_total:.2f}s")
    print(f"Reporte guardado en: {reporte_file}")
    
    return reporte_completo

if __name__ == "__main__":
    generar_reporte_validacion_manual()