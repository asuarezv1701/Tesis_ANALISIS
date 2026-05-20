"""
Actualización Incremental de Análisis de Índices de Vegetación

Este script:
1. Detecta fechas e índices nuevos que aún no han sido procesados
2. Calcula estadísticas solo para los datos nuevos
3. Integra los resultados nuevos con el caché existente
4. Re-ejecuta el análisis temporal sobre la serie completa (antigua + nueva)
5. Compara la tendencia nueva vs la anterior para mostrar qué cambió

CUÁNDO USARLO:
  - Cuando descargas nuevas imágenes con Tesis_DESCARGAS
  - Es más rápido que inicio_analisis.py porque solo procesa lo nuevo

CUÁNDO usar inicio_analisis.py en su lugar:
  - Primera vez que analizas datos (para construir el caché inicial)
  - Si quieres regenerar todas las visualizaciones y reportes PDF
  - Si modificaste el shapefile u otros parámetros de configuración
"""

import sys
import pickle
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

from configuracion.config import (
    RUTA_DESCARGAS,
    RUTA_DATOS_PROCESADOS,
    RUTA_REPORTES,
    INDICES_INFO,
    obtener_indices_disponibles,
)
from analizador_tesis.procesador_base import (
    listar_imagenes_indice,
    cargar_datos_optimizado,
)
from analizador_tesis.estadisticas import (
    calcular_estadisticas_avanzadas,
    calcular_coeficiente_variacion,
    clasificar_heterogeneidad,
    detectar_outliers_zscore,
)
from analizador_tesis.temporal import (
    preparar_serie_temporal,
    calcular_tendencia_lineal,
    test_mann_kendall,
)


# ============================================================================
# RUTAS DE CACHÉ
# ============================================================================

def _ruta_cache_stats(indice: str) -> Path:
    return RUTA_DATOS_PROCESADOS / f"stats_{indice}.pkl"


def _ruta_cache_tendencias(indice: str) -> Path:
    return RUTA_DATOS_PROCESADOS / f"tendencias_{indice}.pkl"


# ============================================================================
# LECTURA / ESCRITURA DE CACHÉ
# ============================================================================

def cargar_cache_stats(indice: str) -> pd.DataFrame:
    """Carga el DataFrame de estadísticas cacheado para un índice."""
    ruta = _ruta_cache_stats(indice)
    if ruta.exists():
        with open(ruta, "rb") as f:
            return pickle.load(f)
    return pd.DataFrame()


def guardar_cache_stats(indice: str, df: pd.DataFrame) -> None:
    """Guarda el DataFrame de estadísticas actualizado."""
    ruta = _ruta_cache_stats(indice)
    with open(ruta, "wb") as f:
        pickle.dump(df, f)


def cargar_tendencias_previas(indice: str) -> dict | None:
    """Carga las tendencias calculadas en la última ejecución."""
    ruta = _ruta_cache_tendencias(indice)
    if ruta.exists():
        with open(ruta, "rb") as f:
            return pickle.load(f)
    return None


def guardar_tendencias(indice: str, tendencias: dict) -> None:
    ruta = _ruta_cache_tendencias(indice)
    with open(ruta, "wb") as f:
        pickle.dump(tendencias, f)


# ============================================================================
# CÁLCULO DE ESTADÍSTICAS POR IMAGEN
# ============================================================================

def calcular_stats_imagen(img_info: dict, indice: str) -> dict | None:
    """
    Calcula estadísticas de una imagen individual usando CSV o TIFF.
    Devuelve un dict con una fila por fecha, o None si hay error.
    """
    try:
        datos, fuente = cargar_datos_optimizado(img_info, usar_csv=True)

        if len(datos) == 0:
            return None

        stats = calcular_estadisticas_avanzadas(datos)

        if stats["n"] == 0:
            return None

        outliers_mask = detectar_outliers_zscore(datos, umbral=3)
        n_outliers = int(np.sum(outliers_mask[~np.isnan(datos)]))
        pct_outliers = (n_outliers / stats["n"] * 100) if stats["n"] > 0 else 0.0

        return {
            "fecha": img_info["fecha_str"],
            "indice": indice,
            "fuente": fuente,
            "pixeles_validos": stats["n"],
            "media": round(stats["media"], 6),
            "mediana": round(stats["mediana"], 6),
            "std": round(stats["std"], 6),
            "cv": round(stats["cv"], 4) if stats.get("cv") is not None else None,
            "min": round(stats["min"], 6),
            "max": round(stats["max"], 6),
            "rango": round(stats["rango"], 6),
            "skewness": round(stats["skewness"], 4),
            "kurtosis": round(stats["kurtosis"], 4),
            "pct_outliers": round(pct_outliers, 2),
            "heterogeneidad": clasificar_heterogeneidad(stats.get("cv")),
        }
    except Exception as e:
        print(f"    ERROR al procesar {img_info.get('fecha_str', '?')}: {e}")
        return None


