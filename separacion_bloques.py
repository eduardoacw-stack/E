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
            # Si ya hay un bloque en construcción, lo guardamos
            if bloque_actual:
                bloques.append(bloque_actual)
                bloque_actual = []
        
        bloque_actual.append(linea)

    # Guardar último bloque si quedó algo
    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques


if __name__ == "__main__":
    # 📂 Carpeta donde guardas tus archivos
    carpeta = Path.home() / "storage" / "shared" / "paradas"

    # Nombre del archivo de entrada: DD-MM.txt (ejemplo: 26-09.txt)
    fecha = datetime.now().strftime("%d-%m")
    input_path = carpeta / f"{fecha}.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo: {input_path}")
        exit(1)

    # Leer contenido del archivo
    texto = input_path.read_text(encoding="utf-8", errors="ignore")

    # Separar bloques
    bloques = separar_bloques(texto)
    print(f"✅ Se detectaron {len(bloques)} bloques.")

    # Crear archivo de salida en la MISMA carpeta
    output_path = carpeta / f"{fecha}_bloques.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, b in enumerate(bloques, 1):
            f.write(f"=== Bloque {i} ===\n")
            for l in b:
                f.write(l + "\n")
            f.write("\n")

    print(f"📂 Archivo generado: {output_path}")
