"""
Configuración centralizada del proyecto de análisis de tesis.
Todas las rutas, parámetros y constantes se definen aquí.
"""

import os
from pathlib import Path

# ============================================================================
# RUTAS BASE DEL PROYECTO
# ============================================================================

# Ruta base del proyecto de análisis
RUTA_PROYECTO = Path(__file__).parent.parent.absolute()

# Ruta de datos de entrada (desde Tesis_DESCARGAS)
NOMBRE_CARPETA_DESCARGAS = "UPIITA_contours_25nov.2025"
RUTA_DESCARGAS = RUTA_PROYECTO.parent / "Tesis_DESCARGAS" / "descargas" / NOMBRE_CARPETA_DESCARGAS

# Ruta del shapefile para enmascaramiento
RUTA_SHAPEFILE = RUTA_PROYECTO.parent / "Tesis_DESCARGAS" / "shapefiles" / "UPIITA_contours_25nov.2025" / "UPIITA_contours_25Nov2025.shp"

# ============================================================================
# RUTAS DE SALIDA
# ============================================================================

# NOTA: Todas las salidas se guardan en una carpeta "resultados" para mantener orden
RUTA_RESULTADOS = RUTA_PROYECTO / "resultados"

RUTA_REPORTES = RUTA_RESULTADOS / "reportes"
RUTA_VISUALIZACIONES = RUTA_RESULTADOS / "visualizaciones"
RUTA_REPORTES_PDF = RUTA_RESULTADOS / "reportes_pdf"
# Caché de estadísticas computadas por índice (para actualización incremental)
RUTA_DATOS_PROCESADOS = RUTA_RESULTADOS / "datos_procesados"

# Crear carpetas si no existen
for ruta in [RUTA_REPORTES, RUTA_VISUALIZACIONES, RUTA_REPORTES_PDF, RUTA_DATOS_PROCESADOS]:
    ruta.mkdir(exist_ok=True, parents=True)

# ============================================================================
# ÍNDICES DE VEGETACIÓN DISPONIBLES
# ============================================================================

INDICES_INFO = {
    "NDVI": {
        "nombre": "Normalized Difference Vegetation Index",
        "descripcion": "Índice de Vegetación Normalizado",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "< 0": "Agua, nubes, nieve",
            "0-0.2": "Suelo desnudo, rocas, construcciones",
            "0.2-0.5": "Vegetación escasa o estresada",
            "0.5-0.8": "Vegetación moderada a densa",
            "> 0.8": "Vegetación muy densa y saludable"
        },
        # Umbrales científicos fijos (Rouse et al. 1974; Tucker 1979).
        # Al ser rangos definidos por la literatura, son comparables entre fechas
        # y justificables sin decisión arbitraria.
        "umbrales_canonicos": [
            {"zona": 0, "limite_inferior": -1.0,        "limite_superior": 0.0,        "etiqueta": "Sin vegetación",          "color": "#d73027"},
            {"zona": 1, "limite_inferior":  0.0,        "limite_superior": 0.2,        "etiqueta": "Suelo desnudo",           "color": "#fc8d59"},
            {"zona": 2, "limite_inferior":  0.2,        "limite_superior": 0.4,        "etiqueta": "Vegetación escasa",       "color": "#fee08b"},
            {"zona": 3, "limite_inferior":  0.4,        "limite_superior": 0.6,        "etiqueta": "Vegetación moderada",     "color": "#91cf60"},
            {"zona": 4, "limite_inferior":  0.6,        "limite_superior": float('inf'), "etiqueta": "Vegetación densa",      "color": "#1a9850"},
        ]
    },
    "NDRE": {
        "nombre": "Normalized Difference Red Edge",
        "descripcion": "Red Edge Normalizado",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "bajo": "Bajo contenido de clorofila",
            "alto": "Alto contenido de clorofila, detecta estrés temprano"
        },
        # Umbrales científicos fijos (Gitelson & Merzlyak 1994).
        "umbrales_canonicos": [
            {"zona": 0, "limite_inferior": -1.0,        "limite_superior": 0.0,        "etiqueta": "Sin actividad clorofílica", "color": "#d73027"},
            {"zona": 1, "limite_inferior":  0.0,        "limite_superior": 0.15,       "etiqueta": "Clorofila muy baja",        "color": "#fc8d59"},
            {"zona": 2, "limite_inferior":  0.15,       "limite_superior": 0.30,       "etiqueta": "Clorofila baja",            "color": "#fee08b"},
            {"zona": 3, "limite_inferior":  0.30,       "limite_superior": 0.45,       "etiqueta": "Clorofila moderada",        "color": "#91cf60"},
            {"zona": 4, "limite_inferior":  0.45,       "limite_superior": float('inf'), "etiqueta": "Clorofila alta",          "color": "#1a9850"},
        ]
    },
    "MSAVI": {
        "nombre": "Modified Soil-Adjusted Vegetation Index",
        "descripcion": "Índice Ajustado de Vegetación",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "bajo": "Poca cobertura vegetal",
            "alto": "Mayor cobertura vegetal, minimiza efecto del suelo"
        },
        # Umbrales científicos fijos (Qi et al. 1994).
        "umbrales_canonicos": [
            {"zona": 0, "limite_inferior": -1.0,        "limite_superior": 0.0,        "etiqueta": "Sin cobertura vegetal",  "color": "#d73027"},
            {"zona": 1, "limite_inferior":  0.0,        "limite_superior": 0.15,       "etiqueta": "Cobertura mínima",       "color": "#fc8d59"},
            {"zona": 2, "limite_inferior":  0.15,       "limite_superior": 0.30,       "etiqueta": "Cobertura baja",         "color": "#fee08b"},
            {"zona": 3, "limite_inferior":  0.30,       "limite_superior": 0.50,       "etiqueta": "Cobertura moderada",     "color": "#91cf60"},
            {"zona": 4, "limite_inferior":  0.50,       "limite_superior": float('inf'), "etiqueta": "Cobertura alta",       "color": "#1a9850"},
        ]
    },
    "RECI": {
        "nombre": "Red Edge Chlorophyll Index",
        "descripcion": "Índice de Clorofila Red Edge",
        "rango_teorico": (0, 20),
        "interpretacion": {
            "0-5": "Bajo contenido de clorofila",
            "5-10": "Contenido moderado de clorofila",
            "> 10": "Alto contenido de clorofila"
        },
        # Umbrales científicos fijos (Gitelson et al. 2003).
        "umbrales_canonicos": [
            {"zona": 0, "limite_inferior":  0.0,        "limite_superior": 1.0,        "etiqueta": "Clorofila muy baja",  "color": "#d73027"},
            {"zona": 1, "limite_inferior":  1.0,        "limite_superior": 3.0,        "etiqueta": "Clorofila baja",      "color": "#fc8d59"},
            {"zona": 2, "limite_inferior":  3.0,        "limite_superior": 6.0,        "etiqueta": "Clorofila moderada",  "color": "#fee08b"},
            {"zona": 3, "limite_inferior":  6.0,        "limite_superior": 10.0,       "etiqueta": "Clorofila alta",      "color": "#91cf60"},
            {"zona": 4, "limite_inferior": 10.0,        "limite_superior": float('inf'), "etiqueta": "Clorofila muy alta", "color": "#1a9850"},
        ]
    },
    "NDMI": {
        "nombre": "Normalized Difference Moisture Index",
        "descripcion": "Índice de Humedad",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "bajo": "Baja humedad, estrés hídrico",
            "alto": "Alta humedad en vegetación"
        },
        # Umbrales científicos fijos (Gao 1996).
        "umbrales_canonicos": [
            {"zona": 0, "limite_inferior": -1.0,        "limite_superior": -0.2,       "etiqueta": "Estrés hídrico severo", "color": "#d73027"},
            {"zona": 1, "limite_inferior": -0.2,        "limite_superior":  0.0,       "etiqueta": "Estrés hídrico leve",   "color": "#fc8d59"},
            {"zona": 2, "limite_inferior":  0.0,        "limite_superior":  0.2,       "etiqueta": "Humedad moderada",      "color": "#fee08b"},
            {"zona": 3, "limite_inferior":  0.2,        "limite_superior":  0.4,       "etiqueta": "Humedad buena",         "color": "#91cf60"},
            {"zona": 4, "limite_inferior":  0.4,        "limite_superior": float('inf'), "etiqueta": "Humedad alta",        "color": "#1a9850"},
        ]
    }
}

