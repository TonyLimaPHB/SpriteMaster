# src/ui/sidebar.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton,
    QCheckBox, QColorDialog, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

print("🎛️ [INFO] Carregando módulo: Sidebar...")

class Sidebar(QWidget):
    def __init__(self, canvas=None, parent=None):
        super().__init__(parent)

        self.canvas = canvas  # Referência ao Canvas
        self.init_ui()

    def init_ui(self):
        from .alignment_dialog import AlignmentDialog

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        # Estilo do sidebar
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #1e1e1e; border-left: 1px solid #333; padding: 10px;")

        # Título
        title = QLabel("🔧 Configurações")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(title)

        # Campo de número de frames
        frame_layout = QHBoxLayout()
        self.frame_label = QLabel("🔢 Frames desejados:")
        self.frame_label.setStyleSheet("color: white;")
        self.spin_frames = QSpinBox()
        self.spin_frames.setMinimum(1)
        self.spin_frames.setMaximum(100)
        self.spin_frames.setValue(4)
        self.spin_frames.valueChanged.connect(self.on_frame_count_changed)
        self.apply_style(self.spin_frames)
        frame_layout.addWidget(self.frame_label)
        frame_layout.addWidget(self.spin_frames)
        layout.addLayout(frame_layout)

        # Status
        self.status_label = QLabel("✅ Frames selecionados: 0/4")
        self.status_label.setStyleSheet("color: #aaa;")
        layout.addWidget(self.status_label)

        # Remover fundo
        remove_bg_layout = QHBoxLayout()
        self.remove_bg_checkbox = QCheckBox("🧹 Remover Fundo")
        self.remove_bg_checkbox.setStyleSheet("color: white;")
        self.remove_bg_checkbox.toggled.connect(self.toggle_remove_bg)
        self.bg_color_button = QPushButton("🎨")
        self.bg_color_button.setFixedSize(30, 25)
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        self.bg_color_button.setStyleSheet("background-color: green;")
        self.bg_color = QColor(Qt.GlobalColor.green)
        remove_bg_layout.addWidget(self.remove_bg_checkbox)
        remove_bg_layout.addWidget(self.bg_color_button)
        layout.addLayout(remove_bg_layout)

        # Botão alinhamento
        align_button = QPushButton("🧱 Ajustar Alinhamento")
        align_button.clicked.connect(self.open_alignment_dialog)
        self.apply_style(align_button)
        layout.addWidget(align_button)

        # Botão limpar seleção
        clear_button = QPushButton("🗑 Limpar Seleção")
        clear_button.clicked.connect(self.clear_selections)
        self.apply_style(clear_button)
        layout.addWidget(clear_button)

        layout.addStretch()

    def apply_style(self, widget):
        widget.setStyleSheet("""
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555;
            padding: 5px;
        """)

    def toggle_remove_bg(self, checked):
        print(f"🧼 [AÇÃO] Remover fundo {'ativado' if checked else 'desativado'}")
        if self.canvas:
            self.canvas.remove_background = checked
            self.canvas.update()

    def choose_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self, "Escolha a cor do fundo")
        if color.isValid():
            self.bg_color = color
            self.bg_color_button.setStyleSheet(f"background-color: {color.name()};")
            if self.canvas:
                self.canvas.bg_color = color
                self.canvas.update()
            print(f"🌈 Cor do fundo definida: {color.name()}")

    def update_bg_button_color(self, color):
        self.bg_color = color
        self.bg_color_button.setStyleSheet(f"background-color: {color.name()};")
        if self.canvas:
            self.canvas.bg_color = color
            self.canvas.update()
        print(f"🎨 Cor atualizada via clique na imagem: {color.name()}")

    def on_frame_count_changed(self, value):
        print(f"🔢 Número de frames alterado para: {value}")
        if self.canvas:
            self.canvas.set_max_frames(value)
        self.update_status()

    def update_status(self):
        total = len(self.canvas.selected_rects) if self.canvas else 0
        max_frames = self.spin_frames.value()
        self.status_label.setText(f"✅ Frames selecionados: {total}/{max_frames}")

    def clear_selections(self):
        print("🗑️ Limpando seleções via botão...")
        if self.canvas:
            self.canvas.clear_selections()
        self.update_status()

    def open_alignment_dialog(self):
        from .alignment_dialog import AlignmentDialog
        if not self.canvas or not self.canvas.selected_rects:
            self.canvas.show_info("Nenhum frame foi selecionado.")
            return

        dialog = AlignmentDialog(self.canvas)
        if dialog.exec():
            all_configs = dialog.get_all_configs()
            for i, config in enumerate(all_configs):
                if i < len(self.canvas.selected_rects):
                    self.canvas.selected_rects[i] = self.canvas.selected_rects[i]
                    # Guarda a configuração no Canvas ou em outro lugar se necessário
            self.canvas.update()
            print("✅ Alinhamento individual aplicado aos frames")
