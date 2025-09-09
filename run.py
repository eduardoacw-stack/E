#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import unicodedata
import re
import argparse
import sys

def normalize_text(s: str) -> str:
    """Normaliza texto: NFKD, elimina diacríticos y casefold."""
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return s.casefold()

def load_palabras(path: Path):
    """Carga la lista de palabras desde palabras.txt."""
    palabras = []
    if path.exists():
        txt = path.read_text(encoding='utf-8', errors='ignore')
        for line in txt.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                palabras.append(line)
    return palabras

def limpiar_texto(texto: str, palabras: list):
    """Elimina las palabras de cada línea sin borrar la línea completa."""
    lineas_limpias = []
    removed_count = 0
    for linea in texto.splitlines():
        nueva_linea = linea
        for p in palabras:
            # reemplazo insensible a mayúsculas y acentos
            pattern = re.compile(re.escape(p), flags=re.IGNORECASE)
            nueva_linea, n = pattern.subn('', nueva_linea)
            removed_count += n
        lineas_limpias.append(nueva_linea.strip())  # quitamos espacios sobrantes
    return "\n".join(lineas_limpias), removed_count

def main():
    ap = argparse.ArgumentParser(description="Limpia palabras del archivo diario")
    ap.add_argument('--date', help='Forzar fecha dd-mm (por defecto hoy)')
    ap.add_argument('--debug', action='store_true', help='Muestra información de depuración')
    args = ap.parse_args()

    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = args.date if args.date else datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"
    palabras_file = Path(__file__).parent / "palabras.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo: {archivo_hoy}")
        sys.exit(1)

    palabras = load_palabras(palabras_file)
    texto = archivo_hoy.read_text(encoding='utf-8', errors='ignore')

    texto_limpio, removed_count = limpiar_texto(texto, palabras)

    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text(texto_limpio, encoding='utf-8')

    print(f"✅ Guardado: {archivo_salida}")
    print(f"ℹ️  Palabras eliminadas: {removed_count}")

    if args.debug:
        print("--- Lista de palabras aplicadas ---")
        for p in palabras:
            print("-", p)

if __name__ == "__main__":
    main()
