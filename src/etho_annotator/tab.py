from qtpy import QtGui, QtWidgets, QtCore
import os
import pyqtgraph as pg
from typing import Dict
from . import formbuilder
from .roi import MyEllipseROI, MyPointROI, MyRectROI, MyLedROI, geometries
from .form import yaml, Loader



class FastImageWidget(pg.GraphicsLayoutWidget):
    def __init__(self, *args, useOpenGL=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.useOpenGL(useOpenGL)

        self.pixmapItem = QtWidgets.QGraphicsPixmapItem()
        self.pixmapItem.setShapeMode(QtWidgets.QGraphicsPixmapItem.BoundingRectShape)

        self.viewBox = self.addViewBox()
        self.viewBox.addItem(self.pixmapItem)
        self.viewBox.setAspectLocked(lock=True, ratio=1)
        self.viewBox.setMenuEnabled(False)
        self.viewBox.setMouseEnabled(x=False, y=False)

    def registerMouseClickEvent(self, func):
        self.pixmapItem.mouseClickEvent = func

    def registerMouseDoubleClickEvent(self, func):
        self.pixmapItem.mouseDoubleClickEvent = func

    def setImage(
        self, image, image_format=QtGui.QImage.Format_RGB888, auto_scale: bool = False
    ):
        qimg = QtGui.QImage(image, image.shape[1], image.shape[0], image_format)
        qpix = QtGui.QPixmap(qimg)
        self.pixmapItem.setPixmap(qpix)
        if auto_scale:
            self.fitImage(image.shape[1], image.shape[0])

    def fitImage(self, width: int, height: int):
        self.viewBox.setRange(xRange=(0, width), yRange=(0, height), padding=0)


class BaseAdder(FastImageWidget):
    def __init__(self, image, parent):
        super().__init__()
        self.parent = parent
        self.setImage(image, auto_scale=True)
        self.registerMouseClickEvent(self._mouseClickEvent)
        self.registerMouseDoubleClickEvent(self._mouseDoubleClickEvent)
        self.rois = []

    @property
    def nb_rois(self):
        return len(self.rois)


class FlyAdder(BaseAdder):
    def addROI(self, roi):
        self.viewBox.addItem(roi)
        self.rois.append(roi)
        self.parent.gm.setText(str(self.nb_rois))
        if self.nb_rois > 0:
            self.parent.gm.setReadOnly(True)
            self.parent.gm.setText("")
            self.parent.gm.setPlaceholderText(str(self.nb_rois))

    def removeROI(self, roi):
        self.viewBox.removeItem(roi)
        self.rois.remove(roi)

        if self.nb_rois > 0:
            self.parent.gm.setPlaceholderText(str(self.nb_rois))
        else:
            self.parent.gm.setReadOnly(False)
            self.parent.gm.setText(str(self.nb_rois))

    def _mouseDoubleClickEvent(self, event):
        event.ignore()

    def _mouseClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = (event.pos().x() - 10, event.pos().y() - 10)  # -10 to center new roi
            roi = MyPointROI(pos=pos, size=(20, 20), parent=self)
            self.addROI(roi)
        else:
            event.ignore()


class ChamberAdder(BaseAdder):
    def addROI(self, roi):
        self.viewBox.addItem(roi)
        self.rois.append(roi)

    def removeROI(self, roi):
        self.viewBox.removeItem(roi)
        self.rois.remove(roi)

    def _mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = (event.pos().x(), event.pos().y())  # -10 to center new roi
            idx = [radio.isChecked() for radio in self.parent.gm.radios].index(True)
            size = (200, 200)
            if self.nb_rois > 0:
                size = self.rois[-1].size()

            roi = self.parent.gm.geoms[idx](pos=pos, size=size, angle=0, parent=self)
            self.addROI(roi)
        else:
            event.ignore()

    def _mouseClickEvent(self, event):
        event.ignore()


def createExclusiveGroup():
    groupBox = QtWidgets.QGroupBox("ROI geometry")

    groupBox.radios = [
        QtWidgets.QRadioButton("R&ectangle"),
        QtWidgets.QRadioButton("C&ircle"),
        QtWidgets.QRadioButton("L&ED"),
    ]
    groupBox.geoms = [MyRectROI, MyEllipseROI, MyLedROI]
    groupBox.radios[0].setChecked(True)

    vbox = QtWidgets.QVBoxLayout()
    for radio in groupBox.radios:
        vbox.addWidget(radio)
    vbox.addStretch(1)
    groupBox.setLayout(vbox)
    groupBox.setFlat(True)
    return groupBox


class BaseTab(pg.GraphicsLayoutWidget):
    def serialize(self):
        d = dict()
        d["nb_rois"] = self.mv.nb_rois
        d["positions"] = [list(roi.pos()) for roi in self.mv.rois]
        d["sizes"] = [list(roi.size()) for roi in self.mv.rois]
        d["angles"] = [roi.angle() for roi in self.mv.rois]
        d["geometries"] = [roi.geometry for roi in self.mv.rois]
        d["centers"] = [roi.center for roi in self.mv.rois]
        return d

    def from_dict(self, d: Dict):
        for n in range(d["nb_rois"]):
            roi = geometries[d["geometries"][n]](
                d["positions"][n], d["sizes"][n], d["angles"][n], parent=self
            )
            self.mv.addROI(roi)


class ChambersTab(BaseTab, pg.GraphicsLayoutWidget):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mv = ChamberAdder(image, parent=self)
        self.gm = createExclusiveGroup()
        self.help = QtWidgets.QLabel(
            "<B>Instructions</B><br>"
            "<br>"
            "Add chamber - double click.<br>"
            "<br>"
            "Move chamber - drag.<br>"
            "Delete chamber - right-click.<br>"
            "<br>"
            "Resize chamber - drag green diamonds.<br>"
            "Rotate chamber - drag green circles.<br>"
        )

        self.vb = QtWidgets.QVBoxLayout()
        self.vb.addWidget(self.gm)
        self.vb.addStretch(1)
        self.vb.addWidget(self.help)
        self.vb.addStretch(5)

        self.hb = QtWidgets.QHBoxLayout()
        self.hb.addWidget(self.mv)
        self.hb.addLayout(self.vb)

        self.setLayout(self.hb)


class FlyTab(BaseTab, pg.GraphicsLayoutWidget):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mv = FlyAdder(image, parent=self)
        self.gm = QtWidgets.QLineEdit(placeholderText="0")
        self.help = QtWidgets.QLabel(
            "<B>Instructions</B><br>"
            "<br>"
            "Add animal - single click.<br>"
            "<br>"
            "Move animal - drag.<br>"
            "Delete animal - right-click.<br>"
            "<br>"
            "Or just enter number of animals.<br>"
        )

        self.vb = QtWidgets.QVBoxLayout()
        self.vb.addWidget(QtWidgets.QLabel("<B>Number of animals</B>"))
        self.vb.addWidget(self.gm)
        self.vb.addStretch(1)
        self.vb.addWidget(self.help)
        self.vb.addStretch(5)

        self.hb = QtWidgets.QHBoxLayout()
        self.hb.addWidget(self.mv)
        self.hb.addLayout(self.vb)

        self.setLayout(self.hb)


def make_form(movie_name):
    rootname = movie_name.split("dat")[0][:-1]
    localdir = os.path.dirname(os.path.realpath(__file__))

    yaml_file = os.path.join(localdir, "form_analysis profiles.yaml")
    with open(yaml_file, "r") as form_yaml:
        items_to_create = yaml.load(form_yaml, Loader=Loader)

    # autopopulate list with profiles from folder:
    profile_dir = os.path.join(rootname, "workflow", "analysis_profiles")

    # look in `workflow/analysis profiles` in the folder of the current experiment
    # also include defaults from `snakemake-workflows/analysis profiles` (at least new.yaml)
    profile_names = os.listdir(profile_dir)

    for profile_name in profile_names:
        if profile_name.startswith('.'):
            continue
        profile_path = os.path.join(profile_dir, profile_name)
        # append to pull down options
        items_to_create["main"][0]["options"] += "," + profile_name
        # create sub-form
        with open(profile_path, "r") as form_yaml:
            sub_form = yaml.load(form_yaml, Loader=Loader)
        items_to_create["main"][0][profile_name] = sub_form

    # find a way to specify defaults for each folder - maybe instead of "None",
    # set it to a specified "analysis profiles/default.yaml" if that file exists
    if "default.yaml" in profile_names:
        items_to_create["main"][0]["default"] = "default.yaml"

    form = formbuilder.DictFormWidget(form_dict=items_to_create)
    form.serialize = form.get_form_data
    form.deserialize = form.set_form_data
    return form
