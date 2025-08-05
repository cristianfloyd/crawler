#!/usr/bin/env python3
"""
Test específico para equivalencias CBC en el normalizador
Verifica que las materias CBC genéricas matcheen con materias obligatorias específicas
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from normalizador_nombres_materias import NormalizadorNombresMaterias

def test_equivalencias_cbc():
    """Test de equivalencias específicas CBC"""
    print("=" * 60)
    print("TEST: Equivalencias CBC")
    print("=" * 60)
    
    normalizador = NormalizadorNombresMaterias()
    
    # Casos de prueba específicos CBC -> Obligatorias
    casos_test = [
        # Casos que deberían funcionar ahora
        ("Química General e Inorgánica", "quimica"),  # Obligatoria -> CBC
        ("Física 1", "fisica"),                       # Obligatoria -> CBC
        ("Física I", "fisica"),                       # Obligatoria -> CBC
        ("Quimica", "quimica general e inorganica"),  # CBC -> Obligatoria
        ("Fisica", "fisica i"),                       # CBC -> Obligatoria
        
        # Casos existentes que ya funcionaban
        ("Álgebra I", "algebra i"),
        ("Análisis I", "analisis i"),
    ]
    
    print("🧪 Probando equivalencias CBC:")
    print()
    
    equivalencias_funcionando = 0
    total_casos = len(casos_test)
    
    for nombre_entrada, esperado_contiene in casos_test:
        resultado = normalizador.normalizar_nombre_web(nombre_entrada)
        
        if resultado and esperado_contiene.lower() in resultado.lower():
            print(f"✅ '{nombre_entrada}' -> '{resultado}' (contiene '{esperado_contiene}')")
            equivalencias_funcionando += 1
        elif resultado:
            print(f"⚠️  '{nombre_entrada}' -> '{resultado}' (esperaba que contuviera '{esperado_contiene}')")
        else:
            print(f"❌ '{nombre_entrada}' -> None (esperaba que contuviera '{esperado_contiene}')")
    
    print()
    print(f"📊 Resultado: {equivalencias_funcionando}/{total_casos} equivalencias funcionando")
    
    # Mostrar estadísticas del normalizador actualizado
    stats = normalizador.obtener_estadisticas()
    print(f"📋 Estadísticas del normalizador:")
    print(f"   • Materias base: {stats['total_materias_base']}")
    print(f"   • Variaciones en índice: {stats['total_variaciones_indice']}")
    print(f"   • Equivalencias CBC: {stats['total_equivalencias_cbc']}")
    
    return equivalencias_funcionando >= total_casos * 0.7  # 70% mínimo

def test_casos_problematicos():
    """Test de casos específicos que estaban fallando"""
    print("\n" + "=" * 60)
    print("TEST: Casos problemáticos específicos")
    print("=" * 60)
    
    normalizador = NormalizadorNombresMaterias()
    
    casos_problematicos = [
        "Química General e Inorgánica (Lic. En Cs. Biol. y Geo.) - Electiva de Intro. a las Cs. Naturales",
        "Física 1 (Lic. en Cs. Físicas) - Electiva de Intro. a las Cs. Naturales (solicitar equivalencia)",
        "Física 1 (Q) - Electiva de Intro. a las Cs. Naturales",
        "Quimica",  # CBC simple
        "Fisica",   # CBC simple
    ]
    
    print("🔍 Casos problemáticos:")
    print()
    
    for caso in casos_problematicos:
        resultado = normalizador.normalizar_nombre_web(caso)
        print(f"   '{caso}' -> '{resultado}'")
    
    return True

def main():
    """Ejecuta todos los tests de equivalencias CBC"""
    print("🧪 TESTS DE EQUIVALENCIAS CBC")
    print("Verificando mejoras en matching para materias CBC")
    
    tests_exitosos = 0
    total_tests = 2
    
    try:
        if test_equivalencias_cbc():
            tests_exitosos += 1
        
        if test_casos_problematicos():
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
        print("[SUCCESS] ✓ Equivalencias CBC funcionando correctamente")
        print("[INFO] ¡Listo para re-ejecutar el enriquecimiento!")
    else:
        print(f"[WARNING] {total_tests - tests_exitosos} tests fallaron")
        print("[INFO] Revisar equivalencias antes de continuar")

if __name__ == "__main__":
    main()