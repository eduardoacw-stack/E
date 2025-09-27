# filtrado.py
from pathlib import Path
from datetime import datetime
import re
import unicodedata

try:
    from openpyxl import Workbook
except ImportError:
    print("⚠️ Necesitas instalar openpyxl: pip install openpyxl")
    exit(1)

def cargar_palabras(path_palabras):
    """Carga palabras desde un archivo, una palabra por línea."""
    if not path_palabras.exists():
        return []
    return [ln.strip() for ln in path_palabras.read_text(encoding="utf-8").splitlines() if ln.strip()]

def borrar_palabras(texto, palabras):
    """Elimina todas las ocurrencias de las palabras indicadas, insensible a mayúsculas y acentos."""
    resultado = []
    for linea in texto.splitlines():
        nueva_linea = linea
        for palabra in palabras:
            patron = re.compile(re.escape(palabra), re.IGNORECASE)
            nueva_linea = patron.sub('', nueva_linea)
        resultado.append(nueva_linea.strip())
    return "\n".join(resultado)

def generar_excel(bloques, output_path: Path):
    """Genera un Excel con la primera línea en la columna A y la segunda en la columna B."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Direcciones"
    ws.append(["Address Line", "Postcode"])
    for bloque in bloques:
        lineas = [ln for ln in bloque.splitlines() if ln.strip()]
        if len(lineas) >= 2:
            ws.append([lineas[1], lineas[0]])
    wb.save(output_path.with_suffix(".xlsx"))
    return output_path.with_suffix(".xlsx")

def procesar_filtrado():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")

    # Archivo que viene de reglas.py
    input_path = carpeta / f"{fecha}_reglas.txt"
    output_txt = carpeta / f"{fecha}_filtrado.txt"
    output_xlsx = carpeta / f"{fecha}_filtrado.xlsx"

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

    # Reducir cada bloque a solo CP + dirección
    bloques_reducidos = []
    for bloque in bloques:
        if len(bloque) >= 2:
            bloques_reducidos.append("\n".join(bloque[:2]))

    # Unir bloques a texto
    texto = "\n\n".join(bloques_reducidos)

    # Cargar lista de palabras a borrar
    palabras_path = Path(__file__).parent / "palabras.txt"
    palabras_a_borrar = cargar_palabras(palabras_path)

    # Borrar las palabras indicadas
    if palabras_a_borrar:
        texto = borrar_palabras(texto, palabras_a_borrar)

    # Guardar archivo TXT final
    output_txt.write_text(texto, encoding="utf-8")
    print(f"✅ Archivo filtrado TXT generado: {output_txt}")

    # Guardar Excel
    bloques_finales = [b for b in texto.split("\n\n") if b.strip()]
    excel_path = generar_excel(bloques_finales, output_xlsx)
    print(f"✅ Archivo Excel generado: {excel_path}")
