
#
# ///////////////////////////////////////////////////////////////
from labelme.config import get_config
import sys
import argparse
import os
import platform
from labelme.widgets import Canvas
# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None
config = "dgd"
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

