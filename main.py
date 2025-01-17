import sys
import os
import ctypes
from PySide6.QtGui import QResizeEvent

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from systemtheme import Window
from game import *


APP_ID = 'masstrix.assettocorasrandomizer.0_1_0' # arbitrary string


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ImageWidget(QLabel):

    def __init__(self):
        super(ImageWidget, self).__init__()
        self._pix = None

    def set_image(self, image: QImage):
        self._pix = QPixmap.fromImage(image)
        self.update_pix()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.update_pix()

    def update_pix(self):
        if self._pix is None:
            return
        w = self.width()
        h = self.height()
        m = max(w, h)
        self.setPixmap(self._pix.scaled(m, m, Qt.KeepAspectRatio, Qt.SmoothTransformation))


class PreviewCard(QWidget):

    def __init__(self):
        super(PreviewCard, self).__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._stats = {}


        layout = QVBoxLayout()
        text_layout = QGridLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0, 0, 0, 0)

        text_layout.setColumnStretch(1, 1)

        self.image_widget = ImageWidget()
        # self.image_widget.setFixedHeight(300)

        self.title_widget = QLabel('This is a title')
        self.title_widget.setObjectName('title')
        self.stat = QLabel('000')

        stats_widget = QWidget()
        stats_widget.setLayout(text_layout)
        stats_widget.setObjectName('info')
        text_layout.addWidget(self.title_widget, 0, 0, 1, 2)
        # text_layout.addWidget(QLabel('Length'), 1, 0, 1, 1)
        # text_layout.addWidget(self.stat, 1, 1, 1, 1)

        layout.addWidget(self.image_widget, stretch=1)
        layout.addWidget(stats_widget)

        self._stats_layout = text_layout

        # layout.addStretch()

    def set_stat(self, stat: str, text: str):
        if stat not in self._stats:
            self._stats[stat] = {
                'label': QLabel(stat),
                'info': QLabel('')
            }
            index = len(self._stats)
            self._stats_layout.addWidget(self._stats[stat]['label'], index, 0)
            self._stats_layout.addWidget(self._stats[stat]['info'], index, 1)

        info: QLabel = self._stats[stat]['info']
        info.setText(str(text))
            
    def set_title(self, text):
        self.title_widget.setText(text)

    def set_image(self, image_path: str):
        if image_path is None:
            return
        image = QImage(image_path)
        image.scaledToHeight(300)
        self.image_widget.set_image(image)


class AppWindow(Window):

    def __init__(self):
        super(AppWindow, self).__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.manager = AsettoCorsaManager()
        self.manager.refresh_cache()

        self.track_preview_card = PreviewCard()
        self.car_preview_card = PreviewCard()

        self._load_stylesheet()

        self.setMinimumSize(700, 500)
        self._construct_ui()

        # Auto pick random on open
        self.pick_random()

    def _load_stylesheet(self):
        # Load stylesheet
        file = resource_path('assets/style.css')
        style = ''
        with open(file, 'r') as f:
            style = f.read()
        self.setStyleSheet(style)

    def _construct_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        randomize_btn = QPushButton('Random')
        randomize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        style_reload_btn = QPushButton('Reload Stylesheet')
        style_reload_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Make previews
        previews = QHBoxLayout()
        previews.addWidget(self.track_preview_card)
        previews.addWidget(self.car_preview_card)

        randomize_buttons_layout = QHBoxLayout()
        randomize_track_btn = QPushButton('Random Track')
        randomize_track_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        randomize_car_btn = QPushButton('Random Car')
        randomize_car_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        randomize_buttons_layout.addWidget(randomize_track_btn)
        randomize_buttons_layout.addWidget(randomize_car_btn)

        layout.addLayout(previews)
        layout.addLayout(randomize_buttons_layout)
        layout.addWidget(randomize_btn)
        # layout.addWidget(style_reload_btn)

        randomize_btn.clicked.connect(self.pick_random)
        randomize_track_btn.clicked.connect(self.random_track)
        randomize_car_btn.clicked.connect(self.random_car)
        style_reload_btn.clicked.connect(self._load_stylesheet)

    def random_car(self):
        # Load car info
        car = self.manager.pick_random_car()
        self.car_preview_card.set_title(car.name)

        car_skin: CarSkin = car.random_skin()
        if car_skin:
            self.car_preview_card.set_image(car_skin.preview_image)
        else:
            self.car_preview_card.set_image(None)
        self.car_preview_card.set_stat('Brand', car.brand)
        self.car_preview_card.set_stat('Class', car.catagory)
        self.car_preview_card.set_stat('Power', 'Undefined' if car.bhp == 0 else car.bhp)
        self.car_preview_card.set_stat('Weight', 'Undefined' if car.weight == 0 else car.weight)

    def random_track(self):
        # Load track info
        track = self.manager.pick_random_track()
        self.track_preview_card.set_title(track.name)
        self.track_preview_card.set_image(track.outline_file)
        self.track_preview_card.set_stat('Length', f'{track.length_km}km')
        self.track_preview_card.set_stat('Country', track.country)
        self.track_preview_card.set_stat('City', track.city)
        self.track_preview_card.set_stat('Direction', track.direction)

    def pick_random(self):
        self.random_car()
        self.random_track()

def main():
    print('Starting app')
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QApplication(sys.argv)
    app.setApplicationDisplayName('Assetto Corsa Randomizer')

    # Set the windows icon
    icon = QPixmap(QImage(resource_path('assets/images/logo.ico')))
    app.setWindowIcon(icon)

    # Create the app window
    app_window = AppWindow()
    app_window.show()

    # Boot application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()