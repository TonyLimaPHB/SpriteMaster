# src/ui/canvas.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QTransform, QBrush, QImage
from PySide6.QtCore import Qt, QPoint, QRect
import logging

print("🖼️ [INFO] Carregando módulo: Canvas...")


class Canvas(QWidget):
    def __init__(self, sidebar=None, parent=None):
        super().__init__(parent)

        self.background = None  # QPixmap original (com fundo)
        self.background_image_size = None  # Tamanho real da imagem
        self.selection_start = None
        self.selection_end = None
        self.selected_rects = []  # Seleções em escala real
        self.drawing = False
        self.max_frames = 4

        # Configurações de fundo
        self.remove_background = False
        self.bg_color = QColor(Qt.GlobalColor.green)  # Cor do fundo a ser removida
        self.sidebar = sidebar  # Referência ao Sidebar

        # Zoom
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0

        # Estado do fundo xadrez
        self.checkered_applied = False  # Indica se o xadrez já foi aplicado

        self.setStyleSheet("background-color: #1e1e1e;")
        self.setFocusPolicy(Qt.StrongFocus)

        # Alinhamento individual dos frames
        self.individual_alignment_configs = []

    def set_background(self, pixmap: QPixmap):
        """Define a imagem de fundo e aplica o zoom"""
        if pixmap.isNull():
            return

        self.background = pixmap.copy()
        self.background_image_size = pixmap.size()

        # Aplica remoção de fundo e xadrez apenas uma vez
        if self.remove_background and not self.checkered_applied:
            self._apply_removal_and_checkered()
        else:
            transform = QTransform().scale(self.zoom_level, self.zoom_level)
            scaled_pixmap = self.background.transformed(transform)
            self.setFixedSize(scaled_pixmap.size())
            self.update()

    def _apply_removal_and_checkered(self):
        """Remove cor de fundo e aplica fundo xadrez translúcido apenas uma vez"""
        image = self.background.toImage().convertToFormat(QImage.Format_ARGB32)

        r, g, b = self.bg_color.red(), self.bg_color.green(), self.bg_color.blue()

        # Remove pixels com a cor de fundo
        for y in range(image.height()):
            for x in range(image.width()):
                pixel_color = QColor(image.pixel(x, y))
                if pixel_color.red() == r and pixel_color.green() == g and pixel_color.blue() == b:
                    image.setPixelColor(x, y, QColor(0, 0, 0, 0))  # Transparente

        # Converte para QPixmap
        temp_pixmap = QPixmap.fromImage(image)

        # Cria um novo QPixmap com o xadrez como fundo visual
        self.background_display = QPixmap(temp_pixmap.size())
        self.background_display.fill(Qt.transparent)

        painter = QPainter(self.background_display)
        self.draw_checkered_background(painter)
        painter.drawPixmap(0, 0, temp_pixmap)
        painter.end()

        # Marca que o xadrez foi aplicado
        self.checkered_applied = True

        # Aplica o zoom somente uma vez
        self.background = self.background_display.copy(self.background_display.rect())
        self._apply_zoom_and_update()

    def draw_checkered_background(self, painter):
        """Desenha o fundo xadrez translúcido diretamente no painter"""
        checkered_size = 16
        color1 = QColor(200, 200, 200, 100)  # Cinza translúcido
        color2 = QColor(240, 240, 240, 100)  # Branco translúcido

        rect = self.background_display.rect()
        width, height = rect.width(), rect.height()

        for y in range(0, height, checkered_size):
            for x in range(0, width, checkered_size):
                color = color1 if ((x + y) // checkered_size) % 2 == 0 else color2
                painter.fillRect(x, y, checkered_size, checkered_size, QBrush(color))

    def _apply_zoom_and_update(self):
        """Aplica o zoom à imagem final (já com xadrez aplicado)"""
        if not self.background:
            return

        transform = QTransform().scale(self.zoom_level, self.zoom_level)
        scaled_pixmap = self.background.transformed(transform)
        self.setFixedSize(scaled_pixmap.size())
        self.update()

    def get_original_rect(self, qrect):
        """
        Converte QRect do canvas (com zoom) para escala real da imagem
        :param qrect: QRect em escala do Canvas (com zoom)
        :return: QRect em escala real da imagem
        """
        scale = self.zoom_level
        x = int(qrect.x() / scale)
        y = int(qrect.y() / scale)
        width = int(qrect.width() / scale)
        height = int(qrect.height() / scale)
        return QRect(x, y, width, height)

    def _apply_zoom_to_rect(self, rect):
        """Aplica o zoom a um QRect"""
        return QRect(
            int(rect.x() * self.zoom_level),
            int(rect.y() * self.zoom_level),
            int(rect.width() * self.zoom_level),
            int(rect.height() * self.zoom_level)
        )

    def paintEvent(self, event):
        if not self.background:
            return

        painter = QPainter(self)
        world_transform = painter.worldTransform()
        painter.setWorldTransform(QTransform())

        # Desenha imagem final com zoom
        scaled_pixmap = self.background.transformed(
            QTransform().scale(self.zoom_level, self.zoom_level)
        )
        painter.drawPixmap(0, 0, scaled_pixmap)

        # Redesenha seleções verdes translúcidos
        pen_selected = QPen(QColor(0, 255, 0, 200), 2, Qt.SolidLine)
        brush_selected = QColor(0, 255, 0, 50)

        for rect in self.selected_rects:
            transformed_rect = self._apply_zoom_to_rect(rect)
            painter.setPen(pen_selected)
            painter.fillRect(transformed_rect, brush_selected)
            painter.drawRect(transformed_rect)

        # Redesenha seleção em andamento (azul translúcido)
        if self.drawing and self.selection_start and self.selection_end:
            pen_drawing = QPen(QColor(0, 150, 255, 200), 2, Qt.DashLine)
            brush_drawing = QColor(0, 150, 255, 70)
            rect = self._get_selection_rect()
            painter.setPen(pen_drawing)
            painter.fillRect(rect, brush_drawing)
            painter.drawRect(rect)

        painter.setWorldTransform(world_transform)

    def _get_selection_rect(self):
        start = self.selection_start
        end = self.selection_end
        return QRect(start, end).normalized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.background.isNull():
            self.selection_start = event.position().toPoint()
            self.drawing = True
            self.update()

        elif event.button() == Qt.RightButton and not self.background.isNull():
            self.pick_color_from_image(event.position().toPoint())

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.selection_end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.selection_end = event.position().toPoint()
            rect_on_canvas = self._get_selection_rect()
            rect_real = self.get_original_rect(rect_on_canvas)

            if len(self.selected_rects) < self.max_frames:
                self.selected_rects.append(rect_real)
                while len(self.individual_alignment_configs) < len(self.selected_rects):
                    self.individual_alignment_configs.append({
                        "horizontal": "center",
                        "vertical": "bottom",
                        "uniform": True
                    })

            self.drawing = False
            self.selection_start = None
            self.selection_end = None
            self.update()
            self.update_status()

    def keyPressEvent(self, event):
        """Desfaz última seleção com Ctrl+Z"""
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            if self.selected_rects:
                self.selected_rects.pop()
                if len(self.individual_alignment_configs) > len(self.selected_rects):
                    self.individual_alignment_configs.pop()
                self.update_status()
                self.update()
                print("⏮️ Seleção desfeita com Ctrl+Z")
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        """Zoom com rolagem do mouse (Ctrl + rolar)"""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_level = min(self.zoom_level + 0.1, self.max_zoom)
            else:
                self.zoom_level = max(self.zoom_level - 0.1, self.min_zoom)
            self._apply_zoom_and_update()
        else:
            super().wheelEvent(event)

    def pick_color_from_image(self, pos):
        """Pega a cor diretamente da imagem na posição clicada"""
        if not self.background:
            return

        try:
            image = self.background.toImage()
            x = int(pos.x() / self.zoom_level)
            y = int(pos.y() / self.zoom_level)
            pixel = image.pixel(x, y)
            color = QColor(pixel)

            self.bg_color = color
            if self.sidebar:
                self.sidebar.update_bg_button_color(color)
            self.update()

            # Se remover fundo estiver ativo, atualiza a imagem com fundo xadrez translúcido
            if self.remove_background:
                self.checkered_applied = False  # Força reaplicação da transparência
                self._apply_removal_and_checkered()

        except Exception as e:
            logging.error(f"❌ Erro ao pegar cor da imagem: {e}")

    def update_status(self):
        if self.sidebar:
            self.sidebar.update_status()

    def get_alignment_config(self):
        return getattr(self, "_alignment_config", {
            "horizontal": "center",
            "vertical": "bottom",
            "uniform": True
        })

    def set_alignment_config(self, config):
        self._alignment_config = config
        self.individual_alignment_configs = [
            config.copy() for _ in self.selected_rects
        ]
        self.update()

    def get_individual_alignment(self, index):
        if 0 <= index < len(self.individual_alignment_configs):
            return self.individual_alignment_configs[index]
        return self.get_alignment_config()

    def set_individual_alignment(self, index, config):
        if 0 <= index < len(self.selected_rects):
            if index >= len(self.individual_alignment_configs):
                self.individual_alignment_configs.extend([
                    self.get_alignment_config() for _ in range(index - len(self.individual_alignment_configs) + 1)
                ])
            self.individual_alignment_configs[index] = config
            self.update()

    def get_bg_removal_config(self):
        return {
            "remove_background": self.remove_background,
            "bg_color": self.bg_color
        }

    def clear_selections(self):
        self.selected_rects.clear()
        self.individual_alignment_configs.clear()
        self.update()
        self.update_status()

    def set_max_frames(self, value):
        self.max_frames = max(1, value)
        self.update_status()
        self.update()

    def _apply_zoom_to_rect(self, rect):
        return QRect(
            int(rect.x() * self.zoom_level),
            int(rect.y() * self.zoom_level),
            int(rect.width() * self.zoom_level),
            int(rect.height() * self.zoom_level)
        )