# filtrado.py
from pathlib import Path
from datetime import datetime
import re

def procesar_filtrado():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")

    # Archivo que viene de reglas.py
    input_path = carpeta / f"{fecha}_reglas.txt"
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

    # Unir bloques reducidos a texto
    texto = "\n\n".join(bloques_reducidos)

    # 1️⃣ Cargar palabras a borrar
    palabras_path = Path(__file__).parent / "palabras.txt"
    palabras_a_borrar = cargar_palabras(palabras_path)

    # 2️⃣ Borrar las palabras indicadas
    if palabras_a_borrar:
        texto = borrar_palabras(texto, palabras_a_borrar)

    # Cargar lista de palabras a borrar
def cargar_palabras(path_palabras):
    """
    Carga palabras desde un archivo, una palabra por línea.
    """
    if not path_palabras.exists():
        return []
    return [ln.strip() for ln in path_palabras.read_text(encoding="utf-8").splitlines() if ln.strip()]

# Función para borrar palabras de cada línea
def borrar_palabras(texto, palabras):
    """
    Elimina todas las ocurrencias de las palabras indicadas, insensible a mayúsculas y acentos.
    """
    import unicodedata
    import re

    def normalizar(t):
        return ''.join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn')

    resultado = []
    for linea in texto.splitlines():
        nueva_linea = linea
        for palabra in palabras:
            # Reemplazo insensible a mayúsculas/acentos
            patron = re.compile(re.escape(palabra), re.IGNORECASE)
            nueva_linea = patron.sub('', nueva_linea)
        resultado.append(nueva_linea.strip())
    return "\n".join(resultado)

    # Guardar resultado
    resultado = "\n\n".join(bloques_reducidos)
    output_path.write_text(resultado, encoding="utf-8")
    print(f"✅ Archivo filtrado generado: {output_path}")
