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


def limpiar_lineas_y_palabras(texto: str, borrar_lineas: list, borrar_palabras: list) -> str:
    """Primera fase: limpiar texto de lineas y palabras no deseadas"""
    lineas = texto.splitlines()
    resultado = []

    for linea in lineas:
        # Si contiene alguna palabra de lineas.txt -> descartar
        if any(palabra in linea for palabra in borrar_lineas):
            continue

        # Reemplazar palabras de palabras.txt dentro de la linea
        for palabra in borrar_palabras:
            linea = linea.replace(palabra, "")

        resultado.append(linea)

    return "\n".join(resultado)


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
