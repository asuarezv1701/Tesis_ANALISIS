"""
Script de utilidad para listar los índices disponibles en la carpeta de descargas
y verificar qué datos están disponibles para análisis.
"""

import os
from pathlib import Path

# Configuración
RUTA_BASE = r"c:\Users\XMK0181\Documents\TT\Tesis_DESCARGAS\descargas\UPIITA_contours_25nov.2025"

def listar_indices_disponibles():
    """
    Lista los índices disponibles en la carpeta de descargas.
    """
    print("="*80)
    print("ÍNDICES DISPONIBLES PARA ANÁLISIS")
    print("="*80)
    
    if not os.path.exists(RUTA_BASE):
        print(f"\nERROR: No se encontró la carpeta base:")
        print(f"{RUTA_BASE}")
        return
    
    print(f"\nBuscando en: {RUTA_BASE}\n")
    
    indices_encontrados = []
    
    for item in os.listdir(RUTA_BASE):
        ruta_item = os.path.join(RUTA_BASE, item)
        if os.path.isdir(ruta_item):
            # Contar imágenes en el índice
            try:
                carpetas_fechas = [d for d in os.listdir(ruta_item) 
                                  if os.path.isdir(os.path.join(ruta_item, d))]
                num_imagenes = len(carpetas_fechas)
                
                if num_imagenes > 0:
                    indices_encontrados.append({
                        'indice': item,
                        'num_imagenes': num_imagenes,
                        'ruta': ruta_item
                    })
            except Exception as e:
                print(f"Error al analizar {item}: {e}")
    
    if not indices_encontrados:
        print("No se encontraron índices con imágenes.")
        return
    
    print(f"{'Índice':<15} {'Imágenes':<12} {'Estado'}")
    print("-"*80)
    
    for info in sorted(indices_encontrados, key=lambda x: x['indice']):
        estado = "✓ Listo para análisis"
        print(f"{info['indice']:<15} {info['num_imagenes']:<12} {estado}")
    
    print("\n" + "="*80)
    print("CÓMO USAR LOS SCRIPTS")
    print("="*80)
    
    print("\n✓ Ambos scripts son ahora INTERACTIVOS")
    print("\n1. Para analizar índices:")
    print("   python analizar_rangos_indices.py")
    print("   → El script te preguntará qué índices quieres analizar")
    
    print("\n2. Para filtrar datos:")
    print("   python filtrar_datos_indices.py")
    print("   → El script te preguntará:")
    print("     • Qué índices filtrar")
    print("     • Los umbrales para cada índice")
    
    print("\n3. Flujo completo:")
    print("   a) Ejecuta analizar_rangos_indices.py")
    print("   b) Revisa las estadísticas generadas")
    print("   c) Ejecuta filtrar_datos_indices.py")
    print("   d) Ingresa los umbrales basándote en las estadísticas")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    listar_indices_disponibles()
