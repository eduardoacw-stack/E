import subprocess

PAQUETE = "com.cainiao.cs.global.es"
ACTIVIDAD = ".Main"  # cambia según tu app

def abrir_app(paquete, actividad):
    try:
        comando = ["am", "start", "-n", f"{paquete}/{actividad}"]
        subprocess.run(comando, check=True)
        print(f"✅ App {paquete} abierta correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al abrir la app: {e}")

if __name__ == "__main__":
    abrir_app(PAQUETE, ACTIVIDAD)
