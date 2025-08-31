import subprocess

# Nombre del paquete de la app que quieres abrir
PAQUETE = " com.cainiao.cs.global.es"

def abrir_app(paquete):
    try:
        comando = ["adb", "shell", "monkey", "-p", paquete, "-c", "android.intent.category.LAUNCHER", "1"]
        subprocess.run(comando, check=True)
        print(f"✅ App {paquete} iniciada correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al abrir la app: {e}")

if __name__ == "__main__":
    abrir_app(PAQUETE)

