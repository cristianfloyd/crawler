#!/usr/bin/env python3
"""
Test rápido del scraper corregido del Instituto de Cálculo
"""

from src.scraper_horarios_instituto_calculo import ScraperHorariosIC

def test_scraper_con_html_local():
    scraper = ScraperHorariosIC()
    
    # Leer HTML local
    with open("temporales/intituto_de_calculo.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    print("HTML leído exitosamente")
    
    # Extraer materias
    materias = scraper.extraer_materias_de_html(html)
    
    print(f"\nMaterias extraídas: {len(materias)}")
    
    # Mostrar primera materia con horarios
    for i, materia in enumerate(materias):
        if materia["horarios"]:
            print(f"\n=== MATERIA {i+1} CON HORARIOS ===")
            print(f"Nombre: {materia['nombre']}")
            print(f"Horarios raw: {materia['metadata']['horarios_raw']}")
            print(f"Horarios estructurados: {materia['horarios']}")
            print(f"Docentes: {materia['docentes']}")
            break
    else:
        print("\n❌ Ninguna materia tiene horarios extraídos")
        # Mostrar primera materia para debug
        if materias:
            print(f"\n=== DEBUG PRIMERA MATERIA ===")
            print(f"Nombre: {materias[0]['nombre']}")
            print(f"Horarios raw: '{materias[0]['metadata']['horarios_raw']}'")
            print(f"Docentes raw: (necesita debug)")

if __name__ == "__main__":
    test_scraper_con_html_local()