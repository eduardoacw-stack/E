import re
from pathlib import Path
from datetime import datetime


def limpiar_codigos_postales(lineas):
    """
    Convierte líneas que empiezan con CP a solo el número (ej: '46119, Naquera' -> '46119').
    """
    nuevas = []
    for ln in lineas:
        m = re.match(r"^(\d{5}),", ln.strip())
        if m:
            nuevas.append(m.group(1))
        else:
            nuevas.append(ln)
    return nuevas


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

    # 4️⃣ Ejecutar filtrado.py
    try:
        import filtrado  # el archivo filtrado.py debe estar en la misma carpeta
        filtrado.procesar_filtrado()  # esta función se encargará del siguiente paso
        print("✅ filtrado.py ejecutado correctamente.")
    except ImportError:
        print("⚠️ No se encontró filtrado.py o no tiene procesar_filtrado()")

