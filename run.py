#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

# Carpeta donde están los archivos de información diaria
carpeta = Path.home() / "storage/shared/paradas"

# Fecha de hoy (formato dd-mm)
fecha = datetime.now().strftime("%d-%m")
archivo_hoy = carpeta / f"{fecha}.txt"

# Verificar si existe
if archivo_hoy.exists():
    print(f"Archivo encontrado para hoy: {archivo_hoy}")
else:
    print(f"No se encontró archivo para hoy en: {archivo_hoy}")
