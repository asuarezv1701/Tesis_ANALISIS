"""
Módulo de análisis de índices de vegetación para tesis.
Proporciona funcionalidades para procesar, analizar y visualizar datos satelitales.
"""

__version__ = "1.0.0"
__author__ = "Proyecto de Tesis - UPIITA"

# Importaciones convenientes para el usuario del módulo
from .procesador_base import (
    cargar_imagen,
    cargar_imagen_enmascarada,
    limpiar_datos,
    obtener_fecha_carpeta,
    extraer_coordenadas
)

from .estadisticas import (
    calcular_estadisticas_basicas,
    calcular_estadisticas_avanzadas,
    calcular_coeficiente_variacion
)

__all__ = [
    'cargar_imagen',
    'cargar_imagen_enmascarada',
    'limpiar_datos',
    'obtener_fecha_carpeta',
    'extraer_coordenadas',
    'calcular_estadisticas_basicas',
    'calcular_estadisticas_avanzadas',
    'calcular_coeficiente_variacion'
]
