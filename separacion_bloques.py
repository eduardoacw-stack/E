# separacion_bloques.py
import re
from pathlib import Path
from datetime import datetime

def separar_bloques(texto):
    """
    Recibe texto completo como string.
    Devuelve lista de bloques, cada bloque es lista de líneas.
    """
    bloques = []
    bloque_actual = []

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        # Detectar código postal (ejemplo: 46119,)
        if re.match(r"^\d{5},", linea):
            if bloque_actual:
                bloques.append(bloque_actual)
                bloque_actual = []
        bloque_actual.append(linea)

    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques


def procesar_archivo():
    """
    Lee el archivo del día (DD-MM.txt) en la carpeta paradas,
    separa en bloques y genera un archivo DD-MM_bloques.txt.
    """
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")
    input_path = carpeta / f"{fecha}.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo: {input_path}")
        return

    texto = input_path.read_text(encoding="utf-8", errors="ignore")
    bloques = separar_bloques(texto)
    print(f"✅ Se detectaron {len(bloques)} bloques.")

    output_path = carpeta / f"{fecha}_bloques.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for i, b in enumerate(bloques, 1):
            f.write(f"=== Bloque {i} ===\n")
            for l in b:
                f.write(l + "\n")
            f.write("\n")

    print(f"📂 Archivo generado en: {output_path}")