# ============================================================================
# COMPARACIÓN DE TENDENCIAS
# ============================================================================

def _describir_tendencia(t: dict) -> str:
    """Formatea una tendencia en texto legible."""
    direccion = "↑ CRECIENTE" if t["pendiente"] > 0 else "↓ DECRECIENTE"
    sig = "significativa (p<0.05)" if t["significativo"] else "no significativa"
    cambio = f"{t['cambio_porcentual']:+.2f}%" if t.get("cambio_porcentual") is not None else "N/D"
    return (
        f"Pendiente: {t['pendiente']:+.6f}/día  [{direccion}]  "
        f"R²={t['r2']:.4f}  p={t['p_valor']:.4f} ({sig})  "
        f"Cambio total: {cambio}"
    )


def comparar_y_reportar_tendencias(
    indice: str,
    df_anterior: pd.DataFrame,
    df_actual: pd.DataFrame,
    n_nuevas: int,
) -> dict:
    """
    Calcula tendencias sobre el dataset completo y las compara con las previas.
    Devuelve un dict con el resumen del cambio.
    """
    print(f"\n  ── Análisis temporal ──")

    t_previa = cargar_tendencias_previas(indice)
    t_nueva = calcular_tendencia_lineal(df_actual)
    mk_nueva = test_mann_kendall(df_actual["media"].values)

    if t_nueva is None:
        print(f"  Insuficientes puntos para calcular tendencia ({len(df_actual)} fechas)")
        return {"indice": indice, "tendencia_actual": None, "cambio": None}

    print(f"  Tendencia ACTUAL  ({len(df_actual)} fechas):")
    print(f"    {_describir_tendencia(t_nueva)}")

    if mk_nueva:
        print(f"    Mann-Kendall: tau={mk_nueva['tau']:+.4f}  {mk_nueva['resultado']}")

    cambio_pendiente = None
    if t_previa is not None and n_nuevas > 0:
        cambio_pendiente = t_nueva["pendiente"] - t_previa["pendiente"]
        direccion_cambio = "se aceleró" if abs(t_nueva["pendiente"]) > abs(t_previa["pendiente"]) else "se desaceleró"
        print(f"\n  Tendencia ANTERIOR ({len(df_anterior)} fechas):")
        print(f"    {_describir_tendencia(t_previa)}")
        print(f"\n  CAMBIO en tendencia: {cambio_pendiente:+.6f}/día ({direccion_cambio})")
    elif t_previa is None and n_nuevas == 0:
        print("  (No hay tendencia previa ni datos nuevos — caché sin cambios)")

    # Guardar tendencias actualizadas
    guardar_tendencias(indice, t_nueva)

    return {
        "indice": indice,
        "tendencia_actual": t_nueva,
        "mann_kendall": mk_nueva,
        "cambio_pendiente": cambio_pendiente,
    }


# ============================================================================
# PROCESO PRINCIPAL POR ÍNDICE
# ============================================================================

