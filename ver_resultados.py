"""
Visor de Resultados - Análisis de Índices de Vegetación

Este script te permite:
1. Ver las gráficas generadas
2. Explorar las carpetas de resultados
3. Generar un reporte HTML con todas las visualizaciones

Uso:
    python ver_resultados.py
"""

import sys
from pathlib import Path
import webbrowser
from datetime import datetime

# Agregar rutas
sys.path.append(str(Path(__file__).parent))

from configuracion.config import (
    RUTA_VISUALIZACIONES,
    RUTA_REPORTES,
    obtener_indices_disponibles,
    INDICES_INFO
)


def listar_visualizaciones(indice=None):
    """Lista todas las visualizaciones disponibles."""
    print("\n" + "="*80)
    print("VISUALIZACIONES DISPONIBLES")
    print("="*80)
    
    if indice:
        indices = [indice]
    else:
        indices = obtener_indices_disponibles()
    
    total_archivos = 0
    
    for idx in indices:
        carpeta_idx = RUTA_VISUALIZACIONES / idx
        if not carpeta_idx.exists():
            continue
        
        print(f"\n📊 {idx} - {INDICES_INFO[idx]['nombre']}")
        print("-" * 80)
        
        # Listar por tipo de análisis
        for tipo in ['exploratorio', 'temporal', 'espacial', 'segmentacion']:
            carpeta_tipo = carpeta_idx / tipo
            if carpeta_tipo.exists():
                archivos = list(carpeta_tipo.glob('*.png'))
                if archivos:
                    print(f"\n  {tipo.upper()}: {len(archivos)} visualizaciones")
                    for i, archivo in enumerate(sorted(archivos)[-3:], 1):  # Últimas 3
                        print(f"    {i}. {archivo.name}")
                    if len(archivos) > 3:
                        print(f"    ... y {len(archivos)-3} más")
                    total_archivos += len(archivos)
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {total_archivos} visualizaciones generadas")
    print(f"{'='*80}")
    
    return total_archivos


def abrir_carpeta_visualizaciones(indice=None):
    """Abre la carpeta de visualizaciones en el explorador."""
    if indice:
        carpeta = RUTA_VISUALIZACIONES / indice
    else:
        carpeta = RUTA_VISUALIZACIONES
    
    if carpeta.exists():
        import subprocess
        subprocess.Popen(f'explorer "{carpeta}"')
        print(f"\nAbriendo carpeta: {carpeta}")
    else:
        print(f"\nADVERTENCIA: Carpeta no existe: {carpeta}")


def generar_reporte_html():
    """Genera un reporte HTML con todas las visualizaciones."""
    print("\n" + "="*80)
    print("GENERANDO REPORTE HTML")
    print("="*80)
    
    indices = obtener_indices_disponibles()
    
    if not indices:
        print("\nADVERTENCIA: No hay índices con visualizaciones")
        return
    
    # Crear HTML
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Análisis - Índices de Vegetación</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #27ae60;
            padding-bottom: 10px;
        }
        h2 {
            color: #27ae60;
            margin-top: 40px;
            border-left: 5px solid #27ae60;
            padding-left: 10px;
        }
        h3 {
            color: #34495e;
            margin-top: 30px;
        }
        .indice-section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .analisis-tipo {
            margin: 20px 0;
        }
        img {
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .image-container {
            text-align: center;
        }
        .image-title {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        .stats {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            margin-top: 40px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>Reporte de Análisis de Índices de Vegetación</h1>
    <div class="stats">
        <p><strong>Fecha de generación:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <p><strong>Proyecto:</strong> Análisis de Áreas Verdes - Tesis UPIITA</p>
    </div>
"""
    
    total_imgs = 0
    
    for indice in indices:
        carpeta_idx = RUTA_VISUALIZACIONES / indice
        if not carpeta_idx.exists():
            continue
        
        html += f"""
    <div class="indice-section">
        <h2>{indice} - {INDICES_INFO[indice]['nombre']}</h2>
        <p><strong>Descripción:</strong> {INDICES_INFO[indice]['descripcion']}</p>
        <p><strong>Rango:</strong> {INDICES_INFO[indice]['rango']}</p>
"""
        
        # Procesar cada tipo de análisis
        for tipo in ['exploratorio', 'temporal', 'espacial', 'segmentacion']:
            carpeta_tipo = carpeta_idx / tipo
            if not carpeta_tipo.exists():
                continue
            
            archivos = sorted(carpeta_tipo.glob('*.png'))
            if not archivos:
                continue
            
            html += f"""
        <div class="analisis-tipo">
            <h3>{tipo.upper()}</h3>
            <div class="gallery">
"""
            
            for archivo in archivos:
                # Ruta relativa desde el HTML
                ruta_relativa = archivo.relative_to(RUTA_VISUALIZACIONES.parent)
                html += f"""
                <div class="image-container">
                    <img src="{ruta_relativa.as_posix()}" alt="{archivo.stem}">
                    <p class="image-title">{archivo.stem}</p>
                </div>
"""
                total_imgs += 1
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
"""
    
    html += f"""
    <div class="timestamp">
        <p>Reporte generado automáticamente | Total de visualizaciones: {total_imgs}</p>
    </div>
</body>
</html>
"""
    
    # Guardar HTML
    archivo_html = RUTA_VISUALIZACIONES.parent / "reporte_visualizaciones.html"
    archivo_html.write_text(html, encoding='utf-8')
    
    print(f"\nReporte HTML generado: {archivo_html}")
    print(f"Total de imágenes incluidas: {total_imgs}")
    
    # Abrir en navegador
    webbrowser.open(archivo_html.as_uri())
    print("\nAbriendo reporte en navegador...")
    
    return archivo_html


def menu_principal():
    """Menú principal del visor."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                  VISOR DE RESULTADOS Y VISUALIZACIONES                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n" + "="*80)
        print("OPCIONES")
        print("="*80)
        print("""
  1. Listar todas las visualizaciones
  2. Abrir carpeta de visualizaciones (explorador)
  3. Generar reporte HTML completo
  4. 📊 Ver visualizaciones de un índice específico
  5. Abrir carpeta de reportes CSV
  
  0. Salir
        """)
        
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == '0':
            print("\n¡Hasta pronto!")
            break
        
        elif opcion == '1':
            listar_visualizaciones()
        
        elif opcion == '2':
            abrir_carpeta_visualizaciones()
        
        elif opcion == '3':
            generar_reporte_html()
        
        elif opcion == '4':
            indices = obtener_indices_disponibles()
            print("\nÍndices disponibles:")
            for i, idx in enumerate(indices, 1):
                print(f"  {i}. {idx}")
            
            num = input("\nSelecciona número: ").strip()
            if num.isdigit():
                idx_num = int(num) - 1
                if 0 <= idx_num < len(indices):
                    listar_visualizaciones(indices[idx_num])
                    
                    abrir = input("\n¿Abrir carpeta? (s/n): ").strip().lower()
                    if abrir == 's':
                        abrir_carpeta_visualizaciones(indices[idx_num])
        
        elif opcion == '5':
            if RUTA_REPORTES.exists():
                import subprocess
                subprocess.Popen(f'explorer "{RUTA_REPORTES}"')
                print(f"\nAbriendo carpeta: {RUTA_REPORTES}")
            else:
                print(f"\nADVERTENCIA: Carpeta no existe: {RUTA_REPORTES}")
        
        else:
            print("\nADVERTENCIA: Opción no válida")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nSistema interrumpido")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
