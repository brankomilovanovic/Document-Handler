from PySide2.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QAction, QGraphicsSceneContextMenuEvent, QGraphicsSceneMouseEvent
from PySide2.QtGui import QBrush, QPen, Qt, QPainterPath, QColor, QPainter
from PySide2 import QtGui, QtWidgets, QtCore
from PySide2.QtCore import QRectF, QPointF
import xml.etree.ElementTree as et

from ui.add_text_in_slot import AddTextInSlot

class Slot(QGraphicsRectItem):

    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, iface, slot_id, positionX, positionY, width, height):
        super().__init__()
        self.iface = iface #MainWindow
        self.id = slot_id
        self.positionX = positionX
        self.positionY = positionY
        self.width = float(width)
        self.height = float(height)
        self.positionX_tracking = 0
        self.positionY_tracking = 0
        self.width_tracking = 0
        self.height_tracking = 0
        self.setPos(self.positionX, self.positionY)
        self.setRect(0, 0, self.width, self.height)
        self.blackPen = QPen(Qt.black)
        self.blackPen.setWidth(1)
        
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        
        add_text_in_slot = QAction("Add text in slot")
        add_text_in_slot.triggered.connect(lambda: self.add_text())
        add_text_in_slot.setIcon(QtGui.QIcon("resources/icons/image.png"))

        add_image_in_slot = QAction("Add image in slot")
        add_image_in_slot.triggered.connect(lambda: self.add_image())
        add_image_in_slot.setIcon(QtGui.QIcon("resources/icons/newFileTxt.png"))

        delete_action = QAction("Remove Slot")
        delete_action.triggered.connect(lambda: self.delete_action())
        delete_action.setIcon(QtGui.QIcon("resources/icons/delete_icon.png"))
        
        menu = QtWidgets.QMenu()
        menu.addAction(add_text_in_slot)
        menu.addAction(add_image_in_slot)
        menu.addSeparator()
        menu.addAction(delete_action)
        menu.exec_(event.screenPos())
    
    def add_text(self):
        form = AddTextInSlot(self.iface, self.id, str(None))
        form.exec_()

    def delete_action(self):
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()

        for element in root.iter():
            for child in list(element):
                if child.attrib.get("id") == self.id:
                    element.remove(child)
                    print("Uspesno ste obrisali slot ID: " + self.id)

                    xmldata = et.tostring(root, encoding="unicode")
                    myfile = open(self.iface.file_in_current_directory, "w")
                    myfile.write(xmldata)
                    myfile.close()
                    self.iface.read_all_slots_from_page()
                    self.iface.selected_slot = str(None)
    
    def add_image(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self.iface, "Open image", self.iface.current_open_work_space, "Image Files (*.png *.jpg *.bmp)")
        if not file_name:
            return

        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()
        for element in root.iter():
            for child in list(element):
                if child.attrib.get("id") == self.id:
                    child.set("type", "image")
                    child.text = file_name

        xmldata = et.tostring(root, encoding="unicode")
        myfile = open(self.iface.file_in_current_directory, "w")
        myfile.write(xmldata)
        myfile.close()

        self.iface.read_all_slots_from_page()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handleAt(moveEvent.pos())
            cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.removeHandlesPos()
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(moveEvent)

    def hoverEnterEvent(self, moveEvent):
        self.updateHandlesPos()
        super().hoverEnterEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        self.positionY_tracking = self.pos().y()
        self.positionX_tracking = self.pos().x()
        self.width_tracking = self.width
        self.height_tracking = self.height

        self.iface.selected_slot = self.id
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        if self.scene().collidingItems(self):
            self.setPos(self.positionX_tracking, self.positionY_tracking)
            self.setRect(0, 0, self.width_tracking, self.height_tracking)
        else: 
            self.saveReactValue()
        super().mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()
    
    def saveReactValue(self):
        tree = et.parse(self.iface.file_in_current_directory)
        root = tree.getroot()
        for element in root.iter():
            for child in list(element):
                if child.attrib.get("id") == self.id:
                    child.set("positionX", str(float(self.pos().x())))
                    child.set("positionY", str(float(self.pos().y())))
                    child.set("slot_width", str(float(self.rect().width())))
                    child.set("slot_height", str(float(self.rect().height())))

                    xmldata = et.tostring(root, encoding="unicode")
                    myfile = open(self.iface.file_in_current_directory, "w")
                    myfile.write(xmldata)
                    myfile.close()

                    from ui.open_xml_file import OpenXMLFile
                    OpenXMLFile(self.iface).update_document_viewer_and_list_view()

        print('EMPTY: id: {0}, x: {1}, y: {2}'.format(self.id, self.pos().x(), self.pos().y()))

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

    def removeHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(0,0,0,0)
        self.handles[self.handleTopMiddle] = QRectF(0,0,0,0)
        self.handles[self.handleTopRight] = QRectF(0,0,0,0)
        self.handles[self.handleMiddleLeft] = QRectF(0,0,0,0)
        self.handles[self.handleMiddleRight] = QRectF(0,0,0,0)
        self.handles[self.handleBottomLeft] = QRectF(0,0,0,0)
        self.handles[self.handleBottomMiddle] = QRectF(0,0,0,0)
        self.handles[self.handleBottomRight] = QRectF(0,0,0,0)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:

            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:

            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        self.updateHandlesPos()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.setBrush(QBrush(QtGui.QColor("#F9F9F9")))
        painter.setPen(self.blackPen)
        painter.drawRect(self.rect())

        painter.setRenderHint(QPainter.Antialiasing)
        for handle, rect in self.handles.items():
            if self.handleSelected is None or handle == self.handleSelected:
                painter.drawEllipse(rect)

        