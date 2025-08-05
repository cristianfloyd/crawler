#!/usr/bin/env python3
"""
Test de integración para la Fase 5 - ExtractorMateriasObligatorias
Verifica la integración con materias_lcd_descubiertas.json
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from enriquecer_materias_obligatorias import ExtractorMateriasObligatorias

def test_cargar_materias_base():
    """Test de carga de materias desde materias_lcd_descubiertas.json"""
    print("=" * 60)
    print("TEST: Carga de materias LCD descubiertas")
    print("=" * 60)
    
    extractor = ExtractorMateriasObligatorias()
    materias = extractor.cargar_materias_base()
    
    if materias:
        print(f"[OK] Test exitoso: {len(materias)} materias cargadas")
        print(f"[OK] Primera materia: '{materias[0].get('nombre', 'N/A')}'")
        print(f"[OK] Ciclo: {materias[0].get('ciclo', 'N/A')}")
        
        # Verificar estructura
        ciclos_encontrados = {}
        for materia in materias:
            ciclo = materia.get('ciclo', 'sin_ciclo')
            ciclos_encontrados[ciclo] = ciclos_encontrados.get(ciclo, 0) + 1
        
        print(f"[OK] Distribución por ciclos:")
        for ciclo, count in ciclos_encontrados.items():
            print(f"     • {ciclo}: {count} materias")
        
        return True
    else:
        print("[ERROR] No se pudieron cargar las materias")
        return False

def test_normalizador():
    """Test del normalizador integrado"""
    print("\n" + "=" * 60)
    print("TEST: Normalizador integrado")
    print("=" * 60)
    
    extractor = ExtractorMateriasObligatorias()
    
    # Test de normalización con nombres de ejemplo
    nombres_test = [
        "Álgebra I",
        "Análisis Matemático II", 
        "Algoritmos y Estructuras de Datos III",
        "Intro. a la Estadística",
        "Probabilidad y Estadística"
    ]
    
    print("[TEST] Probando normalización:")
    for nombre in nombres_test:
        resultado = extractor.normalizador.normalizar_nombre_web(nombre)
        print(f"     '{nombre}' -> '{resultado}'")
    
    # Mostrar estadísticas del normalizador
    stats = extractor.normalizador.obtener_estadisticas()
    print(f"[OK] Estadísticas del normalizador:")
    print(f"     • Materias base: {stats['total_materias_base']}")
    print(f"     • Variaciones en índice: {stats['total_variaciones_indice']}")
    
    return True

def test_preparacion_matching():
    """Test del método de matching"""
    print("\n" + "=" * 60)
    print("TEST: Preparación para matching")
    print("=" * 60)
    
    extractor = ExtractorMateriasObligatorias()
    
    # Test de preparación para matching
    nombres_test = [
        "algebra i",
        "analisis matematico ii",
        "algoritmos y estructuras de datos iii"
    ]
    
    print("[TEST] Preparación para matching:")
    for nombre in nombres_test:
        resultado = extractor.normalizador._preparar_para_matching(nombre)
        print(f"     '{nombre}' -> '{resultado}'")
    
    return True

def main():
    """Ejecuta todos los tests de integración"""
    print("🧪 TESTS DE INTEGRACIÓN - FASE 5")
    print("Verificando integración con materias_lcd_descubiertas.json")
    
    tests_exitosos = 0
    total_tests = 3
    
    try:
        if test_cargar_materias_base():
            tests_exitosos += 1
        
        if test_normalizador():
            tests_exitosos += 1
            
        if test_preparacion_matching():
            tests_exitosos += 1
            
    except Exception as e:
        print(f"[ERROR] Error durante los tests: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    print(f"Tests exitosos: {tests_exitosos}/{total_tests}")
    
    if tests_exitosos == total_tests:
        print("[SUCCESS] ✓ Todos los tests pasaron correctamente")
        print("[INFO] La integración con materias_lcd_descubiertas.json está funcionando")
    else:
        print(f"[WARNING] {total_tests - tests_exitosos} tests fallaron")
        print("[INFO] Revisar la configuración antes de continuar")

if __name__ == "__main__":
    main()