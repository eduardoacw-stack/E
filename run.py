#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import re
import sys

def procesar_bloques(texto: str):
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    salida = []
    i = 0

    while i < len(lineas):
        bloque = lineas[i:i+4]  # tomamos bloques de 4
        if len(bloque) < 4:
            break  # si el bloque está incompleto, lo ignoramos

        # 1️⃣ primera línea → solo código postal
        m = re.match(r"(\d{5})", bloque[0])
        if m:
            salida.append(m.group(1))
        else:
            salida.append(bloque[0])  # si no hay match, dejamos tal cual

        # 2️⃣ segunda línea → dirección completa
        salida.append(bloque[1])

        # 3️⃣ tercera línea → eliminar (nombre) → no se agrega nada

        # 4️⃣ cuarta línea → código de paquete
        salida.append(bloque[3])

        i += 4  # saltamos al siguiente bloque

    return "\n".join(salida)

def main():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")
    archivo_hoy = carpeta / f"{fecha}.txt"

    if not archivo_hoy.exists():
        print(f"⚠️ No se encontró archivo: {archivo_hoy}")
        sys.exit(1)

    texto = archivo_hoy.read_text(encoding="utf-8", errors="ignore")
    resultado = procesar_bloques(texto)

    archivo_salida = carpeta / f"{fecha}_clean.txt"
    archivo_salida.write_text(resultado, encoding="utf-8")

    print(f"✅ Procesado y guardado en {archivo_salida}")

if __name__ == "__main__":
    main()
