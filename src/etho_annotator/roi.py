import pyqtgraph as pg
import numpy as np


class ROI(pg.graphicsItems.ROI.ROI):
    def __init__(self, pos, size, angle=0, parent=None, **args):
        super().__init__(
            pos, size=size, angle=angle, removable=True, snapSize=1, scaleSnap=1, translateSnap=(1, 1), invertible=True, **args
        )
        self.parent = parent
        self.sigRemoveRequested.connect(self.remove)

    def remove(self):
        self.parent.removeROI(self)

    def mouseClickEvent(self, event):
        if event.button() == 2:
            self.remove()
            event.accept()  # accept so we remove one overlapping roi at a time

    @property
    def center(self):
        # get props
        pos = np.array(self.pos())
        size = np.array(self.size())
        angle = np.array(self.angle())

        # need to half the size and rotate to get the center
        theta = (angle / 180.0) * np.pi
        rotMatrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

        center = (pos + np.dot(rotMatrix, size // 2)).tolist()
        return center


class MyRectROI(ROI):
    geometry = "rectangle"

    def __init__(self, pos, size, angle=0, parent=None, **kwargs):
        super().__init__(
            pos,
            size,
            angle,
            parent,
            pen=pg.mkPen(color="r", width=4.0),
            hoverPen=pg.mkPen(color="r", width=4.0),
            handlePen=pg.mkPen(width=6, color="#40A010"),
            handleHoverPen=pg.mkPen(width=6, color="#40A010"),
            **kwargs
        )
        self._addHandles()

    def _addHandles(self):
        self.addScaleHandle([1, 1], [0, 0])
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 0], [0, 1])
        self.addScaleHandle([0, 1], [1, 0])

        self.addRotateHandle([1, 0.5], [0.5, 0.5])

        for handle in self.handles:
            handle["item"].pen = self.handlePen
            handle["item"].currentPen = self.handlePen


class MyEllipseROI(ROI, pg.graphicsItems.ROI.EllipseROI):
    geometry = "ellipse"

    def __init__(self, pos, size, angle=0, parent=None, **kwargs):
        super().__init__(
            pos,
            size,
            angle,
            parent,
            pen=pg.mkPen(color="r", width=4.0),
            hoverPen=pg.mkPen(color="r", width=4.0),
            handlePen=pg.mkPen(width=6, color="#40A010"),
            handleHoverPen=pg.mkPen(width=6, color="#40A010"),
            **kwargs
        )

    def _addHandles(self):
        self.addRotateHandle([1.0, 0.5], [0.5, 0.5])
        # self.addScaleHandle([0.5 * 2.0**-0.5 + 0.5, 0.5 * 2.0**-0.5 - 0.25], [0, 1])
        # self.addScaleHandle([0.5 * 2.0**-0.5 - 0.25, 0.5 * 2.0**-0.5 + 0.5], [1, 0])
        self.addScaleHandle([0.5 * 2.0**-0.5 + 0.5, 0.5 * 2.0**-0.5 + 0.5], [0.5, 0.5])

        for handle in self.handles:
            handle["item"].pen = self.handlePen
            handle["item"].currentPen = self.handlePen


class MyLedROI(MyEllipseROI):
    geometry = "led"


class MyPointROI(ROI, pg.graphicsItems.ROI.CircleROI):
    geometry = "point"

    def __init__(self, pos, size, angle=0, parent=None, **args):
        super().__init__(
            pos, size, angle, parent, pen=pg.mkPen(color="r", width=4.0), hoverPen=pg.mkPen(color="r", width=4.0), **args
        )
        self.sigRemoveRequested.connect(self.remove)

    def _addHandles(self):
        pass  # prevents addition of non-removable resize handle


geometries = {r.geometry: r for r in [MyRectROI, MyEllipseROI, MyLedROI, MyPointROI]}
