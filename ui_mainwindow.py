# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHeaderView, QLabel, QMainWindow,
    QPlainTextEdit, QPushButton, QSizePolicy, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(713, 496)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutRoot = QVBoxLayout(self.centralwidget)
        self.verticalLayoutRoot.setObjectName(u"verticalLayoutRoot")

        self.splitterMain = QSplitter(self.centralwidget)
        self.splitterMain.setObjectName(u"splitterMain")
        self.splitterMain.setOrientation(Qt.Horizontal)

        self.leftPanel = QWidget(self.splitterMain)
        self.leftPanel.setObjectName(u"leftPanel")
        self.verticalLayoutLeft = QVBoxLayout(self.leftPanel)
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")

        self.pushButtonRefresh = QPushButton(self.leftPanel)
        self.pushButtonRefresh.setObjectName(u"pushButtonRefresh")
        self.verticalLayoutLeft.addWidget(self.pushButtonRefresh)

        self.tableWidgetRules = QTableWidget(self.leftPanel)
        self.tableWidgetRules.setObjectName(u"tableWidgetRules")
        self.verticalLayoutLeft.addWidget(self.tableWidgetRules)

        self.pushButtonAdd = QPushButton(self.leftPanel)
        self.pushButtonAdd.setObjectName(u"pushButtonAdd")
        self.verticalLayoutLeft.addWidget(self.pushButtonAdd)

        self.rightPanel = QWidget(self.splitterMain)
        self.rightPanel.setObjectName(u"rightPanel")
        self.verticalLayoutRight = QVBoxLayout(self.rightPanel)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")

        self.tabWidgetLogs = QTabWidget(self.rightPanel)
        self.tabWidgetLogs.setObjectName(u"tabWidgetLogs")

        self.tabAppLog = QWidget()
        self.tabAppLog.setObjectName(u"tabAppLog")
        self.verticalLayoutTabAppLog = QVBoxLayout(self.tabAppLog)
        self.verticalLayoutTabAppLog.setObjectName(u"verticalLayoutTabAppLog")
        self.plainTextEditAppLog = QPlainTextEdit(self.tabAppLog)
        self.plainTextEditAppLog.setObjectName(u"plainTextEditAppLog")
        self.plainTextEditAppLog.setReadOnly(True)
        self.verticalLayoutTabAppLog.addWidget(self.plainTextEditAppLog)
        self.tabWidgetLogs.addTab(self.tabAppLog, "")

        self.tabCmdLog = QWidget()
        self.tabCmdLog.setObjectName(u"tabCmdLog")
        self.verticalLayoutTabCmdLog = QVBoxLayout(self.tabCmdLog)
        self.verticalLayoutTabCmdLog.setObjectName(u"verticalLayoutTabCmdLog")
        self.plainTextEditCmdLog = QPlainTextEdit(self.tabCmdLog)
        self.plainTextEditCmdLog.setObjectName(u"plainTextEditCmdLog")
        self.plainTextEditCmdLog.setReadOnly(True)
        self.verticalLayoutTabCmdLog.addWidget(self.plainTextEditCmdLog)
        self.tabWidgetLogs.addTab(self.tabCmdLog, "")

        self.tabPsLog = QWidget()
        self.tabPsLog.setObjectName(u"tabPsLog")
        self.verticalLayoutTabPsLog = QVBoxLayout(self.tabPsLog)
        self.verticalLayoutTabPsLog.setObjectName(u"verticalLayoutTabPsLog")
        self.plainTextEditPsLog = QPlainTextEdit(self.tabPsLog)
        self.plainTextEditPsLog.setObjectName(u"plainTextEditPsLog")
        self.plainTextEditPsLog.setReadOnly(True)
        self.verticalLayoutTabPsLog.addWidget(self.plainTextEditPsLog)
        self.tabWidgetLogs.addTab(self.tabPsLog, "")

        self.verticalLayoutRight.addWidget(self.tabWidgetLogs)

        self.verticalLayoutRoot.addWidget(self.splitterMain)

        self.errorLabel = QLabel(self.centralwidget)
        self.errorLabel.setObjectName(u"errorLabel")
        self.verticalLayoutRoot.addWidget(self.errorLabel)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"WSL2 \u7aef\u53e3\u8f6c\u53d1\u7ba1\u7406\u5668", None))
        self.pushButtonRefresh.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.pushButtonAdd.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0\u89c4\u5219", None))
        self.errorLabel.setText("")
        self.tabWidgetLogs.setTabText(self.tabWidgetLogs.indexOf(self.tabAppLog), QCoreApplication.translate("MainWindow", u"\u5e94\u7528\u65e5\u5fd7", None))
        self.tabWidgetLogs.setTabText(self.tabWidgetLogs.indexOf(self.tabCmdLog), QCoreApplication.translate("MainWindow", u"\u547d\u4ee4\u8f93\u51fa", None))
        self.tabWidgetLogs.setTabText(self.tabWidgetLogs.indexOf(self.tabPsLog), QCoreApplication.translate("MainWindow", u"PowerShell", None))
    # retranslateUi