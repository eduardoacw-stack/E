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


def cargar_lista_reemplazos(archivo: Path):
    """
    Carga archivo de reemplazos (formato: origen => destino).
    """
    reglas = []
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            if "=>" in linea:
                origen, destino = linea.split("=>", 1)
                reglas.append((origen.strip(), destino.strip()))
    return reglas


def aplicar_por_palabra(texto: str, reglas):
    """
    Aplica reemplazos palabra por palabra.
    """
    tokens = re.split(r"(\W+)", texto)  # palabras + separadores
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


def aplicar_por_frase(texto: str, reglas):
    """
    Aplica reemplazos de frases completas, insensible a acentos y mayúsculas.
    """
    for origen, destino in reglas:
        # Regex insensible a acentos/mayúsculas
        patron = re.compile(re.escape(normalizar(origen)), re.IGNORECASE)

        # Buscar en versión normalizada
        def reemplazo(match):
            return destino

        texto = re.sub(patron, reemplazo, normalizar(texto))
    return texto


def procesar_reglas():
    carpeta = Path.home() / "storage" / "shared" / "paradas"
    fecha = datetime.now().strftime("%d-%m")

    # Archivos
    input_path = carpeta / f"{fecha}_bloques.txt"
    output_path = carpeta / f"{fecha}_reglas.txt"

    base = Path(__file__).parent
    correcciones_path = base / "correcciones.txt"
    reglas_path = base / "reglas.txt"

    if not input_path.exists():
        print(f"⚠️ No se encontró archivo de entrada: {input_path}")
        return

    texto = input_path.read_text(encoding="utf-8", errors="ignore")

    # 1️⃣ Correcciones automáticas (palabra por palabra)
    correcciones = cargar_lista_reemplazos(correcciones_path)
    if correcciones:
        texto = aplicar_por_palabra(texto, correcciones)

    # 2️⃣ Reglas personalizadas (frases completas)
    reglas = cargar_lista_reemplazos(reglas_path)
    if reglas:
        texto = aplicar_por_frase(texto, reglas)
    else:
        print("⚠️ No se encontraron reglas en reglas.txt")

    # Guardar resultado
    output_path.write_text(texto, encoding="utf-8")
    print(f"✅ Reglas aplicadas. Archivo generado en: {output_path}")
