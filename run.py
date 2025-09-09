#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

def load_palabras(path):
    palabras = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                palabras.append(line)
    return palabras

def limpiar_texto(texto, palabras):
    lineas_limpias = []
    for linea in texto.splitlines():
        if any(p in linea for p in palabras):
            continue
        lineas_limpias.append(linea)
    return "\n".join(lineas_limpias)

def main():
    # 📂 Carpeta compartida "paradas"
    carpeta = Path.home() / "storage/shared/paradas"

    # 📅 Archivo de hoy
    fecha = datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"

    # 📋 Lista de palabras a borrar
    palabras_file = Path(__file__).parent / "palabras.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo para hoy: {archivo_hoy}")
        return

    print(f"✅ Archivo encontrado: {archivo_hoy}")

    # Leer texto original
    texto = archivo_hoy.read_text(encoding="utf-8", errors="ignore")
    palabras = load_palabras(palabras_file)

    # Limpiar texto
    texto_limpio = limpiar_texto(texto, palabras)

    # Guardar archivo limpio en la misma carpeta con sufijo "_clean"
    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text(texto_limpio, encoding="utf-8")

    print(f"✅ Archivo limpio guardado en: {archivo_salida}")

if __name__ == "__main__":
    main()
