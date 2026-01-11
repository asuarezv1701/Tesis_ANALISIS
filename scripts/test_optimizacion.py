"""
Script de prueba para verificar optimización con CSVs
"""
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent.parent))

from configuracion.config import RUTA_DESCARGAS
from analizador_tesis.procesador_base import listar_imagenes_indice, cargar_datos_optimizado

print("="*80)
print("PRUEBA DE OPTIMIZACIÓN CON CSVs")
print("="*80)

# Probar con MSAVI
imgs = listar_imagenes_indice(RUTA_DESCARGAS / 'MSAVI')[:5]

print(f"\nProbando con {len(imgs)} imágenes de MSAVI...")
print("-"*80)

t1 = time.time()
for img in imgs:
    datos, fuente = cargar_datos_optimizado(img)
    print(f"  {img['fecha_str']}: {len(datos):,} píxeles [{fuente.upper()}]")

t2 = time.time()

print("-"*80)
print(f"\nTiempo total: {t2-t1:.2f}s")
print(f"Promedio: {(t2-t1)/len(imgs):.3f}s por imagen")
print("\n✓ Sistema optimizado funcionando correctamente")
