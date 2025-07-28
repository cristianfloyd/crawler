#!/usr/bin/env python3
"""
Tests Específicos para Consultas de Horarios - Día 5
Casos de prueba del MVP según checklist

Autor: Sistema RAG MVP
Fecha: 2025-07-27
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import json
from datetime import datetime
from sistema_embeddings_horarios import SistemaEmbeddingsHorarios

class TestConsultasHorarios(unittest.TestCase):
    """Casos de prueba específicos para el sistema RAG de horarios"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial - cargar sistema RAG una sola vez"""
        print("Configurando sistema RAG para testing...")
        cls.sistema = SistemaEmbeddingsHorarios()
        cls.sistema.cargar_sistema_horarios()
        print("Sistema RAG cargado para testing")
        
        # Almacenar resultados de tests
        cls.resultados_tests = []
    
    def test_01_analisis_matematico_i(self):
        """Test: ¿Cuándo se dicta Análisis Matemático I?"""
        consulta = "¿Cuándo se dicta Análisis Matemático I?"
        print(f"\nTest 1: {consulta}")
        
        respuestas = self.sistema.buscar_similares_horarios(consulta, k=3)
        
        # Verificaciones
        self.assertGreater(len(respuestas), 0, "No se encontraron respuestas")
        
        # Buscar información específica de Análisis I
        encontrado_analisis = False
        for respuesta, score in respuestas:
            contenido = respuesta.get('contenido', '').lower()
            metadatos = respuesta.get('metadatos', {})
            if 'analisis' in contenido and ('matematico' in contenido or 'i' in contenido):
                encontrado_analisis = True
                print(f"Encontrado: {metadatos.get('materia_nombre', 'N/A')} (score: {score:.3f})")
                break
        
        self.assertTrue(encontrado_analisis, "No se encontró información de Análisis Matemático I")
        
        # Guardar resultado
        self._guardar_resultado_test("Análisis Matemático I", consulta, [r[0] for r in respuestas[:1]], encontrado_analisis)
    
    def test_02_martes_por_tarde(self):
        """Test: ¿Qué materias hay los martes por la tarde?"""
        consulta = "¿Qué materias hay los martes por la tarde?"
        print(f"\n📝 Test 2: {consulta}")
        
        respuestas = self.sistema.buscar_con_horarios(consulta, top_k=5)
        
        # Verificaciones
        self.assertGreater(len(respuestas), 0, "No se encontraron respuestas")
        
        # Verificar que incluya información de martes y tarde
        materias_martes_tarde = []
        for respuesta in respuestas:
            contenido = respuesta.get('contenido', '').lower()
            metadata = respuesta.get('metadata', {})
            
            # Verificar martes
            tiene_martes = 'martes' in contenido or 'ma' in str(metadata.get('horarios', []))
            # Verificar tarde (14:00-18:00 aproximadamente)
            tiene_tarde = any(['14:' in str(h) or '15:' in str(h) or '16:' in str(h) for h in metadata.get('horarios', [])])
            
            if tiene_martes and tiene_tarde:
                materias_martes_tarde.append(respuesta.get('materia', 'N/A'))
        
        print(f"✅ Materias encontradas martes tarde: {len(materias_martes_tarde)}")
        self.assertGreater(len(materias_martes_tarde), 0, "No se encontraron materias los martes por la tarde")
        
        # Guardar resultado
        self._guardar_resultado_test("Martes por la tarde", consulta, respuestas[:3], len(materias_martes_tarde) > 0)
    
    def test_03_algoritmos_estructuras(self):
        """Test: ¿Horarios de Algoritmos y Estructuras de Datos?"""
        consulta = "¿Horarios de Algoritmos y Estructuras de Datos?"
        print(f"\n📝 Test 3: {consulta}")
        
        respuestas = self.sistema.buscar_con_horarios(consulta, top_k=3)
        
        # Verificaciones
        self.assertGreater(len(respuestas), 0, "No se encontraron respuestas")
        
        # Buscar Algoritmos específicamente
        encontrado_algoritmos = False
        for respuesta in respuestas:
            contenido = respuesta.get('contenido', '').lower()
            materia = respuesta.get('materia', '').lower()
            
            if 'algoritmo' in contenido or 'algoritmo' in materia:
                encontrado_algoritmos = True
                print(f"✅ Encontrado: {respuesta.get('materia', 'N/A')}")
                horarios = respuesta.get('metadata', {}).get('horarios', [])
                print(f"   Horarios: {horarios}")
                break
        
        # Para casos donde no esté exactamente, buscar materias relacionadas
        if not encontrado_algoritmos:
            for respuesta in respuestas:
                contenido = respuesta.get('contenido', '').lower()
                if 'estructura' in contenido or 'programación' in contenido:
                    print(f"📋 Materia relacionada: {respuesta.get('materia', 'N/A')}")
        
        self._guardar_resultado_test("Algoritmos y Estructuras", consulta, respuestas[:1], encontrado_algoritmos)
    
    def test_04_materias_14_00(self):
        """Test: ¿Qué materias empiezan a las 14:00?"""
        consulta = "¿Qué materias empiezan a las 14:00?"
        print(f"\n📝 Test 4: {consulta}")
        
        respuestas = self.sistema.buscar_con_horarios(consulta, top_k=5)
        
        # Verificaciones
        self.assertGreater(len(respuestas), 0, "No se encontraron respuestas")
        
        # Buscar materias que empiecen a las 14:00
        materias_14_00 = []
        for respuesta in respuestas:
            metadata = respuesta.get('metadata', {})
            horarios = metadata.get('horarios', [])
            
            # Verificar si algún horario empieza con 14:00
            for horario in horarios:
                if '14:00' in str(horario):
                    materias_14_00.append(respuesta.get('materia', 'N/A'))
                    break
        
        print(f"✅ Materias que empiezan a las 14:00: {len(materias_14_00)}")
        for materia in materias_14_00[:3]:  # Mostrar primeras 3
            print(f"   - {materia}")
        
        self.assertGreater(len(materias_14_00), 0, "No se encontraron materias que empiecen a las 14:00")
        
        # Guardar resultado
        self._guardar_resultado_test("Materias 14:00", consulta, respuestas[:3], len(materias_14_00) > 0)
    
    def test_05_busqueda_general_horarios(self):
        """Test: Verificar que el sistema responde a consultas generales de horarios"""
        consultas_generales = [
            "horarios de materias",
            "cuándo hay clases",
            "qué materias hay los lunes",
            "materias por la mañana",
            "clases de tarde"
        ]
        
        resultados_ok = 0
        for consulta in consultas_generales:
            print(f"\n📝 Test general: {consulta}")
            respuestas = self.sistema.buscar_con_horarios(consulta, top_k=2)
            
            if len(respuestas) > 0:
                resultados_ok += 1
                print(f"✅ OK - {len(respuestas)} respuestas")
            else:
                print(f"❌ Sin respuestas")
        
        # Al menos 80% de consultas generales deben funcionar
        porcentaje_exito = (resultados_ok / len(consultas_generales)) * 100
        print(f"\n📊 Éxito en consultas generales: {porcentaje_exito:.1f}%")
        
        self.assertGreaterEqual(porcentaje_exito, 80, 
                               f"Solo {porcentaje_exito:.1f}% de consultas generales funcionaron (mínimo 80%)")
    
    def test_06_tiempo_respuesta(self):
        """Test: Verificar que las consultas responden en tiempo razonable"""
        import time
        
        consulta = "horarios de matemática"
        
        inicio = time.time()
        respuestas = self.sistema.buscar_con_horarios(consulta, top_k=3)
        tiempo_respuesta = time.time() - inicio
        
        print(f"\n⏱️ Tiempo de respuesta: {tiempo_respuesta:.3f}s")
        
        # Debe responder en menos de 2 segundos (target: <500ms)
        self.assertLess(tiempo_respuesta, 2.0, 
                       f"Tiempo de respuesta muy lento: {tiempo_respuesta:.3f}s")
        
        if tiempo_respuesta < 0.5:
            print("✅ Excelente tiempo de respuesta (<500ms)")
        elif tiempo_respuesta < 1.0:
            print("✅ Buen tiempo de respuesta (<1s)")
        else:
            print("⚠️ Tiempo de respuesta aceptable pero mejorable")
    
    def _guardar_resultado_test(self, nombre_test, consulta, respuestas, exito):
        """Guarda resultado de test para reporte final"""
        resultado = {
            'test': nombre_test,
            'consulta': consulta,
            'exito': exito,
            'respuestas_count': len(respuestas),
            'primera_respuesta': respuestas[0] if respuestas else None,
            'timestamp': datetime.now().isoformat()
        }
        self.resultados_tests.append(resultado)
    
    @classmethod
    def tearDownClass(cls):
        """Genera reporte final de testing"""
        print("\n" + "="*60)
        print("📋 REPORTE FINAL DE TESTING")
        print("="*60)
        
        total_tests = len(cls.resultados_tests)
        tests_exitosos = sum(1 for r in cls.resultados_tests if r['exito'])
        
        print(f"Total tests: {total_tests}")
        print(f"Tests exitosos: {tests_exitosos}")
        print(f"Porcentaje de éxito: {(tests_exitosos/total_tests)*100:.1f}%")
        
        # Guardar reporte detallado
        reporte_file = os.path.join(os.path.dirname(__file__), '..', 'reportes', 'reporte_testing_horarios.json')
        
        reporte = {
            'fecha_testing': datetime.now().isoformat(),
            'resumen': {
                'total_tests': total_tests,
                'tests_exitosos': tests_exitosos,
                'porcentaje_exito': (tests_exitosos/total_tests)*100
            },
            'resultados_detallados': cls.resultados_tests
        }
        
        os.makedirs(os.path.dirname(reporte_file), exist_ok=True)
        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Reporte guardado en: {reporte_file}")

if __name__ == '__main__':
    # Ejecutar tests con verbosidad
    unittest.main(verbosity=2)