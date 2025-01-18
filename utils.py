import os
import sys
from enum import Enum
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from aqt import mw, gui_hooks
from aqt.utils import showInfo


class AnimalType(Enum):
    PIG = ("豚", 100)
    CHICKEN = ("鶏", 50)
    COW = ("牛", 200)
    EMPTY = ("空", 0)

    def __init__(self, label, price):
        self._label = label
        self._price = price

    @property
    def label(self):
        return self._label

    @property
    def price(self):
        return self._price


class Animal:
    def __init__(self, animal_type: AnimalType):
        self.animal_type = animal_type
        self.growth = 0
        self.max_growth = 100

    def grow(self):
        self.growth = min(self.growth + 5, self.max_growth)

    def get_sale_price(self):
        growth_multiplier = 1 + (self.growth / 100)
        return int(self.animal_type.price * growth_multiplier)

    def can_sell(self):
        return self.growth >= 50


class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animal = None

    def add_animal(self, animal: Animal):
        if self.animal is None:
            self.animal = animal
            return True
        return False

    def remove_animal(self):
        animal = self.animal
        self.animal = None
        return animal


class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ranch")
        self.setGeometry(100, 100, 800, 600)

        # 所持金を初期化
        self.money = 1000

        # フィールドの初期化
        self.fields = []
        self.cell_size = 100
        self.unlocked_fields = 1  # 最初は1マスだけ解放

        # 3x3のフィールドを作成
        for y in range(3):
            row = []
            for x in range(3):
                row.append(Field(x, y))
            self.fields.append(row)

        # 現在選択中の動物タイプ
        self.current_animal_type = AnimalType.PIG

        # Ankiのフックを設定
        gui_hooks.reviewer_did_answer_card.append(self.called)

    def cycle_animal_type(self):
        if self.current_animal_type == AnimalType.PIG:
            self.current_animal_type = AnimalType.CHICKEN
        elif self.current_animal_type == AnimalType.CHICKEN:
            self.current_animal_type = AnimalType.COW
        elif self.current_animal_type == AnimalType.COW:
            self.current_animal_type = AnimalType.PIG

    def get_field_price(self):
        # 敷地の価格計算（指数関数的に上昇）
        base_price = 500  # 基本価格
        return int(base_price * (1.5 ** (self.unlocked_fields - 1)))

    def can_unlock_field(self):
        return self.unlocked_fields < 9  # 最大9マス

    def try_unlock_field(self):
        if not self.can_unlock_field():
            QMessageBox.warning(self, "購入不可", "これ以上敷地を購入できません！")
            return False

        price = self.get_field_price()
        if self.money < price:
            QMessageBox.warning(self, "購入不可", f"所持金が足りません！\n必要金額: {price}円")
            return False

        reply = QMessageBox.question(self, '敷地を購入',
                                     f'新しい敷地を{price}円で購入しますか？',
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.money -= price
            self.unlocked_fields += 1
            self.update()
            return True
        return False

    def get_animal_color(self, animal_type):
        if animal_type == AnimalType.PIG:
            return QColor(255, 192, 203)  # ピンク
        elif animal_type == AnimalType.CHICKEN:
            return QColor(255, 255, 0)  # 黄色
        elif animal_type == AnimalType.COW:
            return QColor(139, 69, 19)  # 茶色
        return QColor(255, 255, 255)  # 白

    def try_sell_animal(self, field):
        if not field.animal:
            return

        if not field.animal.can_sell():
            QMessageBox.warning(self, "売却不可",
                                "この動物はまだ売却できません。\n成長率が50%以上必要です。")
            return

        price = field.animal.get_sale_price()
        reply = QMessageBox.question(self, '動物を売る',
                                     f'この{field.animal.animal_type.label}を{price}円で売りますか？',
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.money += price
            field.remove_animal()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # 所持金を表示
        painter.setPen(QColor(0, 0, 0))
        font = painter.font()
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(10, 30, f"所持金: {self.money}円")

        # 次の敷地の価格を表示
        if self.can_unlock_field():
            next_price = self.get_field_price()
            painter.drawText(10, 60, f"次の敷地の価格: {next_price}円")

        # マスを描画
        for y in range(3):
            for x in range(3):
                field = self.fields[y][x]
                field_number = y * 3 + x + 1

                # マスの枠を描画
                painter.setPen(QColor(0, 0, 0))

                # ロック状態に応じて背景色を変更
                if field_number <= self.unlocked_fields:
                    painter.setBrush(QColor(255, 255, 255))  # 解放済み
                else:
                    painter.setBrush(QColor(200, 200, 200))  # ロック中

                painter.drawRect(x * self.cell_size, y * self.cell_size + 80,
                                 self.cell_size, self.cell_size)

                # ロックされたマスには鍵マークを表示
                if field_number > self.unlocked_fields:
                    painter.drawText(
                        x * self.cell_size + self.cell_size // 2 - 10,
                        y * self.cell_size + 80 + self.cell_size // 2,
                        "🔒"
                    )
                    continue

                # 動物を描画（解放済みのマスのみ）
                if field.animal:
                    painter.setBrush(self.get_animal_color(field.animal.animal_type))
                    padding = 10
                    painter.drawEllipse(
                        x * self.cell_size + padding,
                        y * self.cell_size + 80 + padding,
                        self.cell_size - 2 * padding,
                        self.cell_size - 2 * padding
                    )

                    # 成長度を表示
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    growth_text = f"{field.animal.growth}%"
                    if field.animal.can_sell():
                        growth_text += f" (売値: {field.animal.get_sale_price()}円)"
                    painter.drawText(
                        x * self.cell_size,
                        y * self.cell_size + 80 + self.cell_size - 5,
                        growth_text
                    )

        # 現在選択中の動物タイプを表示
        painter.drawText(10, self.height() - 10,
                         f"選択中: {self.current_animal_type.label}")

    def mousePressEvent(self, event):
        # Y座標を調整（80ピクセルのオフセットを考慮）
        x = int(event.position().x() // self.cell_size)
        y = int((event.position().y() - 80) // self.cell_size)

        if 0 <= x < 3 and 0 <= y < 3:
            field_number = y * 3 + x + 1

            # ロックされたマスをクリックした場合
            if field_number > self.unlocked_fields:
                self.try_unlock_field()
                return

            field = self.fields[y][x]
            if event.button() == Qt.MouseButton.LeftButton:
                if field.animal is None:
                    purchase_price = self.current_animal_type.price
                    if self.money >= purchase_price:
                        field.add_animal(Animal(self.current_animal_type))
                        self.money -= purchase_price
                        self.cycle_animal_type()
                        self.update()
                    else:
                        QMessageBox.warning(self, "購入不可",
                                            f"所持金が足りません！\n必要金額: {purchase_price}円")
            elif event.button() == Qt.MouseButton.RightButton:
                self.try_sell_animal(field)

    def called(self, reviewer, card, ease):
        # カードを回答したときの処理
        for row in self.fields:
            for field in row:
                if field.animal:
                    field.animal.grow()
        self.update()


def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()