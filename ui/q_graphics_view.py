from xml.etree.ElementPath import prepare_parent
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtWidgets import QGraphicsView, QMenu, QGraphicsSceneContextMenuEvent

class QGraphicsViewClass(QGraphicsView):

    def __init__(self, iface):
        super().__init__() 
        self.iface = iface #MainWindow
        self.select_posX = 0
        self.select_posY = 0

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        try:
            if(self.scene().focusItem() == None):
                mousePoint = QtCore.QPointF(self.mapToScene(event.pos()))
                self.select_posX = mousePoint.x()
                self.select_posY = mousePoint.y()

                add_new_slot_on_position = QtWidgets.QAction("Add new slot here")
                add_new_slot_on_position.triggered.connect(lambda: self.add_new_slot_on_position())
                add_new_slot_on_position.setIcon(QtGui.QIcon("resources/icons/add_slot.png"))
                
                menu = QtWidgets.QMenu()
                menu.addAction(add_new_slot_on_position)
                menu.exec_(event.globalPos())
            else:
                print("Context menu is disable. Your clicked on graphics item.")
        except AttributeError as no_slot_in_page:
            mousePoint = QtCore.QPointF(self.mapToScene(event.pos()))
            self.select_posX = mousePoint.x()
            self.select_posY = mousePoint.y()

            add_new_slot_on_position = QtWidgets.QAction("Add new slot here")
            add_new_slot_on_position.triggered.connect(lambda: self.add_new_slot_on_position())
            add_new_slot_on_position.setIcon(QtGui.QIcon("resources/icons/add_slot.png"))
                
            menu = QtWidgets.QMenu()
            menu.addAction(add_new_slot_on_position)
            menu.exec_(event.globalPos())

    def add_new_slot_on_position(self):
        from ui.new_slot import NewSlot
        NewSlot(self.iface, self.select_posX, self.select_posY, 200, 100)
        self.iface.read_all_slots_from_page()