"""
Módulo de descubrimiento de sitios web para la Facultad de Ciencias Exactas UBA
"""

from .descubrimiento.descubrir_sitios import (
    DescubrirSitios,
    PATRONES_INTERES,
    DEPARTAMENTOS_CONOCIDOS,
    DOMINIO,
    URLS_BASE
)

__all__ = [
    'DescubrirSitios',
    'PATRONES_INTERES', 
    'DEPARTAMENTOS_CONOCIDOS',
    'DOMINIO',
    'URLS_BASE'
] 