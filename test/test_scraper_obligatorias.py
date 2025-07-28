#!/usr/bin/env python3
"""
Script de testing para el Scraper de Materias Obligatorias
Incluye tests unitarios y de integración

Autor: Sistema RAG MVP  
Fecha: 2025-07-26
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from scraper_materias_obligatorias import ScraperMateriasObligatorias

class TestScraperMateriasObligatorias(unittest.TestCase):
    """Tests para el scraper de materias obligatorias"""
    
    def setUp(self):
        """Setup para cada test"""
        self.scraper = ScraperMateriasObligatorias()
        
        # HTML de muestra basado en el HTML real
        self.html_muestra = """
        <html>
        <body>
            <h2>1er cuatrimestre 2025</h2>
            <table class="table">
                <tr><th>Materia</th><th>Departamento</th><th>Página web</th></tr>
                <tr>
                    <td>Algoritmos y Estructuras de Datos I</td>
                    <td>Departamento de Computación</td>
                    <td><a href="https://www.dc.uba.ar/cursada-de-grado/"><img src="/programs/imagenes/website.png"></a></td>
                </tr>
                <tr>
                    <td>Álgebra I</td>
                    <td>Departamento de Matemática</td>
                    <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=1"><img src="/programs/imagenes/website.png"></a></td>
                </tr>
                <tr>
                    <td>Física 1 (Q) - Electiva de Intro. a las Cs. Naturales</td>
                    <td>Departamento de Física</td>
                    <td><a href="https://www.df.uba.ar/es/docentes/distribucion-de-horarios-y-docentes"><img src="/programs/imagenes/website.png"></a></td>
                </tr>
            </table>
            
            <h2>2do cuatrimestre 2025</h2>
            <table class="table">
                <tr><th>Materia</th><th>Departamento</th><th>Página web</th></tr>
                <tr>
                    <td>Análisis II</td>
                    <td>Departamento de Matemática</td>
                    <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=2"><img src="/programs/imagenes/website.png"></a></td>
                </tr>
            </table>
        </body>
        </html>
        """
    
    def test_extraer_materias_por_periodo(self):
        """Test de extracción por período"""
        materias_por_periodo = self.scraper.extraer_materias_por_periodo(self.html_muestra)
        
        # Verificar que se detectaron 2 períodos
        self.assertEqual(len(materias_por_periodo), 2)
        self.assertIn("1er cuatrimestre 2025", materias_por_periodo)
        self.assertIn("2do cuatrimestre 2025", materias_por_periodo)
        
        # Verificar cantidad de materias por período
        self.assertEqual(len(materias_por_periodo["1er cuatrimestre 2025"]), 3)
        self.assertEqual(len(materias_por_periodo["2do cuatrimestre 2025"]), 1)
    
    def test_limpiar_nombre_materia(self):
        """Test de limpieza de nombres"""
        # Test casos normales
        self.assertEqual(
            self.scraper._limpiar_nombre_materia("Algoritmos y Estructuras de Datos I"),
            "Algoritmos y Estructuras de Datos I"
        )
        
        # Test con especificación de carrera
        self.assertEqual(
            self.scraper._limpiar_nombre_materia("Física 1 (Lic. en Cs. Físicas) - Electiva de Intro. a las Cs. Naturales"),
            "Física 1"
        )
        
        # Test con espacios extra
        self.assertEqual(
            self.scraper._limpiar_nombre_materia("  Álgebra   I  "),
            "Álgebra I"
        )
    
    def test_mapear_departamento(self):
        """Test de mapeo de departamentos"""
        self.assertEqual(
            self.scraper._mapear_departamento("Departamento de Matemática"),
            "DM"
        )
        self.assertEqual(
            self.scraper._mapear_departamento("Departamento de Computación"),
            "DC"
        )
        self.assertEqual(
            self.scraper._mapear_departamento("Instituto de Cálculo"),
            "IC"
        )
        
        # Test departamento no mapeado
        self.assertIsNone(
            self.scraper._mapear_departamento("Departamento Inexistente")
        )
    
    def test_identificar_tipo_materia(self):
        """Test de identificación de tipos"""
        self.assertEqual(
            self.scraper._identificar_tipo_materia("Algoritmos y Estructuras de Datos I"),
            "obligatoria"
        )
        self.assertEqual(
            self.scraper._identificar_tipo_materia("Física 1 - Electiva de Intro."),
            "electiva"
        )
        self.assertEqual(
            self.scraper._identificar_tipo_materia("Tesis de Licenciatura"),
            "tesis"
        )
    
    def test_generar_id(self):
        """Test de generación de IDs"""
        periodo = {"año": 2025, "cuatrimestre": "1"}
        id_generado = self.scraper._generar_id("Algoritmos y Estructuras de Datos I", periodo, 0)
        
        self.assertTrue(id_generado.startswith("lcd_obligatoria_"))
        self.assertIn("algoritmos_y_estructuras_de_datos_i", id_generado)
        self.assertIn("2025_1", id_generado)
    
    def test_procesar_url_horarios(self):
        """Test de procesamiento de URLs"""
        # URL completa
        url_completa = "https://www.dc.uba.ar/cursada-de-grado/"
        self.assertEqual(
            self.scraper._procesar_url_horarios(url_completa),
            url_completa
        )
        
        # URL relativa
        url_relativa = "/materias/horarios"
        resultado = self.scraper._procesar_url_horarios(url_relativa)
        self.assertTrue(resultado.startswith("https://"))
    
    def test_validar_materias_extraidas(self):
        """Test de validación de datos extraídos"""
        materias_por_periodo = self.scraper.extraer_materias_por_periodo(self.html_muestra)
        stats = self.scraper.validar_materias_extraidas(materias_por_periodo)
        
        self.assertEqual(stats["total_materias"], 4)
        self.assertEqual(stats["total_periodos"], 2)
        self.assertIn("DC", stats["departamentos_unicos"])
        self.assertIn("DM", stats["departamentos_unicos"])
        self.assertIn("DF", stats["departamentos_unicos"])

class TestIntegracion(unittest.TestCase):
    """Tests de integración"""
    
    def setUp(self):
        self.scraper = ScraperMateriasObligatorias()
    
    @patch('scraper_materias_obligatorias.requests.Session.get')
    def test_scraping_completo_mock(self, mock_get):
        """Test del proceso completo con HTTP mockeado"""
        # Configurar mock response
        mock_response = MagicMock()
        mock_response.text = """
        <html><body>
            <h2>1er cuatrimestre 2025</h2>
            <table class="table">
                <tr><th>Materia</th><th>Departamento</th><th>Página web</th></tr>
                <tr>
                    <td>Test Materia</td>
                    <td>Departamento de Computación</td>
                    <td><a href="https://test.com"><img src="test.png"></a></td>
                </tr>
            </table>
        </body></html>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Ejecutar scraping
        resultado = self.scraper.ejecutar_scraping_completo()
        
        # Verificar resultado
        self.assertTrue(resultado)
        
        # Verificar que se llamó a la URL correcta
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.scraper.base_url)

