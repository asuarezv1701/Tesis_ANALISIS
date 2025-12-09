"""
Genera visualizaciones de la evolución temporal y distribución de valores por índice.
- Lee estadisticas_<INDICE>.csv generadas por analizar_rangos_indices.py
- Lee CSVs por imagen generados en datos_filtrados/<INDICE>/<FECHA>/pixeles_<INDICE>_<FECHA>.csv
- Produce gráficos de serie temporal (media/mediana por fecha) y boxplots por fecha
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

BASE_ANALISIS = os.path.dirname(os.path.abspath(__file__))
SALIDA_VIS = os.path.join(BASE_ANALISIS, 'visualizaciones')
SALIDA_DATOS = os.path.join(BASE_ANALISIS, 'datos_filtrados')

INDICES = ["NDVI", "NDRE", "MSAVI", "RECI", "NDMI"]

os.makedirs(SALIDA_VIS, exist_ok=True)


def cargar_estadisticas(indice):
    path = os.path.join(BASE_ANALISIS, 'reportes', f"estadisticas_{indice}.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Convertir fecha si está
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        return df
    return None


def cargar_pixeles_filtrados(indice):
    base = os.path.join(SALIDA_DATOS, indice)
    if not os.path.exists(base):
        return None
    registros = []
    for carpeta in sorted(os.listdir(base)):
        ruta_carpeta = os.path.join(base, carpeta)
        if not os.path.isdir(ruta_carpeta):
            continue
        # CSV por imagen
        patrones = glob.glob(os.path.join(ruta_carpeta, f"pixeles_{indice}_{carpeta}.csv"))
        for csv in patrones:
            try:
                df = pd.read_csv(csv)
                # Fecha desde la carpeta
                fecha = extraer_fecha(carpeta)
                df['fecha'] = fecha
                registros.append(df)
            except Exception:
                pass
    if registros:
        df_all = pd.concat(registros, ignore_index=True)
        return df_all
    return None


def extraer_fecha(nombre_carpeta):
    try:
        partes = nombre_carpeta.split('_')
        for p in partes:
            if len(p) == 8 and p.isdigit():
                return datetime.strptime(p, '%Y%m%d')
    except Exception:
        return None
    return None


def plot_series(indice, df_stats, df_pixels):
    fig_dir = os.path.join(SALIDA_VIS, indice)
    os.makedirs(fig_dir, exist_ok=True)

    # Serie temporal desde estadísticas (media/mediana por fecha)
    if df_stats is not None and 'fecha' in df_stats.columns:
        df_s = df_stats[['fecha','media','mediana']].dropna()
        plt.figure(figsize=(10,5))
        plt.plot(df_s['fecha'], df_s['media'], marker='o', label='Media')
        plt.plot(df_s['fecha'], df_s['mediana'], marker='s', label='Mediana')
        plt.title(f"Serie temporal ({indice}) - Media y Mediana")
        plt.xlabel("Fecha")
        plt.ylabel(indice)
        plt.grid(True, alpha=0.3)
        plt.legend()
        out = os.path.join(fig_dir, f"serie_media_mediana_{indice}.png")
        plt.tight_layout()
        plt.savefig(out, dpi=150)
        plt.close()

    # Boxplot por fecha usando pixeles
    if df_pixels is not None and 'fecha' in df_pixels.columns:
        dfp = df_pixels.dropna()
        dfp = dfp.rename(columns={indice: 'valor'})
        # Ordenar por fecha
        dfp['fecha'] = pd.to_datetime(dfp['fecha'], errors='coerce')
        fechas = sorted(dfp['fecha'].dropna().unique())
        datos = [dfp[dfp['fecha']==f]['valor'].values for f in fechas]
        if len(datos) > 0:
            plt.figure(figsize=(12,5))
            plt.boxplot(datos, labels=[f.strftime('%Y-%m-%d') for f in fechas], showfliers=False)
            plt.title(f"Distribución por fecha ({indice})")
            plt.xlabel("Fecha")
            plt.ylabel(indice)
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, axis='y', alpha=0.3)
            out = os.path.join(fig_dir, f"boxplot_por_fecha_{indice}.png")
            plt.tight_layout()
            plt.savefig(out, dpi=150)
            plt.close()


def main():
    print("="*80)
    print("GRAFICAR SERIES Y DISTRIBUCIONES POR ÍNDICE")
    print("="*80)
    print(f"Guardando en: {SALIDA_VIS}\n")

    generadas = []
    for indice in INDICES:
        df_stats = cargar_estadisticas(indice)
        df_pixels = cargar_pixeles_filtrados(indice)

        if df_stats is None and df_pixels is None:
            continue

        plot_series(indice, df_stats, df_pixels)
        generadas.append(indice)
        print(f"✓ Figuras generadas para {indice}")

    if not generadas:
        print("No se encontraron datos para graficar. Asegúrate de ejecutar análisis y filtrado primero.")
    else:
        print("\nFiguras guardadas en:")
        print(f"  {SALIDA_VIS}")


if __name__ == "__main__":
    main()