def actualizar_indice(indice: str) -> dict:
    """
    Detecta datos nuevos de un índice, actualiza el caché y reporta cambios.
    """
    print(f"\n{'='*70}")
    print(f"ÍNDICE: {indice} — {INDICES_INFO[indice]['nombre']}")
    print(f"{'='*70}")

    # --- 1. Cargar caché existente ---
    df_cache = cargar_cache_stats(indice)
    fechas_en_cache = set(df_cache["fecha"].tolist()) if not df_cache.empty else set()

    # --- 2. Listar todas las imágenes disponibles ---
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)

    if not imagenes:
        print(f"  Sin imágenes en {ruta_indice}")
        return {"indice": indice, "nuevas": 0, "total": 0}

    # --- 3. Detectar fechas nuevas ---
    imagenes_nuevas = [
        img for img in imagenes
        if img["fecha_str"] and img["fecha_str"] not in fechas_en_cache
    ]

    print(f"\n  En caché:          {len(fechas_en_cache)} fechas")
    print(f"  Disponibles:       {len(imagenes)} fechas")
    print(f"  Nuevas a procesar: {len(imagenes_nuevas)} fechas")

    # --- 4. Procesar solo las nuevas ---
    nuevas_rows = []
    if imagenes_nuevas:
        print()
        for i, img in enumerate(imagenes_nuevas, 1):
            print(f"  [{i}/{len(imagenes_nuevas)}] {img['fecha_str']}... ", end="", flush=True)
            row = calcular_stats_imagen(img, indice)
            if row:
                nuevas_rows.append(row)
                fuente = row.get("fuente", "?").upper()
                print(f"OK  ({fuente}, media={row['media']:.4f})")
            else:
                print("OMITIDA (sin datos válidos)")

        df_nuevas = pd.DataFrame(nuevas_rows)
        df_completo = pd.concat([df_cache, df_nuevas], ignore_index=True)
        df_completo = df_completo.sort_values("fecha").reset_index(drop=True)

        guardar_cache_stats(indice, df_completo)
        print(f"\n  ✓ Caché actualizado — {len(df_completo)} fechas totales")
    else:
        print("  ✓ No hay datos nuevos — usando caché existente")
        df_completo = df_cache

    if df_completo.empty:
        print("  Sin datos para análisis temporal")
        return {"indice": indice, "nuevas": 0, "total": 0}

    # --- 5. Comparar tendencias ---
    resumen = comparar_y_reportar_tendencias(
        indice=indice,
        df_anterior=df_cache,
        df_actual=df_completo,
        n_nuevas=len(imagenes_nuevas),
    )
    resumen["nuevas"] = len(imagenes_nuevas)
    resumen["total"] = len(df_completo)

    # --- 6. Guardar CSV actualizado en reportes ---
    _guardar_reporte_csv(indice, df_completo)

    return resumen


def _guardar_reporte_csv(indice: str, df: pd.DataFrame) -> None:
    """Guarda el CSV con todas las estadísticas del índice en reportes/01_exploratorio/."""
    carpeta = RUTA_REPORTES / "01_exploratorio"
    carpeta.mkdir(exist_ok=True, parents=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta_csv = carpeta / f"estadisticas_actualizadas_{indice}_{ts}.csv"
    df.to_csv(ruta_csv, index=False)
    print(f"  ✓ CSV guardado: {ruta_csv.name}")


# ============================================================================
# RESUMEN FINAL
# ============================================================================

def _imprimir_resumen(resultados: list[dict]) -> None:
    print("\n" + "=" * 70)
    print("RESUMEN DE ACTUALIZACIÓN")
    print("=" * 70)
    print(f"\n{'ÍNDICE':<8}  {'NUEVAS':>7}  {'TOTAL':>6}  TENDENCIA ACTUAL")
    print("-" * 70)
    for r in resultados:
        t = r.get("tendencia_actual")
        if t:
            direccion = "↑ CRECIENTE" if t["pendiente"] > 0 else "↓ DECRECIENTE"
            sig = "(sig.)" if t["significativo"] else "(no sig.)"
            tendencia_str = f"{t['pendiente']:+.6f}/día  {direccion} {sig}"
        else:
            tendencia_str = "insuficientes datos"
        print(f"  {r['indice']:<6}  {r['nuevas']:>7}  {r['total']:>6}  {tendencia_str}")
    print()

    total_nuevas = sum(r["nuevas"] for r in resultados)
    if total_nuevas == 0:
        print("No se encontraron datos nuevos. El caché está al día.")
    else:
        print(f"Se integraron {total_nuevas} imagen(es) nueva(s) en total.")
        print(
            "\nNOTA: Las visualizaciones y reportes PDF no se regeneraron.\n"
            "      Ejecuta inicio_analisis.py si necesitas actualizarlos."
        )


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    print("""
================================================================================
    ACTUALIZACIÓN INCREMENTAL DE ANÁLISIS
================================================================================

  Detecta datos nuevos, calcula sus estadísticas y compara tendencias.
  Los datos anteriores se conservan en caché — no se re-procesan.

================================================================================
""")

    indices = obtener_indices_disponibles()
    if not indices:
        print("ERROR: No se encontraron índices en Tesis_DESCARGAS.")
        print(f"       Verifica la ruta: {RUTA_DESCARGAS}")
        return

    print(f"Índices disponibles: {', '.join(indices)}\n")

    resultados = []
    for indice in indices:
        resumen = actualizar_indice(indice)
        resultados.append(resumen)

    _imprimir_resumen(resultados)

    print("=" * 70)
    input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nActualización interrumpida por el usuario")
    except Exception as e:
        print(f"\nERROR inesperado: {e}")
        import traceback
        traceback.print_exc()
