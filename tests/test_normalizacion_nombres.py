#!/usr/bin/env python3
"""
Test de normalización de nombres de materias
Verifica que la función elimine acentos, ñ y caracteres especiales correctamente
"""

from procesar_datos_unificado import ProcesadorDatosUnificado

def test_normalizacion_nombres():
    """Prueba la función de normalización de nombres"""
    procesador = ProcesadorDatosUnificado()
    
    # Casos de prueba
    casos_prueba = [
        # Original -> Esperado
        ("Análisis Matemático I", "analisis matematico i"),
        ("Álgebra Lineal", "algebra lineal"),
        ("Introducción a la Programación", "introduccion a la programacion"),
        ("Diseño de Algoritmos", "diseno de algoritmos"),
        ("Estadística Espacial con R", "estadistica espacial con r"),
        ("Optimización Semidefinida", "optimizacion semidefinida"),
        ("Técnicas de Visualización", "tecnicas de visualizacion"),
        ("Matemática Discreta II", "matematica discreta ii"),
        ("Programación Orientada a Objetos", "programacion orientada a objetos"),
        ("Base de Datos", "base de datos"),
        ("Señales y Sistemas", "senales y sistemas"),
        ("Redes Neuronales", "redes neuronales"),
        ("Inteligencia Artificial", "inteligencia artificial")
    ]
    
    print("🧪 PROBANDO NORMALIZACIÓN DE NOMBRES")
    print("=" * 50)
    
    errores = 0
    for original, esperado in casos_prueba:
        resultado = procesador._normalizar_nombre_sin_acentos(original)
        
        if resultado == esperado:
            print(f"✅ '{original}' -> '{resultado}'")
        else:
            print(f"❌ '{original}' -> '{resultado}' (esperado: '{esperado}')")
            errores += 1
    
    print(f"\n📊 RESULTADO: {len(casos_prueba) - errores}/{len(casos_prueba)} pruebas exitosas")
    
    if errores == 0:
        print("🎉 ¡Todas las pruebas pasaron correctamente!")
    else:
        print(f"⚠️  {errores} pruebas fallaron")
    
    return errores == 0

if __name__ == "__main__":
    test_normalizacion_nombres()