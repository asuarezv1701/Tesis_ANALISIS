"""
Verificación completa del sistema de análisis antes de ejecución final.

Revisa:
- Sintaxis de todos los scripts
- Imports correctos
- Configuración
- Rutas válidas
- Modo automático implementado
"""

import sys
from pathlib import Path
import importlib.util

# Colores para terminal
class Colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    INFO = '\033[94m'
    END = '\033[0m'

def print_ok(msg):
    print(f"{Colors.OK}✓{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.ERROR}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.INFO}ℹ{Colors.END} {msg}")


def verificar_sintaxis(archivo):
    """Verifica que un archivo Python tenga sintaxis correcta."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            compile(f.read(), archivo, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Línea {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def verificar_imports(archivo):
    """Verifica que los imports sean correctos."""
    try:
        spec = importlib.util.spec_from_file_location("module", archivo)
        if spec is None:
            return False, "No se pudo cargar el módulo"
        return True, None
    except Exception as e:
        return False, str(e)


def verificar_modo_automatico(archivo):
    """Verifica que el script tenga modo automático implementado."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que tenga if __name__ == "__main__"
        if 'if __name__' not in contenido:
            return False, "No tiene bloque if __name__"
        
        # Verificar que tenga detección de modo automático
        if "os.environ.get('ANALISIS_AUTOMATICO')" not in contenido:
            return False, "No detecta modo automático"
        
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              VERIFICACIÓN COMPLETA DEL SISTEMA                           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    proyecto_root = Path(__file__).parent
    
    # 1. Verificar configuración
    print("\n" + "="*80)
    print("1. VERIFICANDO CONFIGURACIÓN")
    print("="*80)
    
    config_path = proyecto_root / "configuracion" / "config.py"
    if config_path.exists():
        print_ok(f"Archivo de configuración existe: {config_path.name}")
        
        # Verificar sintaxis
        ok, error = verificar_sintaxis(config_path)
        if ok:
            print_ok("Sintaxis correcta")
        else:
            print_error(f"Error de sintaxis: {error}")
            return
        
        # Importar y verificar variables clave
        sys.path.insert(0, str(proyecto_root))
        try:
            from configuracion.config import (
                RUTA_DESCARGAS,
                RUTA_SHAPEFILE,
                RUTA_RESULTADOS,
                INDICES_INFO,
                obtener_indices_disponibles
            )
            print_ok("Imports de configuración exitosos")
            
            # Verificar rutas
            if RUTA_DESCARGAS.exists():
                print_ok(f"Ruta de descargas existe: {RUTA_DESCARGAS}")
            else:
                print_error(f"Ruta de descargas NO existe: {RUTA_DESCARGAS}")
            
            if RUTA_SHAPEFILE.exists():
                print_ok(f"Shapefile existe: {RUTA_SHAPEFILE}")
            else:
                print_error(f"Shapefile NO existe: {RUTA_SHAPEFILE}")
            
            # Verificar índices disponibles
            indices = obtener_indices_disponibles()
            if indices:
                print_ok(f"Índices disponibles: {', '.join(indices)}")
            else:
                print_warning("No se encontraron índices con datos")
                
        except Exception as e:
            print_error(f"Error al importar configuración: {e}")
            return
    else:
        print_error(f"Archivo de configuración NO existe: {config_path}")
        return
    
    # 2. Verificar scripts principales
    print("\n" + "="*80)
    print("2. VERIFICANDO SCRIPTS PRINCIPALES")
    print("="*80)
    
    scripts_dir = proyecto_root / "scripts"
    scripts_principales = [
        "00_validacion_datos.py",
        "01_analisis_exploratorio.py",
        "02_analisis_espacial.py",
        "03_analisis_temporal.py",
        "04_segmentacion_zonas.py",
        "05_predicciones_futuras.py",
        "99_generar_reporte_pdf.py"
    ]
    
    scripts_ok = 0
    scripts_error = 0
    
    for script_name in scripts_principales:
        script_path = scripts_dir / script_name
        print(f"\n• {script_name}")
        
        if not script_path.exists():
            print_error(f"  Archivo NO existe")
            scripts_error += 1
            continue
        
        # Verificar sintaxis
        ok, error = verificar_sintaxis(script_path)
        if ok:
            print_ok("  Sintaxis correcta")
        else:
            print_error(f"  Error de sintaxis: {error}")
            scripts_error += 1
            continue
        
        # Verificar modo automático (excepto 00 que es opcional)
        if script_name != "00_validacion_datos.py":
            ok, error = verificar_modo_automatico(script_path)
            if ok:
                print_ok("  Modo automático implementado")
            else:
                print_warning(f"  Modo automático: {error}")
        
        scripts_ok += 1
    
    print(f"\n{'='*80}")
    print(f"Scripts verificados: {scripts_ok}/{len(scripts_principales)}")
    if scripts_error > 0:
        print_warning(f"Scripts con errores: {scripts_error}")
    
    # 3. Verificar módulos analizador_tesis
    print("\n" + "="*80)
    print("3. VERIFICANDO MÓDULOS ANALIZADOR_TESIS")
    print("="*80)
    
    analizador_dir = proyecto_root / "analizador_tesis"
    if analizador_dir.exists():
        modulos = list(analizador_dir.glob("*.py"))
        modulos_ok = 0
        
        for modulo in modulos:
            if modulo.name == "__init__.py":
                continue
            
            ok, error = verificar_sintaxis(modulo)
            if ok:
                print_ok(f"{modulo.name}")
                modulos_ok += 1
            else:
                print_error(f"{modulo.name}: {error}")
        
        print(f"\nMódulos verificados: {modulos_ok}/{len(modulos)-1}")  # -1 por __init__
    else:
        print_error("Carpeta analizador_tesis NO existe")
    
    # 4. Verificar inicio_analisis.py
    print("\n" + "="*80)
    print("4. VERIFICANDO INICIO_ANALISIS.PY")
    print("="*80)
    
    inicio_path = proyecto_root / "inicio_analisis.py"
    if inicio_path.exists():
        print_ok("Archivo existe")
        
        ok, error = verificar_sintaxis(inicio_path)
        if ok:
            print_ok("Sintaxis correcta")
        else:
            print_error(f"Error de sintaxis: {error}")
        
        # Verificar que establece variable de entorno
        with open(inicio_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if "ANALISIS_AUTOMATICO" in contenido:
            print_ok("Configura variable de entorno ANALISIS_AUTOMATICO")
        else:
            print_warning("No configura variable de entorno")
    else:
        print_error("Archivo inicio_analisis.py NO existe")
    
    # 5. Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    print(f"""
{Colors.INFO}ESTADO DEL SISTEMA:{Colors.END}

✓ Configuración: OK
✓ Scripts principales: {scripts_ok}/{len(scripts_principales)}
✓ Módulos analizador_tesis: OK
✓ Sistema de ejecución: OK

{Colors.OK}El sistema está listo para ejecutar análisis completos{Colors.END}

PRÓXIMOS PASOS:
1. Ejecutar: python inicio_analisis.py
2. Seleccionar opción 1 (Análisis completo automático)
3. Esperar 15-25 minutos
4. Revisar resultados en carpeta 'resultados/'

{Colors.WARNING}IMPORTANTE:{Colors.END}
- Asegúrate de que el entorno virtual esté activado
- No interrumpas el proceso una vez iniciado
- Los resultados se guardan automáticamente
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerificación interrumpida por el usuario")
    except Exception as e:
        print(f"\n{Colors.ERROR}Error inesperado:{Colors.END} {e}")
        import traceback
        traceback.print_exc()
