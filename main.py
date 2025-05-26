import sys
import traceback

print("🔧 [INFO] Iniciando o editor de spritesheets...")

try:
    print("🎨 Carregando interface gráfica...")
    from PySide6.QtWidgets import QApplication

    print("🧠 Importando módulos principais...")
    from src.app import SpritesheetApp

    print("⚙️ Iniciando aplicação...")
    app = QApplication(sys.argv)

    print("🖥️ Abrindo janela principal...")
    window = SpritesheetApp()
    window.show()

    print("▶️ Executando loop da aplicação...\n")
    sys.exit(app.exec())

except Exception as e:
    print(f"❌ [ERRO CRÍTICO] {str(e)}")
    print("🧾 Detalhes do erro:\n")
    traceback.print_exc()
    sys.exit(1)
