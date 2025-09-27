# data.py
import separacion_bloques
import reglas

def main():
    print("🚀 Iniciando procesamiento...")

    # 1️⃣ Ejecutar separación de bloques
    separacion_bloques.procesar_archivo()

    # 2️⃣ Ejecutar aplicación de reglas
    reglas.procesar_reglas()

    print("✅ Proceso finalizado.")

if __name__ == "__main__":
    main()
