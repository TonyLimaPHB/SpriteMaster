# src/logic/exporter.py

from PIL import Image
import logging

print("📦 [INFO] Carregando módulo: Exporter...")

class SpriteSheetExporter:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original_image = Image.open(image_path).convert("RGBA")
        self.frames = []

        logging.info(f"🖼️ Imagem carregada: {image_path} ({self.original_image.size})")

    def add_frame(self, rect, config=None):
        """
        Adiciona um frame com base na seleção feita no Canvas
        :param rect: QRect com as coordenadas em escala real
        :param config: Dicionário com configurações de fundo e alinhamento
        """
        x = rect.x()
        y = rect.y()
        width = rect.width()
        height = rect.height()
        box = (x, y, x + width, y + height)

        try:
            frame = self.original_image.crop(box)

            if config and config.get("remove_background"):
                bg_color = config["bg_color"]
                frame = self._remove_background(frame, bg_color)

            align_config = config.get("align_config", {
                "horizontal": "center",
                "vertical": "bottom",
                "uniform": True
            })

            if align_config.get("uniform", False):
                max_dim = max(frame.width, frame.height)
                base = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))

                h_align = align_config.get("horizontal", "center")
                v_align = align_config.get("vertical", "bottom")

                # Cálculo das coordenadas com base no alinhamento
                x_off = {
                    "left": 0,
                    "center": (max_dim - frame.width) // 2,
                    "right": max_dim - frame.width
                }[h_align]

                y_off = {
                    "top": 0,
                    "center": (max_dim - frame.height) // 2,
                    "bottom": max_dim - frame.height
                }[v_align]

                base.paste(frame, (x_off, y_off), frame)
                frame = base

            self.frames.append(frame)
            logging.debug(f"✂️ Frame adicionado: {box}")

        except Exception as e:
            logging.error(f"❌ Erro ao adicionar frame: {e}", exc_info=True)

    def _remove_background(self, image, color):
        """
        Remove uma cor específica da imagem e substitui por transparência
        :param image: Imagem PIL.Image
        :param color: QColor com a cor a ser removida
        """
        r, g, b = color.red(), color.green(), color.blue()
        data = image.getdata()

        new_data = []
        for pixel in data:
            if len(pixel) == 4:
                pr, pg, pb, pa = pixel
            else:
                pr, pg, pb = pixel
                pa = 255

            if pr == r and pg == g and pb == b:
                new_data.append((0, 0, 0, 0))  # Transparente
            else:
                new_data.append(pixel)

        image = image.copy()
        image.putdata(new_data)
        return image

    def export(self, output_path, layout="horizontal"):
        """
        Exporta todos os frames como spritesheet
        :param output_path: Caminho onde será salvo
        :param layout: 'horizontal' ou 'vertical'
        """
        count = len(self.frames)
        if count == 0:
            logging.warning("⚠️ Nenhum frame foi adicionado.")
            return False

        max_width = max(f.width for f in self.frames)
        max_height = max(f.height for f in self.frames)

        sheet_size = (
            max_width * count if layout == "horizontal" else max_width,
            max_height if layout == "horizontal" else max_height * count
        )

        sheet = Image.new("RGBA", sheet_size, (0, 0, 0, 0))

        try:
            if layout == "horizontal":
                for i, frame in enumerate(self.frames):
                    sheet.paste(frame, (i * max_width, 0), frame)
            elif layout == "vertical":
                for i, frame in enumerate(self.frames):
                    sheet.paste(frame, (0, i * max_height), frame)
            else:
                raise ValueError(f"Layout desconhecido: {layout}")

            sheet.save(output_path, "PNG")
            logging.info(f"💾 Spritesheet salva em: {output_path}")
            return True

        except Exception as e:
            logging.error(f"❌ Erro ao salvar spritesheet: {e}", exc_info=True)
            return False
