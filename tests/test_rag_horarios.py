#!/usr/bin/env python3
"""
Test completo del Sistema RAG de Horarios - Día 4
Validación del funcionamiento del sistema RAG especializado

Autor: Sistema RAG MVP
Fecha: 2025-07-27
"""

import sys
import os
from consultar_horarios_rag import ConsultorHorarios
import logging

# Configuración de logging
logging.basicConfig(level=logging.WARNING)

class TestRAGHorarios:
    """Clase para probar el sistema RAG de horarios"""
    
    def __init__(self):
        self.consultor = ConsultorHorarios()
        self.resultados_tests = []
        
    def ejecutar_test(self, nombre_test: str, consulta: str, criterios_exito: dict):
        """Ejecuta un test específico"""
        print(f"\n🧪 TEST: {nombre_test}")
        print(f"📝 Consulta: '{consulta}'")
        print("-" * 50)
        
        try:
            resultados = self.consultor.procesar_consulta(consulta, k=5)
            
            # Evaluar criterios de éxito
            exito = True
            detalles = {}
            
            # Criterio: Mínimo de resultados
            if 'min_resultados' in criterios_exito:
                min_req = criterios_exito['min_resultados']
                detalles['resultados_encontrados'] = len(resultados)
                if len(resultados) < min_req:
                    exito = False
                    detalles['error_min_resultados'] = f"Se esperaban al menos {min_req}, se encontraron {len(resultados)}"
            
            # Criterio: Resultados con horarios
            if 'debe_tener_horarios' in criterios_exito and criterios_exito['debe_tener_horarios']:
                con_horarios = sum(1 for r in resultados if r['tiene_horarios'])
                detalles['con_horarios'] = con_horarios
                if con_horarios == 0:
                    exito = False
                    detalles['error_horarios'] = "Ningún resultado tiene horarios"
            
            # Criterio: Score mínimo
            if 'score_minimo' in criterios_exito and resultados:
                mejor_score = max(r['score'] for r in resultados)
                detalles['mejor_score'] = mejor_score
                if mejor_score < criterios_exito['score_minimo']:
                    exito = False
                    detalles['error_score'] = f"Score máximo {mejor_score:.3f} < {criterios_exito['score_minimo']}"
            
            # Criterio: Contiene palabras clave
            if 'debe_contener' in criterios_exito:
                palabras = criterios_exito['debe_contener']
                encontradas = []
                for palabra in palabras:
                    for resultado in resultados:
                        nombre = resultado['nombre'].lower()
                        if palabra.lower() in nombre:
                            encontradas.append(palabra)
                            break
                
                detalles['palabras_encontradas'] = encontradas
                if len(encontradas) != len(palabras):
                    faltantes = set(palabras) - set(encontradas)
                    detalles['palabras_faltantes'] = list(faltantes)
            
            # Mostrar resultados
            if resultados:
                print(f"✅ {len(resultados)} resultados encontrados:")
                for i, resultado in enumerate(resultados[:3], 1):
                    nombre = resultado['nombre']
                    score = resultado['score']
                    tiene_horarios = "🕐" if resultado['tiene_horarios'] else "❌"
                    dept = resultado['codigo_dept']
                    print(f"   {i}. [{score:.3f}] {tiene_horarios} {nombre} ({dept})")
                    
                    # Mostrar primer horario si existe
                    if resultado['horarios']:
                        h = resultado['horarios'][0]
                        print(f"      📅 {h['dia']}: {h['hora_inicio']}-{h['hora_fin']}")
            else:
                print("❌ No se encontraron resultados")
                exito = False
            
            # Resultado del test
            self.resultados_tests.append({
                'nombre': nombre_test,
                'consulta': consulta,
                'exito': exito,
                'detalles': detalles,
                'resultados': len(resultados)
            })
            
            if exito:
                print(f"🎉 TEST EXITOSO")
            else:
                print(f"❌ TEST FALLIDO: {detalles}")
            
            return exito
            
        except Exception as e:
            print(f"💥 ERROR EN TEST: {e}")
            self.resultados_tests.append({
                'nombre': nombre_test,
                'consulta': consulta,
                'exito': False,
                'detalles': {'error': str(e)},
                'resultados': 0
            })
            return False

    def ejecutar_bateria_tests(self):
        """Ejecuta batería completa de tests"""
        print("🧪 EJECUTANDO BATERÍA DE TESTS DEL SISTEMA RAG DE HORARIOS")
        print("=" * 70)
        
        # Test 1: Consulta básica de materia específica
        self.ejecutar_test(
            "Consulta materia específica",
            "¿Cuándo se dicta Análisis Matemático?",
            {
                'min_resultados': 1,
                'debe_tener_horarios': True,
                'score_minimo': 0.3,
                'debe_contener': ['análisis', 'matemático']
            }
        )
        
        # Test 2: Consulta por día específico
        self.ejecutar_test(
            "Búsqueda por día",
            "¿Qué materias hay los lunes?",
            {
                'min_resultados': 2,
                'debe_tener_horarios': True,
                'score_minimo': 0.2
            }
        )
        
        # Test 3: Consulta por franja horaria
        self.ejecutar_test(
            "Búsqueda por franja horaria",
            "¿Materias por la mañana?",
            {
                'min_resultados': 1,
                'debe_tener_horarios': True,
                'score_minimo': 0.2
            }
        )
        
        # Test 4: Consulta de algoritmos/programación
        self.ejecutar_test(
            "Materia de programación",
            "Horarios de Algoritmos y Estructuras de Datos",
            {
                'min_resultados': 1,
                'debe_tener_horarios': False,  # Puede no tener horarios
                'score_minimo': 0.3,
                'debe_contener': ['algoritmos']
            }
        )
        
        # Test 5: Consulta por departamento
        self.ejecutar_test(
            "Búsqueda por departamento",
            "Materias del Departamento de Computación",
            {
                'min_resultados': 3,
                'score_minimo': 0.2
            }
        )
        
        # Test 6: Consulta de estadística
        self.ejecutar_test(
            "Materia de estadística",
            "¿Cuándo se dicta Estadística?",
            {
                'min_resultados': 1,
                'debe_tener_horarios': True,
                'score_minimo': 0.3,
                'debe_contener': ['estadística']
            }
        )
        
        # Test 7: Consulta específica de día y hora
        self.ejecutar_test(
            "Día y franja específica",
            "¿Qué hay los viernes por la tarde?",
            {
                'min_resultados': 1,
                'score_minimo': 0.2
            }
        )
        
        # Test 8: Consulta de materias nocturnas
        self.ejecutar_test(
            "Clases nocturnas",
            "¿Hay clases de noche?",
            {
                'min_resultados': 1,
                'score_minimo': 0.2
            }
        )

    def generar_reporte_final(self):
        """Genera reporte final de los tests"""
        print("\n" + "=" * 70)
        print("📊 REPORTE FINAL DE TESTS")
        print("=" * 70)
        
        total_tests = len(self.resultados_tests)
        tests_exitosos = sum(1 for t in self.resultados_tests if t['exito'])
        tests_fallidos = total_tests - tests_exitosos
        
        print(f"📈 RESUMEN:")
        print(f"   • Total tests: {total_tests}")
        print(f"   • Exitosos: {tests_exitosos} ({tests_exitosos/total_tests*100:.1f}%)")
        print(f"   • Fallidos: {tests_fallidos} ({tests_fallidos/total_tests*100:.1f}%)")
        
        if tests_fallidos > 0:
            print(f"\n❌ TESTS FALLIDOS:")
            for test in self.resultados_tests:
                if not test['exito']:
                    print(f"   • {test['nombre']}: {test['consulta']}")
                    if 'error' in test['detalles']:
                        print(f"     Error: {test['detalles']['error']}")
        
        print(f"\n✅ TESTS EXITOSOS:")
        for test in self.resultados_tests:
            if test['exito']:
                print(f"   • {test['nombre']}: {test['resultados']} resultados")
        
        # Evaluación general
        if tests_exitosos >= total_tests * 0.8:  # 80% de éxito
            print(f"\n🎉 SISTEMA RAG DE HORARIOS: ¡FUNCIONANDO CORRECTAMENTE!")
            print(f"   El sistema supera el 80% de éxito en las pruebas")
            return True
        else:
            print(f"\n⚠️  SISTEMA RAG DE HORARIOS: NECESITA MEJORAS")
            print(f"   El sistema no alcanza el 80% de éxito requerido")
            return False

    def ejecutar_tests_completos(self):
        """Ejecuta todos los tests y genera reporte"""
        # Cargar sistema
        print("🔄 Cargando sistema RAG de horarios...")
        if not self.consultor.cargar_sistema():
            print("❌ No se pudo cargar el sistema RAG")
            return False
        
        # Ejecutar tests
        self.ejecutar_bateria_tests()
        
        # Generar reporte
        return self.generar_reporte_final()


def main():
    """Función principal"""
    print("🤖 TEST COMPLETO DEL SISTEMA RAG DE HORARIOS")
    print("Sistema de validación para el MVP RAG con consultas de horarios")
    print("=" * 70)
    
    tester = TestRAGHorarios()
    
    # Ejecutar tests completos
    exito = tester.ejecutar_tests_completos()
    
    # Salir con código apropiado
    if exito:
        print(f"\n✅ Todos los tests completados exitosamente")
        sys.exit(0)
    else:
        print(f"\n❌ Algunos tests fallaron")
        sys.exit(1)


if __name__ == "__main__":
    main()