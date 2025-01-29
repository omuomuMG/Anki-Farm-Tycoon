# gui/paint_handler.py

from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt
from ..models.animal_type import AnimalType
from ..constants import CELL_SIZE, STATS_PANEL_WIDTH


class PaintHandler:
    def draw_statistics(self, painter: QPainter, stats: dict, money: int):
        """Draw statistics panel"""
        painter.setPen(QColor(0, 0, 0))
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        # Money display
        painter.drawText(10, 20, f"Money: {money} coins")

        # Statistics
        y_pos = 40
        font.setPointSize(11)
        painter.setFont(font)
        painter.drawText(10, y_pos, "Statistics:")
        y_pos += 15

        font.setBold(False)
        painter.setFont(font)
        for animal_type in [AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW]:
            stat = stats[animal_type]
            text = f"{animal_type.emoji} {animal_type.label}: Sold: {stat['sold']}, Cleaned: {stat['cleaned']}"
            painter.drawText(10, y_pos, text)
            y_pos += 20

    def draw_field(self, painter: QPainter, field, images: dict, pos_x: int, pos_y: int):
        """Draw field and its contents"""
        if field.animal:
            if field.animal.is_dead:
                # Draw grave
                grave_size = min(CELL_SIZE - 20, images['grave'].width())
                painter.drawPixmap(
                    pos_x + (CELL_SIZE - grave_size) // 2,
                    pos_y + (CELL_SIZE - grave_size) // 2,
                    grave_size,
                    grave_size,
                    images['grave']
                )
                # Draw dead status
                painter.setPen(QColor(255, 0, 0))
                painter.drawText(
                    pos_x,
                    pos_y + CELL_SIZE - 5,
                    f"Dead ({field.animal.animal_type.label})"
                )
            else:
                # Draw living animal
                animal_image = images['animals'][field.animal.animal_type]
                animal_size = min(CELL_SIZE - 10, animal_image.width())
                painter.drawPixmap(
                    pos_x + (CELL_SIZE - animal_size) // 2,
                    pos_y + (CELL_SIZE - animal_size) // 2,
                    animal_size,
                    animal_size,
                    animal_image
                )

                # Draw product if exists
                if field.animal.has_product and field.animal.animal_type in [AnimalType.CHICKEN, AnimalType.COW]:
                    product_image = images['products'][field.animal.animal_type]
                    product_size = min(CELL_SIZE // 4, product_image.width())
                    painter.drawPixmap(
                        pos_x + CELL_SIZE - product_size - 5,
                        pos_y + CELL_SIZE - product_size - 5,
                        product_size,
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
                    pos_y + CELL_SIZE - 5,
                    growth_text
                )