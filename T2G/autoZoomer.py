from copy import copy

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from qgis.core import QgsRectangle, QgsPoint
from collections import deque
from itertools import chain


class ExtentProvider(QObject):
    extent = QgsRectangle()
    features = deque(maxlen=8)
    ready = pyqtSignal()

    def __init__(self, vertices, canvas, history=1):
        super().__init__()
        self.canvas = canvas
        self.vertices = vertices
        self.history = history
        self.active_mode = self.mode_layer
        self.modes = [self.mode_layer,
                      self.mode_from_last,
                      self.mode_from_last_two,
                      self.mode_from_last_four,
                      self.mode_from_last_eight,
                      ]

    def set_history(self, n):
        self.history = n

    def from_vertices(self, vertices, margin=0.1):
        margin *= .5
        xys = [(vertex.x(), vertex.y()) for vertex in vertices]
        xs, ys = zip(*xys)
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        delta_x = max_x - min_x
        delta_y = max_y - min_y
        x_margin = delta_x * margin
        y_margin = delta_y * margin
        self.extent = QgsRectangle(min_x - x_margin,
                                   min_y - y_margin,
                                   max_x + x_margin,
                                   max_y + y_margin)

    def from_features(self, margin=0.1):
        active_features = list(self.features)[-self.history:]
        vertices = chain(*active_features)
        self.from_vertices(vertices, margin)

    def add_feature(self):
        self.features.append(self.vertices.get_qgs_points())
        self.ready.emit()

    def mode_layer(self):
        self.extent = self.vertices.layer.extent()

    def mode_from_last(self):
        self.history = 1
        self.from_features()

    def mode_from_last_two(self):
        self.history = 2
        self.from_features()

    def mode_from_last_four(self):
        self.history = 4
        self.from_features()

    def mode_from_last_eight(self):
        self.history = 8
        self.from_features()

    def update(self):
        self.active_mode()

    def set_mode(self, cb_index):
        i = cb_index
        self.active_mode = self.modes[i]
        self.modes[i]()

    def reset(self):
        self.features.clear()


class AutoZoomer:
    def __init__(self, canvas, extent_provider, active=True):
        self.canvas = canvas
        self.active = active
        self.extent_provider = extent_provider

    def toggle(self):
        self.active = not self.active

    @pyqtSlot()
    def activate(self):
        self.active = True

    @pyqtSlot()
    def deactivate(self):
        self.active = False

    def set_active(self, active):
        self.active = active

    def apply(self):
        if self.active:
            self.extent_provider.update()
            self.canvas.setExtent(self.extent_provider.extent)
            self.canvas.refresh()


