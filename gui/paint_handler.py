from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

from ..utils.save_manager import SaveManager
from ..models.animal_type import AnimalType, TRACKED_ANIMAL_TYPES
from ..constants import INITIAL_MONEY, ANIMAL_RENDER_SETTINGS


class PaintHandler:
    @staticmethod
    def _get_animal_render_config(animal_type: AnimalType, is_child: bool):
        stage = "child" if is_child else "adult"
        animal_config = ANIMAL_RENDER_SETTINGS.get(animal_type.name, {}).get(stage, {})
        return {
            "scale": animal_config.get("scale", 1.0),
            "offset_x": animal_config.get("offset_x", 0),
            "offset_y": animal_config.get("offset_y", 0),
        }

    @staticmethod
    def _draw_animal_emoji(painter: QPainter, animal_type: AnimalType, pos_x: int, pos_y: int, cell_size: int):
        painter.save()
        font = painter.font()
        font.setPointSize(max(18, int(cell_size * 0.42)))
        painter.setFont(font)
        painter.drawText(
            pos_x,
            pos_y + max(0, cell_size // 12),
            cell_size,
            int(cell_size * 0.65),
            Qt.AlignmentFlag.AlignCenter,
            animal_type.emoji,
        )
        painter.restore()

    def draw_statistics(self, painter: QPainter, stats: dict, money: int, current_day: int):
        """Draw statistics panel"""
        painter.setPen(QColor(0, 0, 0))
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        previous_money = INITIAL_MONEY
        save_data = SaveManager.load_game()

        if save_data and "previous_money" in save_data:
            previous_money = save_data["previous_money"]

        money_increase =  money - previous_money

        # Money display
        painter.drawText(10, 20, f"Money: {money} coins")

        if money_increase > 0:
            painter.setPen(QColor(0, 0, 255))
            painter.drawText(50, 30, f"+{money_increase}")
            painter.setPen(QColor(0, 0, 0))
        elif money_increase < 0:
            painter.setPen(QColor(255, 0, 0))
            painter.drawText(50, 30, f"{money_increase}")
            painter.setPen(QColor(0, 0, 0))

        painter.drawText(10, 45, f"Day: {current_day}")

        # Statistics
        y_pos = 65
        font.setPointSize(11)
        painter.setFont(font)
        painter.drawText(10, y_pos, "Statistics:")
        y_pos += 15

        font.setBold(False)
        painter.setFont(font)
        for animal_type in TRACKED_ANIMAL_TYPES:
            stat = stats.get(animal_type, {"sold": 0, "dead": 0})
            text = f"{animal_type.emoji} {animal_type.label}: Sold: {stat['sold']}, Dead: {stat['dead']}"
            painter.drawText(10, y_pos, text)
            y_pos += 18

    def draw_field(self, painter: QPainter, field, images: dict, pos_x: int, pos_y: int, cell_size: int):
        """Draw field and its contents"""
        if field.animal:
            if field.animal.is_dead:
                # Draw grave
                grave_size = min(cell_size - 20, images['grave'].width())
                painter.drawPixmap(
                    pos_x + (cell_size - grave_size) // 2,
                    pos_y + (cell_size - grave_size) // 2,
                    grave_size,
                    grave_size,
                    images['grave']
                )
                # Draw dead status
                painter.setPen(QColor(255, 0, 0))
                painter.drawText(
                    pos_x,
                    pos_y + cell_size - 5,
                    f"Dead ({field.animal.animal_type.label})"
                )
            else:
                # Draw living animal
                animal_type = field.animal.animal_type
                animal_image = images.get('animals', {}).get(animal_type)
                child_images = images.get('child_animals', {})
                child_image = child_images.get(animal_type)
                is_child = field.animal.growth < 50
                if is_child and child_image and not child_image.isNull():
                    animal_image = child_image

                if animal_image and not animal_image.isNull():
                    render_config = self._get_animal_render_config(animal_type, is_child)
                    base_animal_size = min(cell_size - 20, animal_image.width(), animal_image.height())
                    animal_scale = max(0.1, float(render_config["scale"]))
                    animal_size = max(1, int(base_animal_size * animal_scale))
                    offset_x = int(render_config["offset_x"])
                    offset_y = int(render_config["offset_y"])

                    painter.drawPixmap(
                        pos_x + (cell_size - animal_size) // 2 + offset_x,
                        pos_y + (cell_size - animal_size) // 2 + offset_y,
                        animal_size,
                        animal_size,
                        animal_image
                    )
                else:
                    self._draw_animal_emoji(painter, animal_type, pos_x, pos_y, cell_size)

                # Draw product if exists
                product_image = images.get('products', {}).get(field.animal.animal_type)
                if field.animal.has_product and product_image and not product_image.isNull():
                    product_size = min(cell_size // 4, product_image.width())
                    painter.drawPixmap(
                        pos_x + cell_size - product_size - 5,
                        pos_y + cell_size - product_size - 5,
                        int(product_size - product_size/6),
                        product_size,
                        product_image
                    )

                # Draw growth and price information
                painter.setBrush(Qt.BrushStyle.NoBrush)
                growth_text = f"{field.animal.growth}%"
                if field.animal.can_sell():
                    growth_text += f" (Value: {field.animal.get_sale_price()} coins)"
                else:
                    painter.setPen(QColor(0, 0, 0))

                # Set font size
                font = painter.font()
                font.setPointSize(10)
                painter.setFont(font)

                # Draw text
                painter.drawText(
                    pos_x + 5,
                    pos_y + cell_size - 5,
                    growth_text
                )