# ============================================================================
# PARÁMETROS DE ANÁLISIS
# ============================================================================

# Parámetros de filtrado
PERCENTILES_DEFAULT = [1, 5, 25, 50, 75, 95, 99]

# Valores inválidos a considerar como NaN
VALORES_INVALIDOS = [0, -9999, -3.40282e+38]  # Común en datos satelitales

# Parámetros de visualización
DPI_GRAFICAS = 150
FIGSIZE_DEFAULT = (12, 6)
FIGSIZE_GRANDE = (14, 8)

# Parámetros de clustering
N_CLUSTERS_DEFAULT = 5

# Parámetros de análisis temporal
VENTANA_TEMPORAL_DIAS = 7  # Para cálculo de velocidad de cambio

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

NIVEL_LOG = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def validar_configuracion():
    """
    Valida que las rutas principales existan.
    """
    errores = []
    
    if not RUTA_DESCARGAS.exists():
        errores.append(f"No se encontró carpeta de descargas: {RUTA_DESCARGAS}")
    
    if not RUTA_SHAPEFILE.exists():
        errores.append(f"No se encontró shapefile: {RUTA_SHAPEFILE}")
    
    return errores


def obtener_ruta_indice(indice):
    """
    Retorna la ruta completa de un índice específico.
    """
    return RUTA_DESCARGAS / indice


def obtener_indices_disponibles():
    """
    Retorna lista de índices que tienen datos disponibles.
    """
    if not RUTA_DESCARGAS.exists():
        return []
    
    indices_disponibles = []
    for item in RUTA_DESCARGAS.iterdir():
        if item.is_dir() and item.name in INDICES_INFO:
            # Verificar que tenga carpetas de fechas
            carpetas = [d for d in item.iterdir() if d.is_dir()]
            if carpetas:
                indices_disponibles.append(item.name)
    
    return sorted(indices_disponibles)


if __name__ == "__main__":
    # Validar configuración al ejecutar este archivo
    print("="*80)
    print("VALIDACIÓN DE CONFIGURACIÓN")
    print("="*80)
    
    print(f"\nRuta del proyecto: {RUTA_PROYECTO}")
    print(f"Ruta de descargas: {RUTA_DESCARGAS}")
    print(f"Ruta de shapefile: {RUTA_SHAPEFILE}")
    
    errores = validar_configuracion()
    
    if errores:
        print("\nERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  • {error}")
    else:
        print("\nConfiguración válida")
        
        indices = obtener_indices_disponibles()
        if indices:
            print(f"\nÍndices disponibles: {', '.join(indices)}")
        else:
            print("\nADVERTENCIA: No se encontraron índices con datos")
