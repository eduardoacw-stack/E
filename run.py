#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py
1. Limpia líneas y palabras (insensible a mayúsculas/acentos)
2. Extrae código postal + dirección
3. Genera un Excel con columnas: address line | postcode usando solo openpyxl
"""

from pathlib import Path
from datetime import datetime
import argparse
import sys
import unicodedata
import re

try:
    from openpyxl import Workbook
except ImportError:
    print("⚠️ Necesitas instalar openpyxl: pkg install python; pip install openpyxl")
    sys.exit(1)


# ---------------- UTILIDADES ----------------
def normalizar(texto: str) -> str:
    """Normaliza texto: minúsculas y sin acentos"""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )


def load_list(path: Path):
    """Carga lista de patrones desde archivo (una palabra/frase por línea)"""
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


# ---------------- LIMPIEZA ----------------
def limpiar_texto(lines, borrar_lineas, borrar_palabras, debug=False):
    out_lines = []
    removed_lines = 0
    removed_words = 0

    for idx, ln in enumerate(lines, start=1):
        if not ln.strip():
            continue

        norm_ln = normalizar(ln)

        # borrar línea completa
        if any(normalizar(pat) in norm_ln for pat in borrar_lineas):
            removed_lines += 1
            if debug:
                print(f"[BORRAR LÍNEA] {idx}: {ln}")
            continue

        # borrar fragmentos dentro de la línea
        original_ln = ln
        for pat in borrar_palabras:
            if normalizar(pat) in norm_ln:
                regex = re.compile(re.escape(pat), re.IGNORECASE)
                ln = regex.sub("", ln)
                removed_words += 1

        if debug and ln != original_ln:
            print(f"[BORRAR PALABRA] {idx}: '{original_ln}' -> '{ln}'")

        if ln.strip():
            out_lines.append(ln)

    return out_lines, removed_lines, removed_words


# ---------------- EXTRAER BLOQUES ----------------
def extraer_codigos_y_direcciones(lines):
    resultado = []
    i = 0
    while i < len(lines) - 1:
        linea = lines[i]
        m = re.match(r"^(\d{5}),", linea.strip())
        if m:
            cp = m.group(1)
            direccion = lines[i + 1].strip() if i + 1 < len(lines) else ""
            resultado.append((direccion, cp))
            i += 2
        else:
            i += 1
    return resultado


# ---------------- GENERAR EXCEL ----------------
def generar_excel(resultado, output_path: Path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Direcciones"
    # encabezado
    ws.append(["address line", "postcode"])
    # filas
    for direccion, cp in resultado:
        ws.append([direccion, cp])
    wb.save(output_path.with_suffix(".xlsx"))
    return output_path.with_suffix(".xlsx")


# ---------------- MAIN ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', help="Fecha dd-mm (por defecto hoy)")
    ap.add_argument('-i', '--input', help="Archivo de entrada")
    ap.add_argument('--debug', action='store_true')
    args = ap.parse_args()

    # carpeta y archivo
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = args.date if args.date else datetime.now().strftime("%d-%m")
    input_path = Path(args.input) if args.input else carpeta / f"{fecha}.txt"
    clean_txt_path = carpeta / f"{fecha}_clean.txt"  # DEFINIDA ANTES DE USARLA

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo: {input_path}")
        sys.exit(1)

    # cargar listas de palabras y líneas a borrar
    base = Path(__file__).parent
    borrar_lineas = load_list(base / "lineas.txt")
    borrar_palabras = load_list(base / "palabras.txt")

    # leer archivo
    raw_lines = input_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # 1️⃣ Limpieza
    clean_lines, removed_lines, removed_words = limpiar_texto(
        raw_lines, borrar_lineas, borrar_palabras, debug=args.debug
    )

    # 2️⃣ Extraer CP + dirección
    resultado = extraer_codigos_y_direcciones(clean_lines)
    clean_txt_path.write_text("\n".join(f"{cp} | {direccion}" for direccion, cp in resultado), encoding="utf-8")
    print(f"✅ TXT limpio guardado: {clean_txt_path}")
    print(f"ℹ️ Líneas eliminadas: {removed_lines} — Palabras eliminadas: {removed_words}")
    print(f"ℹ️ Bloques extraídos: {len(resultado)}")

    # 3️⃣ Generar Excel
    excel_path = generar_excel(resultado, clean_txt_path)
    print(f"✅ Excel generado: {excel_path}")


if __name__ == "__main__":
    main()
