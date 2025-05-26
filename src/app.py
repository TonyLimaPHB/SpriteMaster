# src/app.py

from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QWidget, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

print("🧠 [INFO] Carregando módulo: App...")

class SpritesheetApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SpriteMaster 🎨🐍")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.CustomizeWindowHint)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")

        # Atributos principais
        self.image_path = None
        self.pixmap = None

        # Componentes
        self.init_ui()

    def init_ui(self):
        from src.ui.canvas import Canvas
        from src.ui.sidebar import Sidebar

        # Primeiro criamos a Sidebar sem referência ao Canvas
        self.sidebar = Sidebar(canvas=None)

        # Agora criamos o Canvas com referência à Sidebar
        self.canvas = Canvas(sidebar=self.sidebar, parent=self)

        # Atualizamos a Sidebar com a referência ao Canvas
        self.sidebar.canvas = self.canvas

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas, stretch=3)
        main_layout.addWidget(self.sidebar, stretch=0)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("background-color: #1e1e1e; color: white;")

        file_menu = menu_bar.addMenu("📁 Arquivo")

        open_action = file_menu.addAction("📂 Abrir Imagem")
        open_action.triggered.connect(self.open_image_dialog)

        save_action = file_menu.addAction("💾 Salvar Spritesheet")
        save_action.triggered.connect(self.save_spritesheet)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("❌ Sair")
        exit_action.triggered.connect(self.close)

    def open_image_dialog(self):
        print("📂 [AÇÃO] Abrindo diálogo para selecionar imagem...")
        image_dir = os.path.join(os.getcwd(), "assets", "images")
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Spritesheet",
            image_dir,
            "Imagens (*.png *.jpg *.bmp)"
        )
        if file_name:
            self.load_image(file_name)

    def load_image(self, path):
        print(f"🖼️ [INFO] Carregando imagem: {path}")
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.show_error("Erro ao carregar imagem.")
            return
        self.image_path = path
        self.pixmap = pixmap
        self.canvas.set_background(pixmap)
        self.setWindowTitle(f"Editor de Spritesheets - {os.path.basename(path)} 🎮🖼️")
        self.canvas.clear_selections()

    def save_spritesheet(self):
        selected_rects = self.canvas.selected_rects
        if not selected_rects:
            self.show_info("Nenhum frame foi selecionado.")
            return

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Spritesheet",
            output_dir,
            "PNG (*.png)"
        )

        if file_path:
            try:
                from src.logic.exporter import SpriteSheetExporter
                exporter = SpriteSheetExporter(self.image_path)

                # Pega todas as configs salvas nos frames
                bg_removal_config = self.canvas.get_bg_removal_config()
                alignment_configs = getattr(self.canvas, "_individual_align_configs", None)

                configs = []
                for i, rect in enumerate(selected_rects):
                    config = {
                        "remove_background": bg_removal_config["remove_background"],
                        "bg_color": bg_removal_config["bg_color"]
                    }
                    if alignment_configs and i < len(alignment_configs):
                        config["align_config"] = alignment_configs[i]
                    else:
                        config["align_config"] = self.canvas.get_alignment_config()
                    configs.append(config)

                for rect, config in zip(selected_rects, configs):
                    exporter.add_frame(rect, config)

                success = exporter.export(file_path, layout="horizontal")
                if success:
                    print(f"✅ Spritesheet salva em: {file_path}")
                    self.show_info(f"Spritesheet salva com sucesso:\n{file_path}")
                else:
                    self.show_error("Falha ao exportar spritesheet.")
            except Exception as e:
                error_msg = f"❌ Erro ao exportar spritesheet:\n{str(e)}"
                print(error_msg)
                self.show_error(error_msg)

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("❌ Erro")
        msg.setInformativeText(message)
        msg.setWindowTitle("Erro")
        msg.exec()

    def show_info(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("💡 Informação")
        msg.exec()
