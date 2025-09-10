#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import re
import sys

def load_list(path: Path):
    """Carga palabras/patrones de un archivo, ignorando comentarios y vacías."""
    items = []
    if path.exists():
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for line in txt.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                items.append(line)
    return items

def limpiar_texto(texto, palabras, lineas, indent_words):
    lineas_limpias = []
    removed_words = 0
    removed_lines = 0

    for linea in texto.splitlines():
        norm_linea = linea

        # 1️⃣ Borrar línea completa si contiene alguna palabra de lineas.txt
        borrar_linea = any(re.search(re.escape(p), norm_linea, re.IGNORECASE) for p in lineas)
        if borrar_linea:
            removed_lines += 1
            continue

        # 2️⃣ Borrar palabras específicas dentro de la línea
        for p in palabras:
            pattern = re.compile(re.escape(p), flags=re.IGNORECASE)
            norm_linea, n = pattern.subn('', norm_linea)
            removed_words += n

        # 3️⃣ Agregar indentación si detecta palabras en indent.txt
        if any(re.search(re.escape(p), norm_linea, re.IGNORECASE) for p in indent_words):
            norm_linea = "  " + norm_linea  # 2 espacios

        lineas_limpias.append(norm_linea.strip())

    return "\n".join(lineas_limpias), removed_words, removed_lines

def main():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo: {archivo_hoy}")
        sys.exit(1)

    # Archivos de configuración
    palabras_file = Path(__file__).parent / "palabras.txt"
    lineas_file = Path(__file__).parent / "lineas.txt"
    indent_file = Path(__file__).parent / "indent.txt"

    palabras = load_list(palabras_file)
    lineas = load_list(lineas_file)
    indent_words = load_list(indent_file)

    texto = archivo_hoy.read_text(encoding='utf-8', errors='ignore')

    texto_limpio, removed_words, removed_lines = limpiar_texto(texto, palabras, lineas, indent_words)

    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text(texto_limpio, encoding='utf-8')

    print(f"✅ Guardado: {archivo_salida}")
    print(f"ℹ️  Palabras eliminadas: {removed_words}  — Líneas eliminadas: {removed_lines}")

if __name__ == "__main__":
    main()
