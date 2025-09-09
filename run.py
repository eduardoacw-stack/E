#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

def load_palabras(path):
    palabras = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):  # ignorar líneas vacías o comentarios
                    continue
                palabras.append(line)
    return palabras

def main():
    # 📂 Carpeta donde están los archivos de información diaria
    carpeta = Path.home() / "storage/shared/paradas"

    # 📅 Fecha de hoy (formato dd-mm)
    fecha = datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"

    # 📋 Archivo de configuración con palabras a borrar
    palabras_file = Path(__file__).parent / "config" / "palabras.txt"

    # 🔎 Verificar archivo de hoy
    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo para hoy: {archivo_hoy}")
        return

    print(f"✅ Archivo encontrado: {archivo_hoy}")

    # 📖 Leer texto de hoy
    texto = archivo_hoy.read_text(encoding="utf-8", errors="ignore")

    # 📖 Cargar lista de palabras
    palabras = load_palabras(palabras_file)

    print("\n--- Texto original (primeras 15 líneas) ---")
    for linea in texto.splitlines()[:15]:
        print(linea)

    print("\n--- Palabras cargadas ---")
    for p in palabras:
        print("-", p)

if __name__ == "__main__":
    main()
