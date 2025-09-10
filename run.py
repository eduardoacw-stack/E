#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import unicodedata
import re
import csv
import sys
import argparse

# ---------------- utilidades de normalización ----------------
def normalize_text(s: str) -> str:
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return s.casefold()

def normalize_with_mapping(s: str):
    """Devuelve (normalized_string, mapping) donde mapping[i] = índice en s
       del carácter original que originó normalized_string[i]."""
    norm_chars = []
    mapping = []
    for i, ch in enumerate(s):
        decomp = unicodedata.normalize('NFKD', ch)
        for d in decomp:
            if unicodedata.category(d) == 'Mn':
                continue
            norm_chars.append(d.casefold())
            mapping.append(i)
    return ''.join(norm_chars), mapping

# ---------------- cargar configuraciones ----------------
def load_list(path: Path):
    items = []
    if path.exists():
        for ln in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            ln = ln.strip()
            if ln and not ln.startswith('#'):
                items.append(ln)
    return items

# ---------------- limpieza inline preservando acentos ----------------
def remove_inline_patterns_preserve_original(line: str, patterns: list):
    """Para cada patrón en patterns (literal), busca coincidencias insensibles a acentos y case,
       y elimina los fragmentos de la línea original preservando lo demás."""
    orig = line
    for pat in patterns:
        npat = normalize_text(pat)
        if not npat:
            continue
        # repetimos hasta que no haya más coincidencias (por si tras borrar aparecen nuevas coincidencias)
        while True:
            norm_line, mapping = normalize_with_mapping(orig)
            # buscar todas las coincidencias literales del patrón normalizado
            matches = list(re.finditer(re.escape(npat), norm_line, flags=0))
            if not matches:
                break
            # convertir a intervalos sobre la cadena original (usar mapping)
            intervals = []
            for m in matches:
                s = m.start(); e = m.end() - 1
                orig_start = mapping[s]
                orig_end = mapping[e]
                intervals.append((orig_start, orig_end))
            # eliminar intervals en orden descendente sobre la cadena original
            intervals.sort(key=lambda x: x[0], reverse=True)
            for a, b in intervals:
                orig = orig[:a] + orig[b+1:]
    # limpiar espacios redundantes
    return re.sub(r'\s{2,}', ' ', orig).strip()

# ---------------- eliminar líneas según patrones (lineas.txt) ----------------
def line_matches_any(line: str, patterns: list):
    norm = normalize_text(line)
    for p in patterns:
        if normalize_text(p) in norm:
            return True
    return False

# ---------------- agrupar registros por líneas que contienen postal code ----------------
POSTAL_RE = re.compile(r'^\s*(\d{5})(?:\b|,)', flags=re.IGNORECASE)
TRACK_RE = re.compile(r'^[A-Za-z0-9]{8,}$')  # tracking = token alfanumérico >=8 chars, sin espacios

def group_by_postal(lines):
    records = []
    current = None
    for ln in lines:
        m = POSTAL_RE.match(ln)
        if m:
            # empieza nuevo registro
            if current:
                records.append(current)
            current = {'postal_line': ln, 'lines': []}
        else:
            if current:
                current['lines'].append(ln)
            else:
                # líneas antes del primer postal: ignorarlas
                continue
    if current:
        records.append(current)
    return records

# ---------------- parsear cada bloque ----------------
def parse_record(rec):
    # extraer postal
    m = POSTAL_RE.match(rec['postal_line'])
    postal = m.group(1) if m else rec['postal_line'].strip()
    content = rec['lines']
    # buscar tracking desde el final: token alfanum sin espacios y largo >=8
    tracking_idx = None
    for i in range(len(content)-1, -1, -1):
        token = re.sub(r'\s+', '', content[i])
        if TRACK_RE.match(token):
            tracking_idx = i
            break
    if tracking_idx is not None:
        tracking = content[tracking_idx].strip()
        name_idx = tracking_idx - 1 if tracking_idx >= 1 else None
        if name_idx is not None:
            # nombre (lo vamos a eliminar)
            name = content[name_idx].strip()
        else:
            name = ''
        address_lines = content[: max(0, name_idx) ] if name_idx is not None else content[:tracking_idx]
    else:
        tracking = ''
        name = ''
        address_lines = content
    address = ', '.join([a for a in address_lines if a.strip()])
    return {'postal': postal, 'address': address.strip(), 'tracking': tracking.strip()}

# ---------------- script principal ----------------
def main():
    ap = argparse.ArgumentParser(description="Procesa archivo diario: limpia y agrupa por código postal.")
    ap.add_argument('--date', help='Forzar fecha dd-mm (por defecto hoy)')
    ap.add_argument('--debug', action='store_true', help='Mostrar información adicional')
    args = ap.parse_args()

    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = args.date if args.date else datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo: {archivo_hoy}")
        sys.exit(1)

    # archivos de config (en la raíz del repo E)
    baseconf = Path(__file__).parent
    palabras_file = baseconf / "palabras.txt"
    lineas_file = baseconf / "lineas.txt"

    palabras = load_list(palabras_file)
    lineas = load_list(lineas_file)

    raw = archivo_hoy.read_text(encoding='utf-8', errors='ignore')
    raw_lines = [ln.rstrip() for ln in raw.splitlines()]

    # 1) eliminar líneas enteras según lineas.txt (comparación normalizada)
    step1 = []
    removed_line_count = 0
    for ln in raw_lines:
        if ln.strip() == "":
            continue
        if line_matches_any(ln, lineas):
            removed_line_count += 1
            continue
        step1.append(ln)

    # 2) eliminar fragmentos (palabras) dentro de línea, preservando en lo posible original/acento
    step2 = []
    removed_fragment_count = 0
    for ln in step1:
        antes = ln
        nuevo = remove_inline_patterns_preserve_original(ln, palabras)
        # contar diferencias aproximadas (por número de eliminaciones simples)
        if nuevo != antes:
            # heurística: contar palabras eliminadas estimadas
            removed_fragment_count += max(0, (len(antes) - len(nuevo)) // 3)
        if nuevo.strip() != "":
            step2.append(nuevo)
    if args.debug:
        print(f"🔧 Limpieza: líneas eliminadas={removed_line_count}, fragmentos (aprox) eliminados={removed_fragment_count}")

    # 3) agrupar por postal
    records_raw = group_by_postal(step2)
    if args.debug:
        print(f"🔎 Registros detectados: {len(records_raw)}")

    # 4) parsear registros y crear lista final
    parsed = []
    for rec in records_raw:
        parsed.append(parse_record(rec))

    # 5) guardar CSV y TXT en la carpeta paradas
    csv_path = carpeta / f"{fecha}_clean.csv"
    txt_path = carpeta / f"{fecha}_clean.txt"

    # CSV: postal,address,tracking
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["postal","address","tracking"])
        writer.writeheader()
        for r in parsed:
            writer.writerow(r)

    # TXT legible
    with txt_path.open("w", encoding="utf-8") as f:
        for r in parsed:
            f.write(f"{r['postal']}\n{r['address']}\n{r['tracking']}\n\n")

    print(f"✅ Guardado CSV: {csv_path}")
    print(f"✅ Guardado TXT: {txt_path}")
    print(f"ℹ️  Registros procesados: {len(parsed)}")

    if args.debug:
        print("\nPrimeros registros (debug):")
        for i, r in enumerate(parsed[:10], start=1):
            print(f"{i}. postal={r['postal']} | tracking={r['tracking']} | direccion={r['address'][:80]}")

if __name__ == "__main__":
    main()
