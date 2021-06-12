
#
# ///////////////////////////////////////////////////////////////
from labelme.config import get_config
import sys
import argparse
import codecs
import logging
import os
import os.path as osp
import sys
import yaml
import os
import platform
from labelme.widgets import Canvas
from labelme.widgets import ZoomWidget
from labelme import utils
# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None
#config = "dgd"
class MainWindow(QMainWindow):
    FIT_WINDOW , FIT_WIDTH , MANUAL_ZOOM = 0 , 1 , 2

    def __init__(self, default_filename=None, default_prefdef_class_file=None, default_save_dir=None):


        QMainWindow.__init__(self)
        #super(MainWindow , self).__init__()
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        self.fct = UIFunctions
        self.filename = "TOOL"



        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        self.title = "Semi-automatic Labeling Tool"
        description = "Semi-automatic Labeling Tool using Ai"
        # APPLY TEXTS
        self.setWindowTitle(self.title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#??????????????????????????????????????????????------------------------------------
        self.labelList = LabelListWidget()
        self.lastOpenDir = None

        config = get_config()
        self._config = config
        self.dirty = False
        self.output_dir = None

        self.image = QImage()

        self.zoom_values = {}

        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow ,
            self.FIT_WIDTH: self.scaleFitWidth ,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1 ,
        }



        self.canvas = self.labelList.canvas = Canvas(
            epsilon = self._config["epsilon"] ,
            double_click = self._config["canvas"]["double_click"] ,
            #            num_backups = self._config["canvas"]["num_backups"] ,
        )

        self.canvas.zoomRequest.connect(self.fct.zoomRequest)

        # scrollArea = QtWidgets.QScrollArea()
        # scrollArea.setWidget(self.canvas)
        # scrollArea.setWidgetResizable(True)
        # self.scrollBars = {
        #     Qt.Vertical: scrollArea.verticalScrollBar() ,
        #     Qt.Horizontal: scrollArea.horizontalScrollBar() ,
        # }
 #       self.canvas.scrollRequest.connect(self.fct.scrollRequest)

        self.canvas.newShape.connect(self.fct.newShape)
        self.canvas.shapeMoved.connect(self.fct.setDirty)
        self.canvas.selectionChanged.connect(self.fct.shapeSelectionChanged)
        self.canvas.drawingPolygon.connect(self.fct.toggleDrawingSensitive)

#        self.setCentralWidget(scrollArea)

        self.zoomMode = self.FIT_WINDOW
        self.zoomWidget = ZoomWidget()



#        print(self.fct.scaleFitWindow(self))

#        self.canvas.edgeSelected.connect(self.fct.canvasShapeEdgeSelected)
        self.canvas.vertexSelected.connect(widgets.btn_deletePoint.setEnabled)

        self.image = QtGui.QImage()
        self.imagePath = None
        self.recentFiles = []
        self.maxRecent = 7
        self.otherData = None
        self.zoom_level = 100
        self.fit_window = False
        self.zoom_values = {}  # key=filename, value=(zoom_mode, zoom_value)
        self.brightnessContrast_values = {}
        self.scroll_values = {
            Qt.Horizontal: {} ,
            Qt.Vertical: {} ,
        }  # key=filename, value=scroll_value






#???????????????????????????????????????????????---------------------------------------
        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_open.clicked.connect(lambda x: UIFunctions.openDirDialog(self))
        widgets.btn_next.clicked.connect(self.buttonClick)
        widgets.btn_prev.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.btn_delete.clicked.connect(self.buttonClick)
        widgets.btn_polygons.clicked.connect(self.buttonClick)
        widgets.btn_edit.clicked.connect(self.buttonClick)
        widgets.btn_deletePoint.clicked.connect(self.buttonClick)
        widgets.btn_undo.clicked.connect(self.buttonClick)
        widgets.btn_redo.clicked.connect(self.buttonClick)





        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.toggleLeftBox.clicked.connect(self.buttonClick)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)
        widgets.settingsTopBtn.clicked.connect(self.buttonClick)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_dark.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))


    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_open":
            widgets.btn_open.clicked.connect(lambda: UIFunctions.openDirDialog(self))
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     app.setWindowIcon(QIcon("icon.ico"))
#     window = MainWindow()
#     sys.exit(app.exec_())

