'''
Created on Sep 8, 2015

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
import os.path as osp
import qtify_maya_window as qtfy
import appUsageApp
reload(appUsageApp)
import msgBox
from backend import utilities as utils
reload(utils)
from backend import redshift
reload(redshift)

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')
icon_path = osp.join(root_path, 'icons')

title = 'Matte IDs'
obj_id_text = 'Object IDs'
mtl_id_text = 'Material IDs'

Form, Base = uic.loadUiType(osp.join(ui_path, 'ui.ui'))
class UI(Form, Base):
    _previousPath = ''
    _playlist = None
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch) 
        self.listWidgets = []
        
        self.populate()
        
        self.refreshButton.clicked.connect(self.populate)
        self.tableWidget.dropEvent = self.tableDropEvent
        self.switchButton.clicked.connect(self.switchView)
        self.addButton.clicked.connect(self.addSelection)
        
        appUsageApp.updateDatabase('matteIds')
        
    def addSelection(self):
        currentItems = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
        if self.getIdMode() == obj_id_text:
            currentItems.extend(utils.getSelectedMeshes())
            utils.addMeshesToSet(currentItems)
        else:
            currentItems.extend(redshift.getSelectedMtls())
            redshift.addMtlsToSet(currentItems)
        currentItems = list(set(currentItems))
        self.listWidget.clear()
        print currentItems
        self.listWidget.addItems(currentItems)
        self.populate()
        
    def switchView(self):
        text = self.switchButton.text()
        if text == obj_id_text:
            self.switchButton.setText(mtl_id_text)
            self.populate()
        else:
            self.switchButton.setText(obj_id_text)
            self.populate()

    def closeEvent(self, event):
        self.deleteLater()

    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title=title, **kwargs)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.removeSelected()
            
    def removeSelected(self):
        for widget in self.listWidgets:
            selected = widget.selectedItems()
            if selected:
                selected_texts = [i.text() for i in selected]
                try:
                    if self.getIdMode() == obj_id_text:
                        for obj in selected_texts:
                            redshift.removeObjectId(obj)
                    else:
                        for mtl in selected_texts:
                            redshift.removeMtlId(mtl)
                except Exception as ex:
                    self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
                    return
                for item in selected:
                    i = widget.takeItem(widget.row(item))
                    self.listWidget.addItem(i.text())
    
    def tableDropEvent(self, event):
        items = self.listWidget.selectedItems()
        row = self.tableWidget.rowAt(event.pos().y())
        col = self.tableWidget.columnAt(event.pos().x())
        aov = self.tableWidget.item(row, 0).text()
        widget = self.tableWidget.cellWidget(row, col)
        if items:
            item_texts = [i.text() for i in items]
            try:
                if self.getIdMode() == obj_id_text:
                    for text in item_texts:
                        redshift.addObjectId(aov, text, col)
                else:
                    for text in item_texts:
                        redshift.addMtlId(aov, text, col)
            except Exception as ex:
                self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
                return
            widget.addItems(item_texts)
            for item in items:
                self.listWidget.takeItem(self.listWidget.row(item))
        val = self.tableWidget.verticalScrollBar().value()
        m = self.tableWidget.verticalScrollBar().maximum()
        self.populate()
        self.tableWidget.verticalScrollBar().setMaximum(m)
        self.tableWidget.verticalScrollBar().setValue(val)
                        
        
    
    def getIdMode(self):
        return self.switchButton.text()

    def insertRow(self, aov):
        numRows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(numRows)
        if self.getIdMode() == obj_id_text:
            items = redshift.getMeshesFromAOV(aov)
        else:
            items = redshift.getMtlsFromAOV(aov)
        itm = QTableWidgetItem(aov.name())
        itm.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(numRows, 0, itm)
        for key, values in items.items():
            if key == 'redId': col = 1
            if key == 'greenId': col = 2
            if key == 'blueId': col = 3
            self.insertItem(values, numRows, col)
    
    def insertItem(self, items, row, col):
        widget = QListWidget(self)
        #widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget.setMaximumHeight(60)
        self.listWidgets.append(widget)
        for text in items:
            item = QListWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            widget.addItem(item)
        self.tableWidget.setCellWidget(row, col, widget)

    def populate(self):
        for widget in self.listWidgets:
            widget.deleteLater()
        del self.listWidgets[:]
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.listWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels(['AOVs', 'Red ID', 'Green ID', 'Blue ID'])
        if self.getIdMode() == obj_id_text:
            aovs = redshift.getAOVs(obj=True)
            self.listWidget.addItems(redshift.getUnassignedMeshes())
        else:
            aovs = redshift.getAOVs(mtl=True)
            self.listWidget.addItems(redshift.getUnassignedMaterials())
        for aov in aovs:
            self.insertRow(aov)
        if self.listWidgets:
            map(lambda widget: widget.itemClicked.connect(lambda: self.handleItemClick(widget)), self.listWidgets)
        self.tableWidget.resizeRowsToContents()
            
    def handleItemClick(self, widget):
        for listWidget in self.listWidgets:
            if listWidget != widget:
                for i in range(listWidget.count()):
                    item = listWidget.item(i)
                    listWidget.setItemSelected(item, False)