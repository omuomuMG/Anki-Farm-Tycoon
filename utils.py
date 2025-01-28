import os
import random
import sys
from enum import Enum
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from aqt import mw, gui_hooks
from aqt.utils import showInfo
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QCursor
from PyQt6.QtGui import QFont

def get_addon_dir():
    return os.path.dirname(os.path.abspath(__file__))


class AnimalType(Enum):
    PIG = ("豚", 100, "🐷")
    CHICKEN = ("鶏", 50, "🐔")
    COW = ("牛", 200, "🐮")
    EMPTY = ("空", 0, "")

    def __init__(self, label, price, emoji):
        self._label = label
        self._price = price
        self._emoji = emoji

    @property
    def label(self):
        return self._label

    @property
    def price(self):
        return self._price

    @property
    def emoji(self):
        return self._emoji



class Animal:
    def __init__(self, animal_type: AnimalType):
        self.animal_type = animal_type
        self.growth = 0
        self.max_growth = 150
        self.is_dead = False
        self.has_product = False  # 卵やミルクの有無を追跡

    def produce(self) -> int:
        """生産物（卵・ミルク）を生成し、収益を返す"""
        if self.is_dead:
            return 0

        if self.animal_type == AnimalType.CHICKEN:
            # 鶏の卵生産（10%の確率）
            if random.random() < 0.10:
                self.has_product = True
                return random.randint(5, 10)  # 5-10円の収入

        elif self.animal_type == AnimalType.COW:
            # 牛のミルク生産（2%の確率）
            if random.random() < 0.02:
                self.has_product = True
                return 50  # 50円の収入

        return 0

    def grow(self):
        if not self.is_dead:
            self.growth = min(self.growth + 5, self.max_growth)
            if self.growth >= self.max_growth:
                self.is_dead = True

    def get_sale_price(self):
        if self.is_dead:
            return 0
        growth_multiplier = 1 + (self.growth / 100)
        return int(self.animal_type.price * growth_multiplier)

    def can_sell(self):
        return not self.is_dead and self.growth >= 50

    def get_cleanup_cost(self):
        return int(self.animal_type.price * 0.5)  # 掃除費用は購入価格の半額


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
        self.load_images()


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

        # 統計情報の追加
        self.stats = {
            AnimalType.PIG: {"sold": 0, "cleaned": 0},
            AnimalType.CHICKEN: {"sold": 0, "cleaned": 0},
            AnimalType.COW: {"sold": 0, "cleaned": 0}
        }

        # Ankiのフックを設定
        gui_hooks.reviewer_did_answer_card.append(self.called)
        self.selected_animal_type = None

    def load_images(self):
        """画像リソースを読み込む"""
        # アドオンのディレクトリパスを取得
        addon_dir = get_addon_dir()
        resources_dir = os.path.join(addon_dir, "Resources")

        # フィールドタイル画像
        self.tile_image = QPixmap(os.path.join(resources_dir, "maptile_sogen_01.svg"))
        self.locked_tile_image = QPixmap(os.path.join(resources_dir, "maptile_sogen_hana_01.svg"))

        # 動物の画像
        self.animal_images = {
            AnimalType.PIG: QPixmap(os.path.join(resources_dir, "buta.svg")),
            AnimalType.CHICKEN: QPixmap(os.path.join(resources_dir, "niwatori_male.svg")),
            AnimalType.COW: QPixmap(os.path.join(resources_dir, "ushi_red_tsuno.svg"))
        }

        #生産物の画像
        self.product_images = {
            AnimalType.CHICKEN: QPixmap(os.path.join(resources_dir, "egg.svg")),
            AnimalType.COW: QPixmap(os.path.join(resources_dir, "milk.svg"))
        }

    def show_animal_selection_dialog(self):
        menu = QMenu(self)
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                action = menu.addAction(f"{animal_type.emoji} {animal_type.label} ({animal_type.price}円)")
                action.setData(animal_type)

        # メニューを表示
        action = menu.exec(QCursor.pos())
        if action:
            return action.data()
        return None

    def try_cleanup_dead_animal(self, field):
        if not field.animal or not field.animal.is_dead:
            return

        cleanup_cost = field.animal.get_cleanup_cost()
        animal_type = field.animal.animal_type
        reply = QMessageBox.question(
            self,
            '死亡した動物の掃除',
            f'この死亡した{animal_type.label}を{cleanup_cost}円で掃除しますか？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.money >= cleanup_cost:
                self.money -= cleanup_cost
                # 掃除数を増やす
                self.stats[animal_type]["cleaned"] += 1
                field.remove_animal()
                self.update()
            else:
                QMessageBox.warning(self, "掃除不可",
                                  f"所持金が足りません！\n必要金額: {cleanup_cost}円")

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
        animal_type = field.animal.animal_type
        reply = QMessageBox.question(self, '動物を売る',
                                   f'この{animal_type.label}を{price}円で売りますか？',
                                   QMessageBox.StandardButton.Yes |
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.money += price
            # 出荷数を増やす
            self.stats[animal_type]["sold"] += 1
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

        # 統計情報を表示
        y_pos = 60
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(10, y_pos, "統計情報:")
        y_pos += 20

        for animal_type in [AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW]:
            stats = self.stats[animal_type]
            painter.drawText(
                10,
                y_pos,
                f"{animal_type.emoji} {animal_type.label}: "
                f"出荷 {stats['sold']}匹, "
                f"掃除 {stats['cleaned']}匹"
            )
            y_pos += 20

        # 次の敷地の価格を表示
        if self.can_unlock_field():
            next_price = self.get_field_price()
            painter.drawText(10, y_pos + 20, f"次の敷地の価格: {next_price}円")

        # マスを描画
        for y in range(3):
            for x in range(3):
                field = self.fields[y][x]
                field_number = y * 3 + x + 1

                # マスの位置を計算
                pos_x = x * self.cell_size
                pos_y = y * self.cell_size + 80

                # フィールドタイルを描画
                if field_number <= self.unlocked_fields:
                    # 解放済みタイル
                    painter.drawPixmap(
                        pos_x,
                        pos_y,
                        self.cell_size,
                        self.cell_size,
                        self.tile_image
                    )

                    # 動物がいる場合は動物を描画
                    if field.animal:
                        animal_image = self.animal_images[field.animal.animal_type]
                        # 動物画像をタイルの中央に配置
                        animal_size = min(self.cell_size - 20, animal_image.width())
                        painter.drawPixmap(
                            pos_x + (self.cell_size - animal_size) // 2,
                            pos_y + (self.cell_size - animal_size) // 2,
                            animal_size,
                            animal_size,
                            animal_image
                        )

                        if field.animal.has_product and field.animal.animal_type in [AnimalType.CHICKEN,
                                                                                     AnimalType.COW]:
                            product_image = self.product_images[field.animal.animal_type]
                            product_size = min(self.cell_size // 4, product_image.width())
                            painter.drawPixmap(
                                pos_x + self.cell_size - product_size - 5,  # 右下に配置
                                pos_y + self.cell_size - product_size - 5,
                                product_size,
                                product_size,
                                product_image
                            )

                        # 成長率と状態を表示
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        growth_text = f"{field.animal.growth}%"
                        if field.animal.is_dead:
                            growth_text += " (死亡)"
                            painter.setPen(QColor(255, 0, 0))
                        elif field.animal.can_sell():
                            growth_text += f" (売値: {field.animal.get_sale_price()}円)"
                            painter.setPen(QColor(0, 0, 0))
                        painter.drawText(
                            pos_x,
                            pos_y + self.cell_size - 5,
                            growth_text
                        )
                else:
                    # ロックされたタイル
                    painter.drawPixmap(
                        pos_x,
                        pos_y,
                        self.cell_size,
                        self.cell_size,
                        self.locked_tile_image
                    )
                    # ロック表示
                    painter.drawText(
                        pos_x + self.cell_size // 2 - 10,
                        pos_y + self.cell_size // 2,
                        "🔒"
                    )

    def mousePressEvent(self, event):
        x = int(event.position().x() // self.cell_size)
        y = int((event.position().y() - 100) // self.cell_size)

        if 0 <= x < 3 and 0 <= y < 3:
            field_number = y * 3 + x + 1

            if field_number > self.unlocked_fields:
                self.try_unlock_field()
                return

            field = self.fields[y][x]
            if event.button() == Qt.MouseButton.LeftButton:
                if field.animal is None:
                    # 動物選択ダイアログを表示
                    selected_type = self.show_animal_selection_dialog()
                    if selected_type:
                        purchase_price = selected_type.price
                        if self.money >= purchase_price:
                            field.add_animal(Animal(selected_type))
                            self.money -= purchase_price
                            self.update()
                        else:
                            QMessageBox.warning(self, "購入不可",
                                              f"所持金が足りません！\n必要金額: {purchase_price}円")
            elif event.button() == Qt.MouseButton.RightButton:
                if field.animal:
                    if field.animal.is_dead:
                        self.try_cleanup_dead_animal(field)
                    else:
                        self.try_sell_animal(field)

    def called(self, reviewer, card, ease):
        total_production = 0
        # カードを回答したときの処理
        for row in self.fields:
            for field in row:
                if field.animal:
                    # 動物を成長させる
                    field.animal.grow()
                    # 前回の生産物をリセット
                    field.animal.has_product = False
                    # 新しい生産物を生成
                    production = field.animal.produce()
                    if production > 0:
                        total_production += production

        # 生産による収入を加算
        if total_production > 0:
            self.money += total_production

        self.update()

def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()