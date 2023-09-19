import sys
from qtpy import QtWidgets
import pyqtgraph as pg
import logging
import yaml
import os
from videoreader import VideoReader
import rich
from typing import Dict, Any
from .tab import FlyTab, ChambersTab, make_form
from . import form


logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)

pg.setConfigOptions(background=None)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, image, movie_name):
        super().__init__()

        self.image = image
        self.movie_name = movie_name

        self.button_reset = QtWidgets.QPushButton("R&eset")
        self.button_reset.clicked.connect(self.reset)
        self.button_save = QtWidgets.QPushButton("S&ave and Exit")
        self.button_save.clicked.connect(self.save)
        self.button_exit = QtWidgets.QPushButton("Ex&it")
        self.button_exit.clicked.connect(self.exit)

        self.hl = QtWidgets.QHBoxLayout()
        self.hl.addWidget(self.button_reset)
        self.hl.addWidget(self.button_save)
        self.hl.addWidget(self.button_exit)

        self.tabs = [
            ChambersTab(self.image),
            FlyTab(self.image),
            make_form(self.movie_name),
        ]
        self.tab_names = ["Chambers", "Animals", "Jobs"]

        self.load()

        self.tb = QtWidgets.QTabWidget()
        for tab, tab_name in zip(self.tabs, self.tab_names):
            self.tb.addTab(tab, tab_name)

        self.vl = QtWidgets.QVBoxLayout()
        self.vl.addWidget(self.tb)
        self.vl.addLayout(self.hl)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.vl)

        self.setCentralWidget(self.widget)

    def serialize(self) -> Dict[str, Any]:
        d = dict()
        for tab, tab_name in zip(self.tabs, self.tab_names):
            d[tab_name] = tab.serialize()
        return d

    def reset(self):
        while self.tb.count() > 0:
            self.tb.removeTab(0)

        self.tabs = [
            ChambersTab(self.image),
            FlyTab(self.image),
            make_form(self.movie_name),
        ]
        self.tab_names = ["Chambers", "Animals", "Jobs"]

        for tab, tab_name in zip(self.tabs, self.tab_names):
            self.tb.addTab(tab, tab_name)

    def save(self):
        data = self.serialize()
        data["Jobs"] = dict(form.dot_keys_to_nested(data["Jobs"]))
        rich.print(data)

        filename = os.path.splitext(movie_name)[0] + "_analysis.yaml"
        logging.info(f"saving to {filename}")
        with open(filename, "w") as f:
            yaml.dump(data, f)

        self.exit()

    def load(self):
        filename = os.path.splitext(movie_name)[0] + "_analysis.yaml"
        if os.path.exists(filename):
            logging.info(f"loading from {filename}")
            with open(filename, "r") as f:
                d = yaml.load(f, Loader=yaml.SafeLoader)

            self.tabs[0].from_dict(d["Chambers"])
            self.tabs[1].from_dict(d["Animals"])
            logging.info("   restoring settings from file:")
            rich.print(d)
            self.tabs[2].set_form_data(form.nested_to_dot_keys(d["Jobs"]))

    def exit(self):
        pg.exit()


app = QtWidgets.QApplication([])

if len(sys.argv) > 1:
    movie_name = sys.argv[1]
else:
    movie_name, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Open Video", ".", "Video Files (*.avi *.mp4)"
    )

vr = VideoReader(movie_name)
frame = vr[0]
logger.info(vr)

main_window = MainWindow(frame, movie_name)
main_window.resize(frame.shape[1] // 2, frame.shape[0] // 2)
main_window.show()
app.exec_()
