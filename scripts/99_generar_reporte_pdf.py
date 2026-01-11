"""
GENERADOR DE REPORTES PDF PROFESIONALES

Crea reportes en PDF con:
- Resumen ejecutivo
- Gráficas principales
- Tablas con resultados
- Interpretación de resultados

Formato profesional listo para incluir en tesis.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Agregar rutas
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configuracion.config import (
    RUTA_REPORTES,
    RUTA_VISUALIZACIONES,
    INDICES_INFO,
    obtener_indices_disponibles
)


def crear_portada(pdf, indice):
    """Crea portada del reporte."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    # Título principal
    plt.text(0.5, 0.7, 'REPORTE DE ANÁLISIS', 
             ha='center', va='center', fontsize=32, fontweight='bold')
    
    plt.text(0.5, 0.62, f'{INDICES_INFO[indice]["nombre"]}',
             ha='center', va='center', fontsize=24, color='#2E86AB')
    
    plt.text(0.5, 0.55, f'({indice})',
             ha='center', va='center', fontsize=18, color='gray')
    
    # Información
    plt.text(0.5, 0.4, 'Análisis Espacial y Temporal de Vegetación',
             ha='center', va='center', fontsize=14)
    
    plt.text(0.5, 0.35, 'UPIITA - Instituto Politécnico Nacional',
             ha='center', va='center', fontsize=12, style='italic')
    
    # Fecha
    plt.text(0.5, 0.2, f'Generado: {datetime.now().strftime("%d de %B de %Y")}',
             ha='center', va='center', fontsize=10, color='gray')
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()


