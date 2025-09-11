#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import re
import sys

POSTAL_RE = re.compile(r"^(\d{5})")

def extraer_postal_direccion(texto: str):
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    salida = []
    i = 0
    while i < len(lineas):
        m = POSTAL_RE.match(lineas[i])
        if m:
            postal = m.group(1)
            direccion = lineas[i+1] if i+1 < len(lineas) else ""
            salida.append(f"{postal} | {direccion}")
            # saltar hasta el próximo postal
            i += 2
            while i < len(lineas) and not POSTAL_RE.match(lineas[i]):
                i += 1
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

    texto = archivo_hoy.read_text(encoding="utf-8", errors="ignore")
    resultado = extraer_postal_direccion(texto)

    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text(resultado, encoding="utf-8")

    print(f"✅ Procesado y guardado en {archivo_salida}")

if __name__ == "__main__":
    main()
