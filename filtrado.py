# filtrado.py
from pathlib import Path
from datetime import datetime
import re

def procesar_filtrado():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")

    # Archivo que viene de reglas.py
    input_path = carpeta / f"{fecha}_bloques.txt"
    output_path = carpeta / f"{fecha}_filtrado.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo de entrada para filtrar: {input_path}")
        return

    # Leer líneas del archivo
    lineas = input_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Agrupar bloques por líneas vacías
    bloques = []
    bloque_actual = []
    for ln in lineas:
        if ln.strip() == "":
            if bloque_actual:
                bloques.append(bloque_actual)
                bloque_actual = []
        else:
            bloque_actual.append(ln)
    if bloque_actual:
        bloques.append(bloque_actual)

    # Reducir cada bloque a solo CP + dirección (línea 1 y 2)
    bloques_reducidos = []
    for bloque in bloques:
        if len(bloque) >= 2:
            bloques_reducidos.append("\n".join(bloque[:2]))

    # Guardar resultado
    resultado = "\n\n".join(bloques_reducidos)
    output_path.write_text(resultado, encoding="utf-8")
    print(f"✅ Archivo filtrado generado: {output_path}")
