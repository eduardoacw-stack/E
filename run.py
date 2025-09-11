#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
procesar_ruta.py
1. Borra líneas completas y palabras/frases no deseadas.
2. Extrae solo código postal + dirección.
Coincidencias insensibles a mayúsculas/acentos.
"""

from pathlib import Path
from datetime import datetime
import argparse
import sys
import unicodedata
import re
import pandas as pd


# ---------------- UTILIDADES ----------------

def normalizar(texto: str) -> str:
    """Normaliza texto: minúsculas + sin acentos"""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )


def load_list(path: Path):
    """Carga lista de patrones desde archivo (1 por línea)"""
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


# ---------------- ETAPA 1: LIMPIEZA ----------------

def limpiar_texto(lines, borrar_lineas, borrar_palabras, debug=False):
    out_lines = []
    removed_lines = 0
    removed_words = 0

    for idx, ln in enumerate(lines, start=1):
        if not ln.strip():
            continue

        norm_ln = normalizar(ln)

        # 1) Borrar líneas enteras si coinciden
        if any(normalizar(pat) in norm_ln for pat in borrar_lineas):
            removed_lines += 1
            if debug:
                print(f"[BORRAR LÍNEA] {idx}: {ln}")
            continue

        # 2) Borrar palabras/frases dentro de la línea
        original_ln = ln
        for pat in borrar_palabras:
            if normalizar(pat) in norm_ln:
                # regex insensible a acentos y mayúsculas
                regex = re.compile(re.escape(pat), re.IGNORECASE)
                ln = regex.sub("", ln)
                removed_words += 1

        if debug and ln != original_ln:
            print(f"[BORRAR PALABRA] {idx}: '{original_ln}' -> '{ln}'")

        if ln.strip():
            out_lines.append(ln)

    return out_lines, removed_lines, removed_words


# ---------------- ETAPA 2: EXTRAER BLOQUES ----------------

def extraer_codigos_y_direcciones(lines):
    resultado = []
    i = 0
    while i < len(lines) - 1:
        linea = lines[i]
        m = re.match(r"^(\d{5}),", linea.strip())
        if m:
            cp = m.group(1)
            direccion = lines[i + 1].strip() if i + 1 < len(lines) else ""
            resultado.append(f"{cp} | {direccion}")
            i += 2
        else:
            i += 1
    return resultado

# ---------------- GENERAR EXCEL ----------------
def generar_excel(resultado, output_path: Path):
    data = []
    for line in resultado:
        if "|" not in line:
            continue
        cp, direccion = line.split("|", 1)
        data.append({"address line": direccion.strip(), "postcode": cp.strip()})

    df = pd.DataFrame(data, columns=["address line", "postcode"])
    df.to_excel(output_path.with_suffix(".xlsx"), index=False)
    return output_path.with_suffix(".xlsx")


# ---------------- MAIN ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', help="Fecha dd-mm (por defecto hoy)")
    ap.add_argument('-i', '--input', help="Archivo de entrada")
    ap.add_argument('-o', '--output', help="Archivo de salida")
    ap.add_argument('--debug', action='store_true')
    args = ap.parse_args()

    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = args.date if args.date else datetime.now().strftime("%d-%m")

    input_path = Path(args.input) if args.input else carpeta / f"{fecha}.txt"
    output_path = Path(args.output) if args.output else carpeta / f"{fecha}_clean.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo: {input_path}")
        sys.exit(1)

    base = Path(__file__).parent
    borrar_lineas = load_list(base / "lineas.txt")
    borrar_palabras = load_list(base / "palabras.txt")

    raw_lines = input_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Etapa 1: limpieza
    clean_lines, removed_lines, removed_words = limpiar_texto(
        raw_lines, borrar_lineas, borrar_palabras, debug=args.debug
    )

    # Etapa 2: extraer cp + dirección
    resultado = extraer_codigos_y_direcciones(clean_lines)

    # Guardar
    output_path.write_text("\n".join(resultado), encoding="utf-8")

    print(f"✅ Guardado: {output_path}")
    print(f"ℹ️ Líneas eliminadas: {removed_lines} — Palabras eliminadas: {removed_words}")
    print(f"ℹ️ Bloques extraídos: {len(resultado)}")

# 3️⃣ Generar Excel
    excel_path = generar_excel(resultado, clean_txt_path)
    print(f"✅ Excel generado: {excel_path}")

if __name__ == "__main__":
    main()