def test_con_html_real():
    """Test con el HTML real que proporcionaste"""
    print("\n🧪 EJECUTANDO TEST CON HTML REAL")
    print("=" * 50)
    
    # Leer el HTML desde archivo (si existe)
    html_file = "materias_obligatorias.html"
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_real = f.read()
    else:
        # Usar el HTML que proporcionaste (truncado para el ejemplo)
        html_real = """
        <h2>1er cuatrimestre 2025</h2>
        <table class="table">
            <tr><th>Materia</th><th>Departamento</th><th>Página web</th></tr>
            <tr>
                <td>Álgebra I</td>
                <td>Departamento de Matemática</td>
                <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=1"><img src="/programs/imagenes/website.png"></a></td>
            </tr>
            <tr>
                <td>Algoritmos y Estructuras de Datos I</td>
                <td>Departamento de Computación</td>
                <td><a href="https://www.dc.uba.ar/cursada-de-grado/"><img src="/programs/imagenes/website.png"></a></td>
            </tr>
        </table>
        """
    
    scraper = ScraperMateriasObligatorias()
    materias_por_periodo = scraper.extraer_materias_por_periodo(html_real)
    stats = scraper.validar_materias_extraidas(materias_por_periodo)
    
    print(f"✅ Períodos detectados: {stats['total_periodos']}")
    print(f"✅ Total materias: {stats['total_materias']}")
    print(f"✅ Departamentos: {stats['departamentos_unicos']}")
    print(f"✅ Materias por período: {stats['materias_por_periodo']}")
    
    # Mostrar una materia de ejemplo
    if materias_por_periodo:
        primer_periodo = list(materias_por_periodo.keys())[0]
        if materias_por_periodo[primer_periodo]:
            ejemplo = materias_por_periodo[primer_periodo][0]
            print(f"\n📋 EJEMPLO DE MATERIA EXTRAÍDA:")
            print(json.dumps(ejemplo, indent=2, ensure_ascii=False))
    
    return materias_por_periodo, stats

def main():
    """Función principal de testing"""
    print("🧪 INICIANDO TESTS DEL SCRAPER")
    print("=" * 40)
    
    # Ejecutar tests unitarios
    print("\n1️⃣ TESTS UNITARIOS")
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Test con HTML real
    print("\n2️⃣ TEST CON HTML REAL")
    materias, stats = test_con_html_real()
    
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"   - Tests unitarios: ✅ Completados")
    print(f"   - Test HTML real: ✅ {stats['total_materias']} materias extraídas")
    print(f"   - Departamentos: {len(stats['departamentos_unicos'])}")
    
    return materias, stats

if __name__ == "__main__":
    main()