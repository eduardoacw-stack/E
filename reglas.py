# reglas.py
import unicodedata
import re
from pathlib import Path
from datetime import datetime


def normalizar(texto: str) -> str:
    """Convierte a minúsculas y elimina acentos"""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )


def cargar_reglas(archivo: Path):
    reglas = []
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            if "=>" in linea:
                origen, destino = linea.split("=>", 1)
                reglas.append((origen.strip(), destino.strip()))
    return reglas


def aplicar_reglas(texto: str, reglas):
    # Dividir en palabras y separadores (espacios, comas, puntos, saltos de línea, etc.)
    tokens = re.split(r"(\W+)", texto)  

    reglas_norm = [(normalizar(o), d) for o, d in reglas]

    resultado = []
    for token in tokens:
        token_norm = normalizar(token)
        reemplazado = False

        for origen_norm, destino in reglas_norm:
            if token_norm == origen_norm:
                resultado.append(destino)
                reemplazado = True
                break

        if not reemplazado:
            resultado.append(token)

    return "".join(resultado)


def procesar_reglas():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")

    # Archivo de entrada: lo que generó separacion_bloques.py
    input_path = carpeta / f"{fecha}_bloques.txt"
    output_path = carpeta / f"{fecha}_reglas.txt"
    reglas_path = Path(__file__).parent / "reglas.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo de entrada: {input_path}")
        return

    # Cargar texto y reglas
    texto = input_path.read_text(encoding="utf-8", errors="ignore")
    reglas = cargar_reglas(reglas_path)

    if not reglas:
        print("⚠️ No se encontraron reglas en reglas.txt")
        return

    # Aplicar reglas palabra por palabra
    texto_modificado = aplicar_reglas(texto, reglas)

    # Guardar resultado
    output_path.write_text(texto_modificado, encoding="utf-8")
    print(f"✅ Reglas aplicadas. Archivo generado en: {output_path}")
