#!/usr/bin/env python3
"""
Script de testing simplificado para validar las mejoras del descubrimiento
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from descubrir_sitios import DescubrirSitios
import asyncio

async def test_refinamiento():
    """Test rápido del descubrimiento refinado"""
    print("=" * 60)
    print("TEST DEL DESCUBRIMIENTO REFINADO")
    print("=" * 60)
    
    descubridor = DescubrirSitios()
    
    # Test con menos URLs para evitar problemas de encoding
    print("Iniciando descubrimiento con URLs refinadas...")
    await descubridor.descubrir_sitios_completo(max_urls=25)
    
    # Generar reporte
    reporte = descubridor.generar_reporte()
    
    print("\n" + "="*60)
    print("RESULTADOS DEL REFINAMIENTO:")
    print("="*60)
    
    print(f"Total sitios analizados: {reporte['resumen']['total_sitios']}")
    print(f"Sitios con materias: {reporte['resumen']['sitios_con_materias']}")
    print(f"Sitios prioritarios: {len(reporte['sitios_prioritarios'])}")
    
    print("\nTOP 5 SITIOS CON SCORING LCD:")
    for i, sitio in enumerate(reporte["sitios_prioritarios"][:5], 1):
        score_lcd = sitio.get('score_lcd', 0)
        score_base = sitio.get('score_base', 0)
        es_actual = sitio.get('es_actual', True)
        
        print(f"{i}. {sitio['titulo'][:60]}...")
        print(f"   URL: {sitio['url']}")
        print(f"   Score Total: {sitio['score']} (Base: {score_base} + LCD: {score_lcd})")
        print(f"   Actualidad: {'ACTUAL' if es_actual else 'OBSOLETO'}")
        print(f"   Info: {', '.join(sitio['tipos_info'])}")
        print()
    
    print("\nNUEVAS URLs BASE ENCONTRADAS:")
    urls_dc_dm_ic = [url for url in reporte['sitios_detalle'].keys() 
                     if any(dept in url.lower() for dept in ['dc.uba.ar', 'dm.uba.ar', 'ic.fcen'])]
    
    if urls_dc_dm_ic:
        for url in urls_dc_dm_ic[:5]:
            print(f"  - {url}")
    else:
        print("  [No se encontraron URLs de DC/DM/IC - necesita investigación adicional]")
    
    print("\n" + "="*60)
    print("REFINAMIENTO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(test_refinamiento())
    except KeyboardInterrupt:
        print("\nTest cancelado por usuario")
    except Exception as e:
        print(f"Error durante test: {e}")