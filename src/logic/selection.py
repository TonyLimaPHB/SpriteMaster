# src/logic/selection.py

from PySide6.QtCore import QRect
import logging

print("✂️ [INFO] Carregando módulo: Selection...")

class SelectionManager:
    def __init__(self, max_frames=4):
        """
        Gerencia as seleções feitas pelo usuário (frames selecionados)
        :param max_frames: Número máximo de frames permitidos
        """
        self.rects = []
        self.max_frames = max(1, max_frames)  # Garante que não seja zero ou negativo
        logging.info(f"Intialized SelectionManager | Max frames: {self.max_frames}")

    def add_rect(self, rect: QRect):
        """
        Adiciona uma nova seleção se não ultrapassar o limite
        :param rect: QRect com a área selecionada
        """
        if not isinstance(rect, QRect):
            logging.warning("⚠️ Tentativa de adicionar um frame inválido.")
            return

        if len(self.rects) < self.max_frames:
            self.rects.append(rect)
            logging.debug(f"➕ Frame adicionado: {rect}")
        else:
            logging.warning(f"⚠️ Limite de {self.max_frames} frames atingido.")

    def set_max_frames(self, value: int):
        """
        Define o número máximo de frames que podem ser selecionados
        :param value: Novo limite de frames
        """
        if value < 1:
            logging.warning("⚠️ Valor inválido para frames máximos. Usando padrão: 1")
            value = 1

        self.max_frames = value
        logging.info(f"🔢 Limite de frames alterado para: {value}")

    def clear(self):
        """Limpa todas as seleções"""
        self.rects.clear()
        logging.info("🧹 Seleções limpas.")

    def get_selections(self):
        """Retorna todos os frames selecionados"""
        return self.rects.copy()

    def remove_last(self):
        """Remove a última seleção, se existir"""
        if self.rects:
            removed = self.rects.pop()
            logging.info(f"🗑️ Última seleção removida: {removed}")