def agregar_seccion(pdf, titulo):
    """Agrega página de separación de sección."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('#F5F5F5')
    
    plt.text(0.5, 0.5, titulo,
             ha='center', va='center', fontsize=28, fontweight='bold',
             color='#2E86AB')
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()


def agregar_resumen_ejecutivo(pdf, indice):
    """Agrega página con resumen ejecutivo."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    # Título
    plt.text(0.5, 0.95, 'RESUMEN EJECUTIVO',
             ha='center', va='top', fontsize=20, fontweight='bold')
    
    # Buscar archivos de tendencias temporales
    archivo_tendencias = RUTA_REPORTES / "03_temporal" / f"tendencias_{indice}_{datetime.now().strftime('%Y%m%d')}*.csv"
    archivos = list(RUTA_REPORTES.glob(f"03_temporal/tendencias_{indice}_*.csv"))
    
    if archivos:
        df = pd.read_csv(archivos[-1])  # Más reciente
        
        y_pos = 0.85
        
        # Información general
        plt.text(0.1, y_pos, f'Índice analizado: {INDICES_INFO[indice]["nombre"]}',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        plt.text(0.1, y_pos, f'Total de imágenes: {len(df)}',
                 ha='left', va='top', fontsize=10)
        y_pos -= 0.05
        
        if 'fecha_inicio' in df.columns:
            plt.text(0.1, y_pos, f'Período: {df["fecha_inicio"].iloc[0]} a {df["fecha_fin"].iloc[0]}',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.08
        
        # Resultados de tendencia
        plt.text(0.1, y_pos, 'RESULTADOS DE TENDENCIA TEMPORAL:',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        if 'pendiente' in df.columns:
            pendiente = df['pendiente'].iloc[0]
            r2 = df['r_cuadrado'].iloc[0]
            p_valor = df['p_valor'].iloc[0]
            
            # Interpretación
            if p_valor < 0.05:
                significancia = "SIGNIFICATIVA ✓"
                color_sig = 'green'
            else:
                significancia = "No significativa"
                color_sig = 'orange'
            
            if pendiente > 0:
                tendencia = "CRECIENTE (Mejorando)"
                color_tend = 'green'
            else:
                tendencia = "DECRECIENTE (Deteriorando)"
                color_tend = 'red'
            
            plt.text(0.1, y_pos, f'• Tendencia: {tendencia}',
                     ha='left', va='top', fontsize=11, color=color_tend, fontweight='bold')
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• Pendiente: {pendiente:.6f} unidades/día',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• R² = {r2:.3f} (Fuerza de tendencia)',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• Significancia: {significancia} (p={p_valor:.4f})',
                     ha='left', va='top', fontsize=10, color=color_sig, fontweight='bold')
            y_pos -= 0.06
        
        # Interpretación
        plt.text(0.1, y_pos, '¿QUÉ SIGNIFICA?',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.04
        
        explicacion = f"""
El índice {indice} ({INDICES_INFO[indice]['nombre']}) mide: {INDICES_INFO[indice]['descripcion']}

Durante el período analizado, se observa una tendencia {tendencia.lower()}.
"""
        
        for linea in explicacion.strip().split('\n'):
            plt.text(0.1, y_pos, linea.strip(), ha='left', va='top', fontsize=9, wrap=True)
            y_pos -= 0.03
    
    else:
        plt.text(0.5, 0.5, 'No se encontraron datos de análisis temporal',
                 ha='center', va='center', fontsize=12, color='gray')
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()


def agregar_graficas(pdf, indice):
    """Agrega las gráficas principales al PDF."""
    carpeta_vis = RUTA_VISUALIZACIONES / indice
    
    # Buscar gráficas por tipo
    tipos_analisis = ['exploratorio', 'temporal', 'espacial', 'prediccion']
    
    for tipo in tipos_analisis:
        carpeta_tipo = carpeta_vis / tipo
        
        if not carpeta_tipo.exists():
            continue
        
        # Agregar sección
        agregar_seccion(pdf, f'ANÁLISIS {tipo.upper()}')
        
        # Buscar imágenes PNG
        imagenes = sorted(carpeta_tipo.glob('*.png'))
        
        for img_path in imagenes[:10]:  # Máximo 10 imágenes por tipo
            fig = plt.figure(figsize=(8.5, 11))
            
            # Título con nombre del archivo
            plt.text(0.5, 0.98, img_path.stem.replace('_', ' ').title(),
                     ha='center', va='top', fontsize=14, fontweight='bold')
            
            # Cargar y mostrar imagen
            img = plt.imread(img_path)
            ax = plt.axes([0.1, 0.1, 0.8, 0.85])
            ax.imshow(img)
            ax.axis('off')
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()


def agregar_tabla_resultados(pdf, indice):
    """Agrega tablas con resultados numéricos."""
    agregar_seccion(pdf, 'RESULTADOS NUMÉRICOS')
    
    # Buscar CSVs de resultados
    carpetas_reportes = ['03_temporal', '02_espacial', '01_exploratorio']
    
    for carpeta in carpetas_reportes:
        ruta_carpeta = RUTA_REPORTES / carpeta
        
        if not ruta_carpeta.exists():
            continue
        
        # Buscar CSVs de este índice
        csvs = sorted(ruta_carpeta.glob(f'*{indice}*.csv'))
        
        for csv_path in csvs[:5]:  # Máximo 5 tablas por tipo
            try:
                df = pd.read_csv(csv_path)
                
                # Limitar columnas y filas para que quepa
                if len(df.columns) > 8:
                    df = df.iloc[:, :8]
                
                if len(df) > 30:
                    df = df.head(30)
                
                # Crear figura
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.axis('tight')
                ax.axis('off')
                
                # Título
                titulo = csv_path.stem.replace('_', ' ').title()
                plt.text(0.5, 0.98, titulo, ha='center', va='top',
                         fontsize=12, fontweight='bold', transform=fig.transFigure)
                
                # Crear tabla
                tabla = ax.table(cellText=df.values,
                                colLabels=df.columns,
                                cellLoc='center',
                                loc='center',
                                bbox=[0, 0, 1, 0.9])
                
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(8)
                tabla.scale(1, 1.5)
                
                # Estilo
                for (i, j), cell in tabla.get_celld().items():
                    if i == 0:
                        cell.set_facecolor('#2E86AB')
                        cell.set_text_props(weight='bold', color='white')
                    else:
                        if i % 2 == 0:
                            cell.set_facecolor('#F5F5F5')
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
            except Exception as e:
                print(f"⚠️  Error al procesar {csv_path.name}: {e}")
                continue


def generar_reporte_pdf(indice):
    """
    Genera reporte PDF completo para un índice.
    """
    print(f"\n{'='*80}")
    print(f"GENERANDO REPORTE PDF: {indice}")
    print(f"{'='*80}")
    
    # Crear carpeta de PDFs
    RUTA_REPORTES_PDF.mkdir(exist_ok=True, parents=True)
    
    # Nombre del archivo
    archivo_pdf = RUTA_REPORTES_PDF / f"Reporte_{indice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    print(f"\n📄 Creando PDF: {archivo_pdf.name}")
    
    # Crear PDF
    with PdfPages(archivo_pdf) as pdf:
        # 1. Portada
        print("  • Portada")
        crear_portada(pdf, indice)
        
        # 2. Resumen ejecutivo
        print("  • Resumen ejecutivo")
        agregar_resumen_ejecutivo(pdf, indice)
        
        # 3. Gráficas
        print("  • Gráficas de análisis")
        agregar_graficas(pdf, indice)
        
        # 4. Tablas
        print("  • Tablas de resultados")
        agregar_tabla_resultados(pdf, indice)
        
        # Metadata del PDF
        d = pdf.infodict()
        d['Title'] = f'Reporte de Análisis - {indice}'
        d['Author'] = 'Sistema de Análisis de Vegetación - UPIITA'
        d['Subject'] = f'Análisis de {INDICES_INFO[indice]["nombre"]}'
        d['Keywords'] = f'{indice}, vegetación, análisis temporal, análisis espacial'
        d['CreationDate'] = datetime.now()
    
    print(f"\n✅ PDF generado exitosamente")
    print(f"   Ubicación: {archivo_pdf}")
    print(f"   Tamaño: {archivo_pdf.stat().st_size / 1024:.1f} KB")
    
    return archivo_pdf


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              GENERADOR DE REPORTES PDF PROFESIONALES                      ║
║                                                                           ║
║  Crea reportes completos en PDF con gráficas y resultados                ║
║  listos para incluir en tu tesis o presentación.                         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Obtener índices
    indices_disponibles = obtener_indices_disponibles()
    
    if not indices_disponibles:
        print("\n❌ No se encontraron índices con datos.")
        sys.exit(1)
    
    # Detectar modo automático
    import os
    modo_automatico = os.environ.get('ANALISIS_AUTOMATICO') == '1'
    
    if modo_automatico:
        # Generar PDFs para todos
        print("\n🚀 Modo automático: generando PDFs para todos los índices\n")
        
        for indice in indices_disponibles:
            try:
                generar_reporte_pdf(indice)
            except Exception as e:
                print(f"⚠️  Error al generar PDF para {indice}: {e}")
    
    else:
        # Modo interactivo
        while True:
            print("\n" + "="*80)
            print("MENÚ DE GENERACIÓN DE PDFs")
            print("="*80)
            
            print("\nÍNDICES DISPONIBLES:")
            for i, indice in enumerate(indices_disponibles, 1):
                print(f"  {i}. {indice} - {INDICES_INFO[indice]['nombre']}")
            
            print("\nOPCIONES:")
            print("  A. Generar PDFs de TODOS los índices")
            print("  0. Salir")
            
            opcion = input("\nSelecciona una opción: ").strip().upper()
            
            if opcion == '0':
                break
            
            elif opcion == 'A':
                for indice in indices_disponibles:
                    try:
                        generar_reporte_pdf(indice)
                    except Exception as e:
                        print(f"⚠️  Error: {e}")
            
            elif opcion.isdigit():
                num = int(opcion) - 1
                if 0 <= num < len(indices_disponibles):
                    try:
                        generar_reporte_pdf(indices_disponibles[num])
                    except Exception as e:
                        print(f"⚠️  Error: {e}")
    
    print("\n✓ Proceso completado")
    print(f"\n📁 Los PDFs están en: {RUTA_REPORTES_PDF.absolute()}")
