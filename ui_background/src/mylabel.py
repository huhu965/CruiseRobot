from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen

class MyLabel(QLabel):
    x = 0
    y = 0
    # change_flag = False
    # param = []
    def receive_param(self, x, y):
        self.x = x
        self.y = y
        self.update()
    # def receive_position(self,param):
    #     self.param = param
    #     self.change_flag = True
    #     self.update()
    #绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        rect =QRect(self.x, self.y, 10, 5)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red,2,Qt.SolidLine))
        painter.drawRect(rect)
        # if self.change_flag:
        #     for pos in self.param:
        #         rect =QRect(pos['x'], pos['y'], 2, 2)
        #         painter = QPainter(self)
        #         painter.setPen(QPen(Qt.yellow,2,Qt.SolidLine))
        #         painter.drawRect(rect)
