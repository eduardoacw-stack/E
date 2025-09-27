# separacion_bloques.py
import re
from pathlib import Path
from datetime import datetime

def limpiar_codigos_postales(texto: str) -> str:
    """
    Deja solo el número de los códigos postales (ej: '46119, Naquera' -> '46119').
    """
    lineas = texto.splitlines()
    nuevas = []
    for ln in lineas:
        m = re.match(r"^(\d{5}),", ln.strip())
        if m:
            nuevas.append(m.group(1))  # solo el número
        else:
            nuevas.append(ln)
    return "\n".join(nuevas)

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
    output_path = carpeta / f"{fecha}_bloques.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo de entrada: {input_path}")
        return

    # Leer líneas del archivo original
    lineas = input_path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # 1️⃣ Limpiar códigos postales
    lineas = limpiar_codigos_postales(lineas)

    # 2️⃣ Detectar códigos postales únicos
    codigos = sorted(set([ln.strip() for ln in lineas if re.match(r"^\d{5}$", ln.strip())]))

    if not codigos:
        print("⚠️ No se detectaron códigos postales.")
        return

    print("\n📍 Códigos postales detectados:")
    for i, cp in enumerate(codigos, start=1):
        print(f"{i}. {cp}")

    seleccion = input("\n👉 Ingrese los números de los códigos a conservar (ejemplo: 1,3): ").strip()
    if not seleccion:
        print("⚠️ No seleccionaste ningún código postal. Se guardará vacío.")
        seleccionados = []
    else:
        indices = [int(x.strip()) for x in seleccion.split(",") if x.strip().isdigit()]
        seleccionados = [codigos[i - 1] for i in indices if 0 < i <= len(codigos)]

    # 3️⃣ Filtrar bloques por CP seleccionado
    bloques = []
    i = 0
    while i < len(lineas):
        ln = lineas[i].strip()
        if re.match(r"^\d{5}$", ln):  # línea con solo el CP
            cp = ln
            bloque = [cp]
            i += 1
            while i < len(lineas) and not re.match(r"^\d{5}$", lineas[i].strip()):
                bloque.append(lineas[i])
                i += 1
            if cp in seleccionados:
                bloques.append("\n".join(bloque))
        else:
            i += 1

    # Guardar archivo final
    resultado = "\n\n".join(bloques)
    output_path.write_text(resultado, encoding="utf-8")
    print(f"\n✅ Archivo generado: {output_path}")
