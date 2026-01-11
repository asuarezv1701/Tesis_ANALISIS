"""
EJEMPLO DE USO DE ARCHIVOS CSV DE PÍXELES

Este script muestra cómo usar los archivos CSV que contienen valores
de píxeles con coordenadas (longitude, latitude, valor).

Los CSVs están en:
descargas/INDICE/carpeta_fecha/valores_pixeles/*.csv
"""

import sys
from pathlib import Path
import pandas as pd

# Configuración
sys.path.append(str(Path(__file__).parent.parent))

from configuracion.config import RUTA_DESCARGAS
from analizador_tesis.procesador_base import (
    listar_imagenes_indice,
    cargar_csv_pixeles
)


def ejemplo_leer_csv_pixeles(indice="MSAVI"):
    """
    Ejemplo de cómo leer archivos CSV de píxeles.
    """
    print("="*80)
    print(f"EJEMPLO: LECTURA DE CSV DE PÍXELES - {indice}")
    print("="*80)
    
    # Listar imágenes del índice
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    print(f"\nImágenes encontradas: {len(imagenes)}")
    
    # Procesar primera imagen como ejemplo
    if imagenes:
        img_info = imagenes[0]
        
        print(f"\n📄 Procesando: {img_info['nombre_archivo']}")
        print(f"   Fecha: {img_info['fecha_str']}")
        
        # Verificar si tiene CSV de píxeles
        if img_info['csv_pixeles']:
            print(f"   CSV: {img_info['csv_pixeles'].name}")
            
            # Cargar CSV
            df = cargar_csv_pixeles(img_info['csv_pixeles'], filtrar_ceros=True)
            
            print(f"\n📊 Datos del CSV (filtrado):")
            print(f"   Total de píxeles válidos: {len(df):,}")
            print(f"   Columnas: {list(df.columns)}")
            
            # Estadísticas básicas
            print(f"\n📈 Estadísticas del índice {indice}:")
            print(f"   Mínimo: {df['valor'].min():.4f}")
            print(f"   Máximo: {df['valor'].max():.4f}")
            print(f"   Media: {df['valor'].mean():.4f}")
            print(f"   Mediana: {df['valor'].median():.4f}")
            
            # Mostrar primeros píxeles
            print(f"\n📍 Primeros 5 píxeles (sin ceros):")
            print(df.head().to_string(index=False))
            
        else:
            print("   ⚠️ No se encontró CSV de píxeles")
    
    else:
        print(f"\n⚠️ No se encontraron imágenes para {indice}")


def ejemplo_analisis_comparativo():
    """
    Ejemplo de análisis comparativo entre fechas usando CSVs.
    """
    print("\n" + "="*80)
    print("EJEMPLO: COMPARACIÓN ENTRE FECHAS")
    print("="*80)
    
    indice = "NDVI"
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if len(imagenes) >= 2:
        # Comparar primera y última imagen
        img1 = imagenes[0]
        img2 = imagenes[-1]
        
        if img1['csv_pixeles'] and img2['csv_pixeles']:
            df1 = cargar_csv_pixeles(img1['csv_pixeles'])
            df2 = cargar_csv_pixeles(img2['csv_pixeles'])
            
            print(f"\n📅 Fecha 1: {img1['fecha_str']}")
            print(f"   Media {indice}: {df1['valor'].mean():.4f}")
            
            print(f"\n📅 Fecha 2: {img2['fecha_str']}")
            print(f"   Media {indice}: {df2['valor'].mean():.4f}")
            
            diferencia = df2['valor'].mean() - df1['valor'].mean()
            print(f"\n📊 Cambio: {diferencia:+.4f}")
            
            if diferencia > 0:
                print("   ↗ Incremento en vegetación")
            else:
                print("   ↘ Decremento en vegetación")


if __name__ == "__main__":
    # Lista de todos los índices
    indices = ["MSAVI", "NDMI", "NDRE", "NDVI", "RECI"]
    
    # Ejecutar para cada índice
    for indice in indices:
        ejemplo_leer_csv_pixeles(indice)
        print("\n")
    
    # Comparación entre fechas para cada índice
    print("\n" + "="*80)
    print("COMPARACIONES TEMPORALES POR ÍNDICE")
    print("="*80)
    
    for indice in indices:
        ruta_indice = RUTA_DESCARGAS / indice
        imagenes = listar_imagenes_indice(ruta_indice)
        
        if len(imagenes) >= 2:
            img1 = imagenes[0]
            img2 = imagenes[-1]
            
            if img1['csv_pixeles'] and img2['csv_pixeles']:
                df1 = cargar_csv_pixeles(img1['csv_pixeles'])
                df2 = cargar_csv_pixeles(img2['csv_pixeles'])
                
                print(f"\n📊 {indice}:")
                print(f"   Fecha inicial: {img1['fecha_str']} → Media: {df1['valor'].mean():.4f}")
                print(f"   Fecha final:   {img2['fecha_str']} → Media: {df2['valor'].mean():.4f}")
                
                diferencia = df2['valor'].mean() - df1['valor'].mean()
                print(f"   Cambio: {diferencia:+.4f} {'↗ Incremento' if diferencia > 0 else '↘ Decremento'}")
    
    print("\n" + "="*80)
    print("✓ Análisis completado para todos los índices")
    print("="*80)
