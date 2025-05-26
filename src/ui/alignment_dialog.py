# src/ui/alignment_dialog.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor
import logging

print("📐 [INFO] Carregando módulo: AlignmentDialog Individual...")


class AlignmentDialog(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.current_index = 0
        self.configs = []

        self.setWindowTitle("🧱 Alinhamento Individual dos Frames")
        self.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.layout = QVBoxLayout(self)

        # Label de título
        self.title_label = QLabel("👁️ Prévia do Frame:")
        self.title_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.title_label)

        # Miniatura
        self.preview_area = QLabel()
        self.preview_area.setFixedSize(128, 128)
        self.preview_area.setStyleSheet("background-color: transparent;")
        self.layout.addWidget(self.preview_area)

        # Info do frame
        self.frame_info = QLabel(f"Frame {self.current_index + 1} de {len(canvas.selected_rects)}")
        self.frame_info.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.frame_info)

        # Navegação entre frames
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⏮️ Anterior")
        self.next_btn = QPushButton("⏭️ Próximo")
        self.prev_btn.clicked.connect(self.prev_frame)
        self.next_btn.clicked.connect(self.next_frame)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        self.layout.addLayout(nav_layout)

        # Horizontal
        h_layout = QHBoxLayout()
        self.h_combo = QComboBox()
        self.h_combo.addItems(["Esquerda", "Centro", "Direita"])
        self.h_combo.currentIndexChanged.connect(self.update_preview)
        h_layout.addWidget(QLabel("Horizontal:"))
        h_layout.addWidget(self.h_combo)
        self.layout.addLayout(h_layout)

        # Vertical
        v_layout = QHBoxLayout()
        self.v_combo = QComboBox()
        self.v_combo.addItems(["Topo", "Centro", "Base"])
        self.v_combo.currentIndexChanged.connect(self.update_preview)
        v_layout.addWidget(QLabel("Vertical:"))
        v_layout.addWidget(self.v_combo)
        self.layout.addLayout(v_layout)

        # Uniforme
        self.uniform_checkbox = QCheckBox("📏 Quadro Uniforme")
        self.uniform_checkbox.setChecked(True)
        self.uniform_checkbox.toggled.connect(self.update_preview)
        self.layout.addWidget(self.uniform_checkbox)

        # Botões OK / Cancelar
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("✔️ Confirmar")
        cancel_btn = QPushButton("❌ Cancelar")
        confirm_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)

        # Configura inicial
        self._load_initial_configs()
        if self.canvas.selected_rects:
            self.update_combo_boxes()
            self.update_preview()

    def _load_initial_configs(self):
        """Carrega ou cria configurações individuais para cada frame"""
        count = len(self.canvas.selected_rects)
        if hasattr(self.canvas, "individual_alignment_configs"):
            self.configs = self.canvas.individual_alignment_configs.copy()
            while len(self.configs) < count:
                self.configs.append({
                    "horizontal": "center",
                    "vertical": "bottom",
                    "uniform": True
                })
        else:
            self.configs = [{
                "horizontal": "center",
                "vertical": "bottom",
                "uniform": True
            } for _ in range(count)]
            self.canvas.individual_alignment_configs = self.configs

    def update_combo_boxes(self):
        current_config = self.configs[self.current_index]
        self.h_combo.setCurrentText(
            {"left": "Esquerda", "center": "Centro", "right": "Direita"}[current_config["horizontal"]]
        )
        self.v_combo.setCurrentText(
            {"top": "Topo", "center": "Centro", "bottom": "Base"}[current_config["vertical"]]
        )
        self.uniform_checkbox.setChecked(current_config.get("uniform", True))

    def _get_selected_frame(self, index):
        rect = self.canvas.selected_rects[index]
        bg = self.canvas.background
        if bg and not bg.isNull():
            return bg.copy(rect)
        return QPixmap(64, 64).fill(Qt.transparent)

    def _create_aligned_preview(self, frame, h_align="center", v_align="bottom", uniform=True):
        size = 128
        bg = QPixmap(size, size)
        bg.fill(Qt.transparent)

        if not frame or frame.isNull():
            return bg

        painter = QPainter(bg)
        painter.setRenderHint(QPainter.Antialiasing)

        frame_size = frame.size()
        x_offset = (size - frame_size.width()) // 2
        y_offset = (size - frame_size.height()) // 2

        if not uniform:
            painter.drawPixmap(0, 0, frame)
            painter.end()
            return bg

        if h_align == "left":
            x_offset = 0
        elif h_align == "right":
            x_offset = size - frame_size.width()

        if v_align == "top":
            y_offset = 0
        elif v_align == "bottom":
            y_offset = size - frame_size.height()

        painter.drawPixmap(x_offset, y_offset, frame)
        painter.end()
        return bg

    def update_preview(self):
        frame = self._get_selected_frame(self.current_index)
        h_map = {"Esquerda": "left", "Centro": "center", "Direita": "right"}
        v_map = {"Topo": "top", "Centro": "center", "Base": "bottom"}

        h_align = h_map[self.h_combo.currentText()]
        v_align = v_map[self.v_combo.currentText()]
        uniform = self.uniform_checkbox.isChecked()

        preview = self._create_aligned_preview(frame, h_align, v_align, uniform)
        self.preview_area.setPixmap(preview.scaled(
            self.preview_area.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def save_current_config(self):
        h_map = {"Esquerda": "left", "Centro": "center", "Direita": "right"}
        v_map = {"Topo": "top", "Centro": "center", "Base": "bottom"}

        self.configs[self.current_index] = {
            "horizontal": h_map[self.h_combo.currentText()],
            "vertical": v_map[self.v_combo.currentText()],
            "uniform": self.uniform_checkbox.isChecked()
        }

        # Salva no canvas
        self.canvas.individual_alignment_configs = self.configs

    def prev_frame(self):
        self.save_current_config()
        if self.current_index > 0:
            self.current_index -= 1
            self.update_combo_boxes()
            self.update_preview()
            self.update_frame_info()

    def next_frame(self):
        self.save_current_config()
        if self.current_index < len(self.canvas.selected_rects) - 1:
            self.current_index += 1
            self.update_combo_boxes()
            self.update_preview()
            self.update_frame_info()

    def update_frame_info(self):
        self.frame_info.setText(f"Frame {self.current_index + 1} de {len(self.canvas.selected_rects)}")

    def get_all_configs(self):
        self.save_current_config()
        return self.configs

    def accept(self):
        self.save_current_config()
        super().accept()
