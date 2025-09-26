# reglas.py
from pathlib import Path
from datetime import datetime

def cargar_reglas(archivo: Path):
    reglas = []
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            if "=>" in linea:
                origen, destino = linea.split("=>", 1)
                reglas.append((origen.strip(), destino.strip()))
    return reglas


def aplicar_reglas(texto: str, reglas):
    for origen, destino in reglas:
        texto = texto.replace(origen, destino)
    return texto


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

    # Aplicar reglas
    texto_modificado = aplicar_reglas(texto, reglas)

    # Guardar resultado
    output_path.write_text(texto_modificado, encoding="utf-8")
    print(f"✅ Reglas aplicadas. Archivo generado en: {output_path}")
