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

        if re.match(r"^\d{5},", linea):  # Detectar código postal
            if bloque_actual:
                bloques.append(bloque_actual)
                bloque_actual = []
        bloque_actual.append(linea)

    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques


def extraer_codigos(bloques):
    """
    Devuelve una lista de códigos postales únicos en orden de aparición.
    """
    codigos = []
    for bloque in bloques:
        primera_linea = bloque[0]
        m = re.match(r"^(\d{5}),", primera_linea)
        if m:
            cp = m.group(1)
            if cp not in codigos:
                codigos.append(cp)
    return codigos


def procesar_archivo():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")
    input_path = carpeta / f"{fecha}.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo: {input_path}")
        return

    texto = input_path.read_text(encoding="utf-8", errors="ignore")
    bloques = separar_bloques(texto)
    print(f"✅ Se detectaron {len(bloques)} bloques.")

    # 1️⃣ Obtener códigos postales únicos
    codigos = extraer_codigos(bloques)
    print("\n📌 Códigos postales detectados:")
    for i, cp in enumerate(codigos, 1):
        print(f"  {i}. {cp}")

    # 2️⃣ Preguntar al usuario
    seleccion = input("\n👉 Ingresa los códigos postales que quieres mantener (ej: 46118,46180): ")
    seleccion = [s.strip() for s in seleccion.split(",") if s.strip()]

    # 3️⃣ Filtrar bloques
    bloques_filtrados = []
    for bloque in bloques:
        primera_linea = bloque[0]
        m = re.match(r"^(\d{5}),", primera_linea)
        if m and m.group(1) in seleccion:
            bloques_filtrados.append(bloque)

    print(f"\n✅ Se mantendrán {len(bloques_filtrados)} bloques tras el filtrado.")

    # 4️⃣ Guardar resultado en archivo
    output_path = carpeta / f"{fecha}_bloques.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for i, b in enumerate(bloques_filtrados, 1):
            f.write(f"=== Bloque {i} ===\n")
            for l in b:
                f.write(l + "\n")
            f.write("\n")

    print(f"📂 Archivo generado en: {output_path}")
