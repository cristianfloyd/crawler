#!/usr/bin/env python3
"""
Validación Manual Simplificada - Sección 5.2
Sin caracteres especiales para evitar problemas de encoding
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sistema_embeddings_horarios import SistemaEmbeddingsHorarios
import time
import json
from datetime import datetime

def ejecutar_validacion_seccion_5_2():
    """Ejecuta todas las tareas de la sección 5.2"""
    print("VALIDACION MANUAL SECCION 5.2")
    print("="*50)
    
    sistema = SistemaEmbeddingsHorarios()
    inicio_carga = time.time()
    sistema.cargar_sistema_horarios()
    tiempo_carga = time.time() - inicio_carga
    
    resultados = {
        'tiempo_carga_s': round(tiempo_carga, 2),
        'fecha_validacion': datetime.now().isoformat()
    }
    
    # 5.2.1 - Verificar accuracy de 20 consultas aleatorias
    print("\n5.2.1 - ACCURACY 20 CONSULTAS ALEATORIAS")
    print("-"*40)
    
    consultas_test = [
        'analisis matematico', 'algoritmos estructuras datos', 'programacion',
        'calculo', 'algebra', 'fisica', 'matematica discreta', 'bases de datos',
        'cuando se dicta programacion', 'horarios de matematica', 'que hora calculo',
        'cursada de algoritmos', 'materias por la manana', 'clases de tarde',
        'que hay los lunes', 'martes por la tarde', 'miercoles a la manana',
        'materias a las 14:00', 'clases que empiezan a las 10', 'horarios instituto calculo'
    ]
    
    resultados_accuracy = []
    tiempo_total_consultas = 0
    
    for i, consulta in enumerate(consultas_test, 1):
        inicio = time.time()
        respuestas = sistema.buscar_similares_horarios(consulta, k=3)
        tiempo = time.time() - inicio
        tiempo_total_consultas += tiempo
        
        score = respuestas[0][1] if respuestas else 0
        accuracy = "ALTA" if score > 0.6 else "MEDIA" if score > 0.4 else "BAJA"
        
        resultado = {
            'consulta': consulta,
            'score': round(score, 3),
            'accuracy': accuracy,
            'tiempo_ms': round(tiempo * 1000, 1),
            'tiene_resultados': len(respuestas) > 0
        }
        resultados_accuracy.append(resultado)
        
        print(f"{i:2d}. '{consulta}' -> Score: {score:.3f} | {accuracy} | {tiempo*1000:.1f}ms")
        if respuestas:
            nombre = respuestas[0][0]['metadatos']['materia_nombre'][:50]
            print(f"    Top: {nombre}")
    
    exitosas = sum(1 for r in resultados_accuracy if r['accuracy'] in ['ALTA', 'MEDIA'])
    alta_accuracy = sum(1 for r in resultados_accuracy if r['accuracy'] == 'ALTA')
    tiempo_promedio = tiempo_total_consultas / len(consultas_test) * 1000
    
    print(f"\nRESUMEN:")
    print(f"  Consultas exitosas: {exitosas}/20 ({exitosas/20*100:.1f}%)")
    print(f"  Accuracy alta: {alta_accuracy}/20 ({alta_accuracy/20*100:.1f}%)")
    print(f"  Tiempo promedio: {tiempo_promedio:.1f}ms")
    
    resultados['accuracy_20_consultas'] = {
        'total': len(consultas_test),
        'exitosas': exitosas,
        'alta_accuracy': alta_accuracy,
        'porcentaje_exito': round(exitosas/20*100, 1),
        'tiempo_promedio_ms': round(tiempo_promedio, 1),
        'detalle': resultados_accuracy
    }
    
    # 5.2.2 - Comparar respuestas con fuentes originales
    print("\n5.2.2 - COMPARACION CON FUENTES ORIGINALES")
    print("-"*40)
    
    casos_verificacion = [
        {
            'consulta': 'Algoritmos y Estructuras de Datos',
            'departamento_esperado': 'DC',
            'debe_tener_horarios': True
        },
        {
            'consulta': 'Analisis Matematico I', 
            'departamento_esperado': 'DM',
            'debe_tener_horarios': True
        },
        {
            'consulta': 'Calculo',
            'departamento_esperado': 'IC',
            'debe_tener_horarios': True
        }
    ]
    
    verificaciones = []
    
    for caso in casos_verificacion:
        respuestas = sistema.buscar_similares_horarios(caso['consulta'], k=3)
        
        if respuestas:
            mejor = respuestas[0][0]
            dept = mejor['metadatos']['departamento_codigo']
            horarios = mejor['metadatos'].get('tiene_horarios', False)
            
            dept_ok = dept == caso['departamento_esperado']
            horarios_ok = horarios == caso['debe_tener_horarios']
            
            verificacion = {
                'consulta': caso['consulta'],
                'materia_encontrada': mejor['metadatos']['materia_nombre'],
                'dept_esperado': caso['departamento_esperado'],
                'dept_encontrado': dept,
                'dept_correcto': dept_ok,
                'horarios_correcto': horarios_ok,
                'score': round(respuestas[0][1], 3)
            }
            
            print(f"'{caso['consulta']}':")
            print(f"  Materia: {mejor['metadatos']['materia_nombre']}")
            print(f"  Departamento: {dept} ({'OK' if dept_ok else 'FALLO'})")
            print(f"  Horarios: {horarios} ({'OK' if horarios_ok else 'FALLO'})")
            print(f"  Score: {respuestas[0][1]:.3f}")
            
        verificaciones.append(verificacion)
    
    resultados['verificacion_fuentes'] = verificaciones
    
    # 5.2.3 - Identificar tipos de consultas que fallan
    print("\n5.2.3 - TIPOS DE CONSULTAS QUE FALLAN")
    print("-"*40)
    
    consultas_problematicas = [
        ('Materia Inexistente XYZ', 'INEXISTENTE'),
        ('materia', 'VAGA'),
        ('algoritnos', 'TIPOGRAFICO'),
        ('materias los sabados', 'SIN_DATOS'),
        ('mathematics analysis', 'IDIOMA')
    ]
    
    tipos_fallas = {}
    
    for consulta, tipo in consultas_problematicas:
        respuestas = sistema.buscar_similares_horarios(consulta, k=3)
        score = respuestas[0][1] if respuestas else 0
        
        if score < 0.3:
            resultado = 'FALLO'
        elif score < 0.5:
            resultado = 'DUDOSO'
        else:
            resultado = 'OK'
        
        if tipo not in tipos_fallas:
            tipos_fallas[tipo] = []
        tipos_fallas[tipo].append(resultado)
        
        print(f"Tipo {tipo}: '{consulta}' -> {resultado} (score: {score:.3f})")
    
    resultados['tipos_fallas'] = tipos_fallas
    
    # 5.2.4 - Medir tiempos de respuesta
    print("\n5.2.4 - TIEMPOS DE RESPUESTA")
    print("-"*40)
    
    consultas_benchmark = [
        'analisis matematico', 'algoritmos', 'programacion',
        'cuando se dicta calculo', 'materias los lunes', 'horarios tarde'
    ]
    
    tiempos = []
    
    for consulta in consultas_benchmark:
        tiempos_consulta = []
        for _ in range(3):  # 3 repeticiones
            inicio = time.time()
            sistema.buscar_similares_horarios(consulta, k=5)
            tiempo = time.time() - inicio
            tiempos_consulta.append(tiempo * 1000)
        
        tiempo_prom = sum(tiempos_consulta) / 3
        tiempos.append(tiempo_prom)
        print(f"'{consulta}': {tiempo_prom:.1f}ms")
    
    tiempo_prom_global = sum(tiempos) / len(tiempos)
    
    print(f"\nTiempo carga inicial: {tiempo_carga:.2f}s")
    print(f"Tiempo promedio consulta: {tiempo_prom_global:.1f}ms")
    
    evaluacion = "EXCELENTE" if tiempo_prom_global < 500 else "BUENO" if tiempo_prom_global < 1000 else "ACEPTABLE"
    print(f"Evaluacion performance: {evaluacion}")
    
    resultados['tiempos_respuesta'] = {
        'tiempo_carga_s': tiempo_carga,
        'tiempo_promedio_ms': round(tiempo_prom_global, 1),
        'evaluacion': evaluacion
    }
    
    # 5.2.5 - Evaluar calidad de respuestas
    print("\n5.2.5 - CALIDAD DE RESPUESTAS")
    print("-"*40)
    
    casos_calidad = [
        ('Analisis Matematico I', ['debe_contener_analisis', 'debe_tener_horarios']),
        ('materias los martes', ['debe_tener_horarios']),
        ('programacion', ['debe_ser_relevante'])
    ]
    
    evaluaciones = []
    
    for consulta, criterios in casos_calidad:
        respuestas = sistema.buscar_similares_horarios(consulta, k=3)
        
        if respuestas:
            mejor = respuestas[0][0]
            score = respuestas[0][1]
            nombre = mejor['metadatos']['materia_nombre'].lower()
            horarios = mejor['metadatos'].get('tiene_horarios', False)
            
            criterios_ok = 0
            for criterio in criterios:
                if criterio == 'debe_contener_analisis' and 'analisis' in nombre:
                    criterios_ok += 1
                elif criterio == 'debe_tener_horarios' and horarios:
                    criterios_ok += 1
                elif criterio == 'debe_ser_relevante' and score > 0.5:
                    criterios_ok += 1
            
            porcentaje = criterios_ok / len(criterios) * 100
            calidad = 'ALTA' if porcentaje >= 80 and score >= 0.6 else 'MEDIA' if porcentaje >= 60 else 'BAJA'
            
            evaluacion = {
                'consulta': consulta,
                'score': round(score, 3),
                'criterios_ok': criterios_ok,
                'total_criterios': len(criterios),
                'porcentaje': round(porcentaje, 1),
                'calidad': calidad
            }
            
            evaluaciones.append(evaluacion)
            
            print(f"'{consulta}': {calidad} ({criterios_ok}/{len(criterios)} criterios)")
            print(f"  Score: {score:.3f} | Materia: {mejor['metadatos']['materia_nombre'][:40]}")
    
    alta_calidad = sum(1 for e in evaluaciones if e['calidad'] == 'ALTA')
    print(f"\nRespuestas alta calidad: {alta_calidad}/{len(evaluaciones)} ({alta_calidad/len(evaluaciones)*100:.1f}%)")
    
    resultados['calidad_respuestas'] = {
        'evaluaciones': len(evaluaciones),
        'alta_calidad': alta_calidad,
        'porcentaje_alta': round(alta_calidad/len(evaluaciones)*100, 1),
        'detalle': evaluaciones
    }
    
    # Guardar reporte
    reporte_file = os.path.join(os.path.dirname(__file__), '..', 'reportes', 'validacion_manual_5_2.json')
    os.makedirs(os.path.dirname(reporte_file), exist_ok=True)
    
    with open(reporte_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print("VALIDACION MANUAL SECCION 5.2 COMPLETADA")
    print(f"Reporte guardado: {reporte_file}")
    print(f"{'='*50}")
    
    return resultados

if __name__ == "__main__":
    ejecutar_validacion_seccion_5_2()