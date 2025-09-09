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
    """Carga la lista de palabras/patrones desde config/palabras.txt.
       Devuelve (raw_list, compiled_regex_list)."""
    raws = []
    regexes = []
    if not path.exists():
        return raws, regexes

    txt = path.read_text(encoding='utf-8', errors='ignore')
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        raws.append(line)
        if line.startswith('re:'):
            pat = line[3:].strip()
            # Normalizamos la expresión para comparar sobre texto normalizado.
            pat_norm = normalize_text(pat)
            try:
                regexes.append(re.compile(pat_norm))
            except re.error:
                # Si la regex está mal, compilamos como literal
                regexes.append(re.compile(re.escape(pat_norm)))
        else:
            # coincidencia literal (normalizada)
            pat_norm = re.escape(normalize_text(line))
            regexes.append(re.compile(pat_norm))
    return raws, regexes

def main():
    ap = argparse.ArgumentParser(description="Limpia líneas del archivo diario según config/palabras.txt")
    ap.add_argument('--date', help='Forzar fecha dd-mm (por defecto hoy)')
    ap.add_argument('--debug', action='store_true', help='Muestra información adicional de depuración')
    args = ap.parse_args()

    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = args.date if args.date else datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"
    palabras_file = Path(__file__).parent / "config" / "palabras.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo: {archivo_hoy}")
        sys.exit(1)

    raws, regexes = load_palabras(palabras_file)
    if args.debug:
        print("📂 Archivo leído:", archivo_hoy)
        print("📄 palabras (crudas):")
        for r in raws:
            print("  -", r)
        print("🔎 patrones compilados:", len(regexes))

    texto = archivo_hoy.read_text(encoding='utf-8', errors='ignore')
    lines = texto.splitlines()

    kept = []
    removed = 0
    hits = []  # ejemplos de líneas eliminadas

    for i, line in enumerate(lines, start=1):
        norm_line = normalize_text(line)
        matched = False
        for idx, regex in enumerate(regexes):
            if regex.search(norm_line):
                matched = True
                removed += 1
                if args.debug and len(hits) < 50:
                    hits.append((i, line, raws[idx] if idx < len(raws) else "<patron desconocido>"))
                break
        if not matched:
            kept.append(line)

    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text("\n".join(kept), encoding='utf-8')

    print(f"✅ Guardado: {archivo_salida}")
    print(f"ℹ️  Líneas leídas: {len(lines)}  — Eliminadas: {removed}  — Resultado: {len(kept)}")

    if args.debug and hits:
        print("\nEjemplos de líneas eliminadas (línea, patrón, contenido):")
        for ln, contenido, patron in hits[:20]:
            print(f"{ln:4d}  |  {patron}  |  {contenido}")

if __name__ == "__main__":
    main()