#----------------------------------------------------------------
    def zoomRequest (self , delta , pos):
        canvas_width_old = self.canvas.width()
        units = 1.1
        if delta < 0:
            units = 0.9
        self.addZoom(units)

        canvas_width_new = self.canvas.width()
        if canvas_width_old != canvas_width_new:
            canvas_scale_factor = canvas_width_new/canvas_width_old

            x_shift = round(pos.x()*canvas_scale_factor) - pos.x()
            y_shift = round(pos.y()*canvas_scale_factor) - pos.y()

            self.setScroll(
                Qt.Horizontal ,
                self.scrollBars[Qt.Horizontal].value() + x_shift ,
            )
            self.setScroll(
                Qt.Vertical ,
                self.scrollBars[Qt.Vertical].value() + y_shift ,
            )


    def scrollRequest (self , delta , orientation):
        units = -delta*0.1  # natural scroll
        bar = self.scrollBars[orientation]
        value = bar.value() + bar.singleStep()*units
        self.setScroll(orientation , value)


    def newShape (self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        items = self.uniqLabelList.selectedItems()
        text = None
        if items:
            text = items[0].data(Qt.UserRole)
        flags = {}
        group_id = None
        if self._config["display_label_popup"] or not text:
            previous_text = self.labelDialog.edit.text()
            text , flags , group_id = self.labelDialog.popUp(text)
            if not text:
                self.labelDialog.edit.setText(previous_text)

        if text and not self.validateLabel(text):
            self.errorMessage(
                self.tr("Invalid label") ,
                self.tr("Invalid label '{}' with validation type '{}'").format(
                    text , self._config["validate_label"]
                ) ,
            )
            text = ""
        if text:
            self.labelList.clearSelection()
            shape = self.canvas.setLastLabel(text , flags)
            shape.group_id = group_id
            self.addLabel(shape)
            self.actions.editMode.setEnabled(True)
            self.actions.undoLastPoint.setEnabled(False)
            self.actions.undo.setEnabled(True)
            self.setDirty()
        else:
            self.canvas.undoLastLine()
            self.canvas.shapesBackups.pop()


    def toggleDrawingSensitive (self , drawing=True):
        """Toggle drawing sensitive.

        In the middle of drawing, toggling between modes should be disabled.
        """
        self.actions.editMode.setEnabled(not drawing)
        self.actions.undoLastPoint.setEnabled(drawing)
        self.actions.undo.setEnabled(not drawing)
        self.actions.delete.setEnabled(not drawing)


    def removeSelectedPoint (self):
        self.canvas.removeSelectedPoint()
        if not self.canvas.hShape.points:
            self.canvas.deleteShape(self.canvas.hShape)
            self.remLabels([self.canvas.hShape])
            self.setDirty()
            if self.noShapes():
                for action in self.actions.onShapesPresent:
                    action.setEnabled(False)


    def shapeSelectionChanged (self , selected_shapes):
        self._noSelectionSlot = True
        for shape in self.canvas.selectedShapes:
            shape.selected = False
        self.labelList.clearSelection()
        self.canvas.selectedShapes = selected_shapes
        for shape in self.canvas.selectedShapes:
            shape.selected = True
            item = self.labelList.findItemByShape(shape)
            self.labelList.selectItem(item)
            self.labelList.scrollToItem(item)
        self._noSelectionSlot = False
        n_selected = len(selected_shapes)
        self.actions.delete.setEnabled(n_selected)
        self.actions.copy.setEnabled(n_selected)
        self.actions.edit.setEnabled(n_selected == 1)


    def canvasShapeEdgeSelected (self , selected , shape):
        self.actions.addPointToEdge.setEnabled(
            selected and shape and shape.canAddPoint()
        )


    def mayContinue (self):
        if not self.dirty:
            return True
        mb = QtWidgets.QMessageBox
        msg = self.tr('Save annotations to "{}" before closing?').format(
            self.filename
        )
        answer = mb.question(
            self ,
            self.tr("Save annotations?") ,
            msg ,
            mb.Save | mb.Discard | mb.Cancel ,
            mb.Save ,
        )
        if answer == mb.Discard:
            return True
        elif answer == mb.Save:
            self.fct.saveFile(self)
            return True
        else:  # answer == mb.Cancel
            return False


    def openDirDialog (self , _value=False , dirpath=None):
        if not self.mayContinue():
            return

        defaultOpenDirPath = dirpath if dirpath else "."
        if self.lastOpenDir and osp.exists(self.lastOpenDir):
            defaultOpenDirPath = self.lastOpenDir
        else:
            defaultOpenDirPath = (
                osp.dirname(self.filename) if self.filename else "."
            )

        targetDirPath = QFileDialog().getExistingDirectory()
        self.importDirImages(targetDirPath)


    def importDirImages (self , dirpath , pattern=None , load=True):
        # self.actions.openNextImg.setEnabled(True)
        # self.actions.openPrevImg.setEnabled(True)

        if not self.mayContinue() or not dirpath:
            return

        self.lastOpenDir = dirpath
        self.filename = None
        self.ui.fileListWidget.clear()
        for filename in self.scanAllImages( dirpath):
            if pattern and pattern not in filename:
                continue
            label_file = osp.splitext(filename)[0] + ".json"
            if self.output_dir:
                label_file_without_path = osp.basename(label_file)
                label_file = osp.join(self.output_dir , label_file_without_path)
            item = QtWidgets.QListWidgetItem(filename)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            if QtCore.QFile.exists(label_file) and LabelFile.is_label_file(
                    label_file
            ):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.fileListWidget.addItem(item)
        self.openNextImg( load = load)

        # @property


    def imageList (self):
        lst = []
        for i in range(self.ui.fileListWidget.count()):
            item = self.ui.fileListWidget.item(i)
            lst.append(item.text())
        return lst


    def openNextImg (self , _value=False , load=True):
        # keep_prev = self._config["keep_prev"]
        if Qt.KeyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self._config["keep_prev"] = True

        if not self.mayContinue():
            return

        if len(self.imageList()) <= 0:
            return

        filename = None
        if self.filename is None:
            filename = self.imageList()[0]
        else:
            currIndex = self.imageList.index(self.filename)
            if currIndex + 1 < len(self.imageList):
                filename = self.imageList[currIndex + 1]
            else:
                filename = self.imageList[-1]
        self.filename = filename

        if self.filename and load:
            self.loadFile( self.filename)
        # self._config["keep_prev"] = keep_prev


    def loadFile (self , filename=None):
        """Load the specified file, or the last opened file if None."""
        # changing fileListWidget loads file

        if filename in self.imageList() and (
                self.ui.fileListWidget.currentRow() != self.imageList().index(filename)
        ):
            print("faila e v lista")
            self.ui.fileListWidget.setCurrentRow(self.imageList().index(filename))
            self.ui.fileListWidget.repaint()
        # return

        self.resetState()

        print(filename)

        self.canvas.setEnabled(False)
        if filename is None:
            filename = self.settings.value("filename" , "")
        filename = str(filename)
        if not QtCore.QFile.exists(filename):
            self.errorMessage(
                self.tr("Error opening file") ,
                self.tr("No such file: <b>%s</b>")%filename ,
            )
            return False
        # assumes same name, but json extension
        self.status( self.tr("Loading %s...")%osp.basename(str(filename)))

        label_file = osp.splitext(filename)[0] + ".json"
        if self.output_dir:
            label_file_without_path = osp.basename(label_file)
            label_file = osp.join(self.output_dir , label_file_without_path)

        if QtCore.QFile.exists(label_file) and LabelFile.is_label_file(
                label_file
        ):
            try:
                self.labelFile = LabelFile(label_file)

            except LabelFileError as e:
                self.errorMessage(
                    self.tr("Error opening file") ,
                    self.tr(
                        "<p><b>%s</b></p>"
                        "<p>Make sure <i>%s</i> is a valid label file."
                    )
                    %(e , label_file) ,
                )
                self.status(self.tr("Error reading %s")%label_file)
                return False
            self.imageData = self.labelFile.imageData
            self.imagePath = osp.join(
                osp.dirname(label_file) ,
                self.labelFile.imagePath ,
            )
            self.otherData = self.labelFile.otherData
        else:
            self.imageData = LabelFile.load_image_file(filename)
            if self.imageData:
                self.imagePath = filename
            self.labelFile = None
        image = QtGui.QImage.fromData(self.imageData)

        if image.isNull():
            formats = [
                "*.{}".format(fmt.data().decode())
                for fmt in QtGui.QImageReader.supportedImageFormats()
            ]
            self.fct.errorMessage(self ,
                                  self.tr("Error opening file") ,
                                  self.tr(
                                      "<p>Make sure <i>{0}</i> is a valid image file.<br/>"
                                      "Supported image formats: {1}</p>"
                                  ).format(filename , ",".join(formats)) ,
                                  )
            self.status(self.tr("Error reading %s")%filename)
            return False
        self.image = image
        self.filename = filename
        if self._config["keep_prev"]:
            prev_shapes = self.canvas.shapes
        self.canvas.loadPixmap(QtGui.QPixmap.fromImage(image))
        flags = {k: False for k in self._config["flags"] or []}
        if self.labelFile:
            self.loadLabels(self.labelFile.shapes)
            if self.labelFile.flags is not None:
                flags.update(self.labelFile.flags)

        self.loadFlags(flags)

        if self._config["keep_prev"] and self.noShapes():
            self.loadShapes(prev_shapes , replace = False)
            self.setDirty()

        else:
            self.setClean()
        self.canvas.setEnabled(True)

        # set zoom values
        is_initial_load = not self.zoom_values

        if self.filename in self.zoom_values:
            self.zoomMode = self.zoom_values[self.filename][0]
            self.setZoom(self.zoom_values[self.filename][1])
        elif is_initial_load or not self._config["keep_prev_scale"]:
            self.adjustScale(initial = True)
        # set scroll values
        print("ssssssssssssssssssssssssssssssssssssss")
        for orientation in self.scroll_values:
            if self.filename in self.scroll_values[orientation]:
                self.setScroll(
                    orientation , self.scroll_values[orientation][self.filename]
                )
        # set brightness constrast values
        dialog = BrightnessContrastDialog(
            utils.img_data_to_pil(self.imageData) ,
            self.onNewBrightnessContrast ,
            parent = self ,
        )
        brightness , contrast = self.brightnessContrast_values.get(
            self.filename , (None , None)
        )
        if self._config["keep_prev_brightness"] and self.recentFiles:
            brightness , _ = self.brightnessContrast_values.get(
                self.recentFiles[0] , (None , None)
            )
        if self._config["keep_prev_contrast"] and self.recentFiles:
            _ , contrast = self.brightnessContrast_values.get(
                self.recentFiles[0] , (None , None)
            )
        if brightness is not None:
            dialog.slider_brightness.setValue(brightness)
        if contrast is not None:
            dialog.slider_contrast.setValue(contrast)
        self.brightnessContrast_values[self.filename] = (brightness , contrast)
        if brightness is not None or contrast is not None:
            dialog.onNewValue(None)
        self.paintCanvas()
        self.addRecentFile(self.filename)
        # self.toggleActions(True)
        self.canvas.setFocus()
        self.status(self.tr("Loaded %s")%osp.basename(str(filename)))
        return True


    def status (self , message , delay=5000):
        self.statusBar().showMessage(message , delay)


    def setDirty (self):
        # Even if we autosave the file, we keep the ability to undo
        self.actions.undo.setEnabled(self.canvas.isShapeRestorable)

        if self._config["auto_save"] or self.actions.saveAuto.isChecked():
            label_file = osp.splitext(self.imagePath)[0] + ".json"
            if self.output_dir:
                label_file_without_path = osp.basename(label_file)
                label_file = osp.join(self.output_dir , label_file_without_path)
            self.saveLabels(label_file)
            return
        self.dirty = True
        self.actions.save.setEnabled(True)
        # title = __appname__
        if self.filename is not None:
            title = "{} - {}*".format(self.title , self.filename)
        self.setWindowTitle(title)


    def setClean (self):
        self.dirty = False
        # self.fct.saveFile.setEnabled(False)
        # self.fct.createMode.setEnabled(True)
        # self.fct.createRectangleMode.setEnabled(True)
        # self.fct.createCircleMode.setEnabled(True)
        # self.fct.createLineMode.setEnabled(True)
        # self.fct.createPointMode.setEnabled(True)
        # self.fct.createLineStripMode.setEnabled(True)
        title = self.title
        if self.filename is not None:
            title = "{} - {}".format(title , self.filename)
        self.setWindowTitle(title)

        # if self.hasLabelFile():
        #     self.actions.deleteFile.setEnabled(True)
        # else:
        #     self.actions.deleteFile.setEnabled(False)


    def resetState (self):
        # self.labelList.clear()
        self.filename = None
        self.imagePath = None
        self.imageData = None
        self.labelFile = None
        self.otherData = None
        self.canvas.resetState()


    def openPrevImg (self , _value=False):
        keep_prev = self._config["keep_prev"]
        if Qt.KeyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self._config["keep_prev"] = True

        if not self.fct.mayContinue(self):
            return

        if len(self.imageList) <= 0:
            return

        if self.filename is None:
            return

        currIndex = self.imageList.index(self.filename)
        if currIndex - 1 >= 0:
            filename = self.imageList[currIndex - 1]
            if filename:
                self.fct.loadFile(self , filename)

        self._config["keep_prev"] = keep_prev


    def scanAllImages (self , folderPath):
        extensions = [
            ".%s"%fmt.data().decode().lower()
            for fmt in QImageReader.supportedImageFormats()
        ]

        images = []
        for root , dirs , files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = osp.join(root , file)
                    images.append(relativePath)
        images.sort(key = lambda x: x.lower())
        return images


    def loadFlags (self , flags):
        self.ui.flagWidget.clear()
        for key , flag in flags.items():
            item = QtWidgets.QListWidgetItem(key)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if flag else Qt.Unchecked)
            self.ui.flagWidget.addItem(item)


    def saveFile (self , _value=False):
        assert not self.image.isNull() , "cannot save empty image"
        if self.labelFile:
            # DL20180323 - overwrite when in directory
            self.fct._saveFile(self.labelFile.filename)
        elif self.output_file:
            self.fct._saveFile(self.output_file)
            self.close()
        else:
            self._saveFile(self.saveFileDialog())


    def _saveFile (self , filename):
        if filename and self.saveLabels(filename):
            self.addRecentFile(filename)
            self.setClean()


    def errorMessage (self , title , message):
        return QtWidgets.QMessageBox.critical(
            self , title , "<p><b>%s</b></p>%s"%(title , message)
        )


    def setZoom (self , value):
        # self.actions.fitWidth.setChecked(False)
        # self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(value)
        self.zoom_values[self.filename] = (self.zoomMode , value)


    def adjustScale (self , initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
        value = int(100*value)
        self.zoomWidget.setValue(value)
        self.zoom_values[self.filename] = (self.zoomMode , value)


    def scaleFitWindow (self):
        """Figure out the size of the pixmap to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        print(w1)

        h1 = self.centralWidget().height() - e
        print(h1)
        a1 = w1/h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        print(w2)
        h2 = self.canvas.pixmap.height() - 0.0
        print(h2)
        a2 = w2/h2
        return w1/w2 if a2 >= a1 else h1/h2


    def scaleFitWidth (self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w/self.canvas.pixmap.width()

    def onNewBrightnessContrast (self , qimage):
        self.canvas.loadPixmap(
            QtGui.QPixmap.fromImage(qimage) , clear_shapes = False
        )

    def paintCanvas (self):
        assert not self.image.isNull() , "cannot paint null image"
        self.canvas.scale = 0.01*self.zoomWidget.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def addRecentFile (self , filename):
        if filename in self.recentFiles:
            self.recentFiles.remove(filename)
        elif len(self.recentFiles) >= self.maxRecent:
            self.recentFiles.pop()
        self.recentFiles.insert(0 , filename)

    # def toggleActions(self, value=True):
    #     """Enable/Disable widgets which depend on an opened image."""
    #     for z in self.actions.zoomActions:
    #         z.setEnabled(value)
    #     for action in self.actions.onLoadActive:
    #         action.setEnabled(value)


#----------------------------------------------------------------


def get_main_app (argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    app.setWindowIcon(QIcon("icon.ico"))

    argparser = argparse.ArgumentParser()
    argparser.add_argument("image_dir" , nargs = "?")
    argparser.add_argument("predefined_classes_file" ,
                           default = os.path.join(os.path.dirname(__file__) , "data" , "predefined_classes.txt") ,
                           nargs = "?")
    argparser.add_argument("save_dir" , nargs = "?")
    args = argparser.parse_args(argv[1:])
    # Usage : labelImg.py image predefClassFile saveDir
    win = MainWindow(args.image_dir ,
                     args.predefined_classes_file ,
                     args.save_dir)
    win.show()
    return app , win


def main ():
    """construct main app and run it"""
    app , _win = get_main_app(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())

