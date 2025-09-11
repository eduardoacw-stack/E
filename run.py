#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
limpiar_basico.py
Borra líneas completas (por patrones en lineas.txt) y borra fragmentos (por palabras.txt).
Uso:
  python limpiar_basico.py              # toma paradas/<dd-mm>.txt -> paradas/<dd-mm>_clean.txt
  python limpiar_basico.py --date 09-09 --debug
  python limpiar_basico.py -i /ruta/mi.txt -o /ruta/out.txt
"""

from pathlib import Path
from datetime import datetime
import unicodedata
import re
import argparse
import sys

# ---------------- utilidades ----------------
def normalize_text(s: str) -> str:
    """Normalizar: NFKD, quitar diacríticos y casefold para comparaciones."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.casefold()

def normalize_with_mapping(s: str):
    """
    Normaliza pero devuelve además un mapping de índices:
    norm, mapping donde mapping[i] = índice en s del carácter original que originó norm[i].
    """
    norm_chars = []
    mapping = []
    for i, ch in enumerate(s):
        decomp = unicodedata.normalize("NFKD", ch)
        for d in decomp:
            if unicodedata.category(d) == "Mn":
                continue
            norm_chars.append(d.casefold())
            mapping.append(i)
    return "".join(norm_chars), mapping

def load_list_from(path: Path):
    items = []
    if not path.exists():
        return items
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        items.append(ln)
    return items

# ---------------- matching de líneas ----------------
def line_matches_any(line: str, patterns: list) -> bool:
    """Comprueba (insensible a acentos/mayúsculas) si line contiene alguna pattern."""
    nline = normalize_text(line)
    for p in patterns:
        if normalize_text(p) in nline:
            return True
    return False

# ---------------- eliminación inline preservando original ----------------
def remove_inline_patterns_preserve_original(orig_line: str, patterns: list):
    """
    Elimina todas las ocurrencias de cada patrón (literal) en patterns,
    de forma insensible a acentos y mayúsculas, intentando preservar el resto del texto (y acentos).
    Devuelve (nuevo_string, total_eliminaciones)
    """
    s = orig_line
    total_removed = 0
    # iteramos patrones en el orden dado
    for pat in patterns:
        if not pat:
            continue
        npat = normalize_text(pat)
        if not npat:
            continue
        # repetimos hasta que no haya más coincidencias (por si tras eliminar aparecen nuevas)
        while True:
            norm_line, mapping = normalize_with_mapping(s)
            # buscamos matches en la versión normalizada
            matches = list(re.finditer(re.escape(npat), norm_line))
            if not matches:
                break
            # construir intervalos sobre la cadena original
            intervals = []
            for m in matches:
                start_norm = m.start()
                end_norm = m.end() - 1
                orig_start = mapping[start_norm]
                orig_end = mapping[end_norm]
                intervals.append((orig_start, orig_end))
            # eliminar intervals en orden descendente (para no invalidar índices)
            intervals.sort(key=lambda x: x[0], reverse=True)
            for a, b in intervals:
                # cortar en la cadena original s
                s = s[:a] + s[b+1:]
                total_removed += 1
    # colapsar espacios sobrantes y limpiar
    s = re.sub(r'\s{2,}', ' ', s).strip()
    return s, total_removed

# ---------------- procesamiento principal ----------------
def procesar_archivo(input_path: Path, output_path: Path, lineas_patterns: list, palabras_patterns: list, debug=False):
    raw = input_path.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()

    out_lines = []
    removed_lines = 0
    removed_fragments = 0
    examples_removed_lines = []
    examples_removed_fragments = []

    for idx, ln in enumerate(lines, start=1):
        if not ln.strip():
            # conservar lineas vacías opcionalmente: aquí las ignoramos
            continue

        # 1) si la línea coincide con alguna entrada de lineas.txt -> eliminar línea completa
        if line_matches_any(ln, lineas_patterns):
            removed_lines += 1
            if debug and len(examples_removed_lines) < 20:
                examples_removed_lines.append((idx, ln))
            continue

        # 2) sino, eliminar fragmentos indicados en palabras.txt (dentro de la línea)
        new_ln, removed_count = remove_inline_patterns_preserve_original(ln, palabras_patterns)
        removed_fragments += removed_count
        if debug and removed_count and len(examples_removed_fragments) < 20:
            examples_removed_fragments.append((idx, ln, new_ln, removed_count))

        # 3) si tras limpiar la línea queda algo, lo guardamos
        if new_ln.strip():
            out_lines.append(new_ln)
        # si quedó vacía la línea, la descartamos (no queremos renglones vacíos)
    # escribir resultado
    output_path.write_text("\n".join(out_lines), encoding="utf-8")
    # resumen
    summary = {
        "lines_in": len(lines),
        "lines_out": len(out_lines),
        "removed_lines": removed_lines,
        "removed_fragments": removed_fragments,
        "examples_removed_lines": examples_removed_lines,
        "examples_removed_fragments": examples_removed_fragments
    }
    return summary

# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Borra líneas completas y fragmentos según archivos de configuración.")
    ap.add_argument('--date', help='Forzar fecha dd-mm (por defecto hoy)')
    ap.add_argument('-i','--input', help='Archivo de entrada (por defecto paradas/<dd-mm>.txt)')
    ap.add_argument('-o','--output', help='Archivo de salida (por defecto paradas/<dd-mm>_clean.txt)')
    ap.add_argument('--debug', action='store_true', help='Muestra info de depuración')
    args = ap.parse_args()

    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = args.date if args.date else datetime.now().strftime("%d-%m")
    default_input = carpeta / f"{fecha}.txt"
    default_output = carpeta / f"{fecha}_clean.txt"

    input_path = Path(args.input) if args.input else default_input
    output_path = Path(args.output) if args.output else default_output

    if not input_path.exists():
        print(f"⚠️ Archivo de entrada no encontrado: {input_path}")
        sys.exit(1)

    # archivos de configuración (en la raíz del repo E)
    base = Path(__file__).parent
    lineas_file = base / "lineas.txt"
    palabras_file = base / "palabras.txt"

    lineas_patterns = load_list_from(lineas_file)
    palabras_patterns = load_list_from(palabras_file)

    if args.debug:
        print("📁 Input:", input_path)
        print("📁 Output:", output_path)
        print("📄 lineas.txt patterns:", len(lineas_patterns))
        print("📄 palabras.txt patterns:", len(palabras_patterns))

    summary = procesar_archivo(input_path, output_path, lineas_patterns, palabras_patterns, debug=args.debug)

    print(f"✅ Guardado: {output_path}")
    print(f"ℹ️  Líneas leídas: {summary['lines_in']}  — Líneas resultantes: {summary['lines_out']}")
    print(f"ℹ️  Líneas eliminadas: {summary['removed_lines']}  — Fragmentos eliminados (aprox): {summary['removed_fragments']}")
    if args.debug:
        if summary['examples_removed_lines']:
            print("\nEjemplos líneas eliminadas:")
            for ln_no, ln_text in summary['examples_removed_lines'][:10]:
                print(f"  L{ln_no}: {ln_text}")
        if summary['examples_removed_fragments']:
            print("\nEjemplos fragmentos eliminados (línea antes -> después):")
            for item in summary['examples_removed_fragments'][:10]:
                ln_no, before, after, cnt = item
                print(f"  L{ln_no} (-{cnt}): '{before}'  ->  '{after}'")

if __name__ == "__main__":
    main()









#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import re
import sys

# Detectar código postal
POSTAL_RE = re.compile(r"^(\d{5})")
# Detectar tracking (números largos)
TRACKING_RE = re.compile(r"^\d{10,}$")
# Detectar horarios tipo mon:[...]
HORARIO_RE = re.compile(r"^(mon|tue|wed|thu|fri|sat|sun):", re.IGNORECASE)


def cargar_lista(nombre_archivo: str):
    """Carga lista de palabras desde archivo si existe"""
    f = Path(nombre_archivo)
    if f.exists():
        return [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return []

def extraer_postal_direccion(texto: str):
    """Segunda fase: extraer solo postal y direccion"""
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    salida = []
    i = 0
    while i < len(lineas):
        m = POSTAL_RE.match(lineas[i])
        if m:
            postal = m.group(1)

            # Buscar siguiente línea válida como dirección
            direccion = ""
            j = i + 1
            while j < len(lineas):
                if POSTAL_RE.match(lineas[j]):  # otro postal → no es dirección
                    break
                if TRACKING_RE.match(lineas[j]):  # tracking → saltar
                    j += 1
                    continue
                if HORARIO_RE.match(lineas[j]):  # horario → saltar
                    j += 1
                    continue
                # Si pasa los filtros → dirección válida
                direccion = lineas[j]
                break

            if direccion:
                salida.append(f"{postal} | {direccion}")

            # Avanzar hasta el próximo postal
            i = j
        else:
            i += 1

    return "\n".join(salida)


def main():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo: {archivo_hoy}")
        sys.exit(1)

    # Cargar configuraciones
    borrar_lineas = cargar_lista("lineas.txt")
    borrar_palabras = cargar_lista("palabras.txt")

    # Leer archivo original
    texto = archivo_hoy.read_text(encoding="utf-8", errors="ignore")

    # 1. Limpiar palabras y lineas
    texto_limpio = limpiar_lineas_y_palabras(texto, borrar_lineas, borrar_palabras)

    # 2. Extraer postal + direccion
    resultado = extraer_postal_direccion(texto_limpio)

    # Guardar resultado
    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text(resultado, encoding="utf-8")

    print(f"✅ Procesado y guardado en {archivo_salida}")


if __name__ == "__main__":
    main()
