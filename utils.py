import os
import sys
from enum import Enum
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget
from aqt import mw, gui_hooks
from aqt.utils import showInfo


class AnimalType(Enum):
    PIG = "豚"
    CHICKEN = "鶏"
    COW = "牛"
    EMPTY = "空"


class Animal:
    def __init__(self, animal_type: AnimalType):
        self.animal_type = animal_type
        self.growth = 0  # 成長度
        self.max_growth = 100

    def grow(self):
        self.growth = min(self.growth + 1, self.max_growth)

    def is_mature(self):
        return self.growth >= self.max_growth


class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animal = None  # 動物がいない場合はNone

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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ranch")
        self.setGeometry(100, 100, 800, 600)

        # フィールドの初期化
        self.fields = []
        self.selected_field = None
        self.cell_size = 100  # マスの大きさ

        # 現在選択中の動物タイプ
        self.current_animal_type = AnimalType.PIG

        # 3x3のフィールドを作成
        for y in range(3):
            row = []
            for x in range(3):
                row.append(Field(x, y))
            self.fields.append(row)

        # ゲームループを設定（60FPS）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(1000 // 60)

        gui_hooks.reviewer_did_answer_card.append(self.called)

    def cycle_animal_type(self):
        # 動物の種類を順番に切り替える
        if self.current_animal_type == AnimalType.PIG:
            self.current_animal_type = AnimalType.CHICKEN
        elif self.current_animal_type == AnimalType.CHICKEN:
            self.current_animal_type = AnimalType.COW
        elif self.current_animal_type == AnimalType.COW:
            self.current_animal_type = AnimalType.PIG

    def update_game(self):
        # 全ての動物の成長処理
        for row in self.fields:
            for field in row:
                if field.animal:
                    field.animal.grow()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # マスを描画
        for y in range(3):
            for x in range(3):
                field = self.fields[y][x]

                # マスの枠を描画
                painter.setPen(QColor(0, 0, 0))
                painter.setBrush(QColor(255, 255, 255))  # マスの背景を白に設定
                painter.drawRect(x * self.cell_size, y * self.cell_size,
                                 self.cell_size, self.cell_size)

                # 動物を描画
                if field.animal:
                    # ブラシの色を設定
                    painter.setBrush(self.get_animal_color(field.animal.animal_type))
                    padding = 10
                    painter.drawEllipse(
                        x * self.cell_size + padding,
                        y * self.cell_size + padding,
                        self.cell_size - 2 * padding,
                        self.cell_size - 2 * padding
                    )

                    # 成長度を表示
                    painter.setBrush(Qt.BrushStyle.NoBrush)  # テキスト描画用にブラシをクリア
                    painter.drawText(
                        x * self.cell_size,
                        y * self.cell_size + self.cell_size - 5,
                        f"{field.animal.growth}%"
                    )

        # 現在選択中の動物タイプを表示
        painter.setBrush(Qt.BrushStyle.NoBrush)  # テキスト描画用にブラシをクリア
        painter.drawText(10, self.height() - 10, f"選択中: {self.current_animal_type.value}")


    def get_animal_color(self, animal_type):
        if animal_type == AnimalType.PIG:
            return QColor(255, 192, 203)  # ピンク
        elif animal_type == AnimalType.CHICKEN:
            return QColor(255, 255, 0)  # 黄色
        elif animal_type == AnimalType.COW:
            return QColor(139, 69, 19)  # 茶色
        return QColor(255, 255, 255)  # 白

    def mousePressEvent(self, event):
        # クリックされたマスを特定
        x = event.position().x() // self.cell_size
        y = event.position().y() // self.cell_size

        if 0 <= x < 3 and 0 <= y < 3:
            field = self.fields[int(y)][int(x)]
            if event.button() == Qt.MouseButton.LeftButton:
                # 左クリック: 動物を配置
                if field.animal is None:
                    # 現在選択中の動物タイプで動物を配置
                    field.add_animal(Animal(self.current_animal_type))
                    # 次の動物タイプに切り替え
                    self.cycle_animal_type()
            elif event.button() == Qt.MouseButton.RightButton:
                # 右クリック: 動物を削除
                field.remove_animal()

    def called(self, reviewer, card, ease):
        # カードを回答したときの処理
        # 例: ランダムな位置に動物を追加
        import random
        x = random.randint(0, 2)
        y = random.randint(0, 2)
        if self.fields[y][x].animal is None:
            animal_type = random.choice([AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW])
            self.fields[y][x].add_animal(Animal(animal_type))


def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()