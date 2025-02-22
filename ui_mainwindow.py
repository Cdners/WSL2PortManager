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
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(713, 496)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButtonRefresh = QPushButton(self.centralwidget)
        self.pushButtonRefresh.setObjectName(u"pushButtonRefresh")

        self.verticalLayout.addWidget(self.pushButtonRefresh)

        self.tableWidgetRules = QTableWidget(self.centralwidget)
        self.tableWidgetRules.setObjectName(u"tableWidgetRules")

        self.verticalLayout.addWidget(self.tableWidgetRules)

        self.pushButtonAdd = QPushButton(self.centralwidget)
        self.pushButtonAdd.setObjectName(u"pushButtonAdd")

        self.verticalLayout.addWidget(self.pushButtonAdd)

        self.errorLabel = QLabel(self.centralwidget)
        self.errorLabel.setObjectName(u"errorLabel")

        self.verticalLayout.addWidget(self.errorLabel)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"WSL2 \u7aef\u53e3\u8f6c\u53d1\u7ba1\u7406\u5668", None))
        self.pushButtonRefresh.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0", None))
        self.pushButtonAdd.setText(QCoreApplication.translate("MainWindow", u"\u6dfb\u52a0\u89c4\u5219", None))
        self.errorLabel.setText("")
    # retranslateUi