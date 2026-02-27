from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

from ..utils.save_manager import SaveManager
from ..models.animal_type import AnimalType
from ..constants import INITIAL_MONEY


class PaintHandler:
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
        for animal_type in [AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW, AnimalType.HORSE]:
            stat = stats[animal_type]
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
                animal_image = images['animals'][animal_type]
                child_images = images.get('child_animals', {})
                child_image = child_images.get(animal_type)
                if field.animal.growth < 50 and child_image and not child_image.isNull():
                    animal_image = child_image
                animal_size = min(cell_size - 20, animal_image.width())
                painter.drawPixmap(
                    pos_x + (cell_size - animal_size) // 2,
                    pos_y + (cell_size - animal_size) // 2,
                    animal_size,
                    animal_size,
                    animal_image
                )

                # Draw product if exists
                if field.animal.has_product and field.animal.animal_type in [AnimalType.CHICKEN, AnimalType.COW, AnimalType.PIG]:
                    product_image = images['products'][field.animal.animal_type]
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
