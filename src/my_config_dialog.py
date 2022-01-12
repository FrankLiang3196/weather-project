# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    my_config_dialog
@Author:  Jiachen Zhao
@Time:    2021/11/7 19:33
@Description: 
"""

import os, time
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDir, QDate, QDateTime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from src import my_main_window, main_window
from .config_dialog import Ui_setConfig


class ConfigDialog(QDialog, Ui_setConfig):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.inputdir_temp = my_main_window.inputdir
        self.outputdir_temp = my_main_window.outputdir
        self.inputwidth_temp = my_main_window.inputwidth
        self.outputwidth_temp = my_main_window.outputwidth
        self.curdate_temp = my_main_window.curdate

        self.set_Text()
        self.inputdirButton.clicked.connect(self.inputdirButton_Clicked)
        self.outputdirButton.clicked.connect(self.outputdirButton_Clicked)
        self.inputspinBox.valueChanged.connect(self.inputspinBox_Changed)
        self.outputspinBox.valueChanged.connect(self.outputspinBox_Changed)
        self.curdateEdit.dateTimeChanged.connect(self.curtime_Changed)
        self.okButton.clicked.connect(self.okButton_Clicked)
        self.cancelButton.clicked.connect(self.cancelButton_Clicked)

    def set_Format(self):
        self.inputdirEdit.setReadOnly(True)
        self.inputdirEdit.setFont(QFont('Times New Roman', 10, QFont.Black))
        self.inputdirEdit.setAlignment(Qt.AlignCenter)

        self.outputdirEdit.setReadOnly(True)
        self.outputdirEdit.setFont(QFont('Times New Roman', 10, QFont.Black))
        self.outputdirEdit.setAlignment(Qt.AlignCenter)

        self.curdateEdit.setMaximumDate((QDate(2022, 1, 1)))    # 设置系统日期的最大值
        self.curdateEdit.setMinimumDate((QDate(2001, 1, 10)))   # 设置系统时间的最小值
        self.curdateEdit.setAlignment(Qt.AlignCenter)

        self.inputspinBox.setValue(my_main_window.inputwidth)
        self.inputspinBox.setAlignment(Qt.AlignCenter)
        self.inputspinBox.setRange(1, 24)  # 输入序列长度的范围

        self.outputspinBox.setValue(my_main_window.outputwidth)
        self.outputspinBox.setAlignment(Qt.AlignCenter)
        self.outputspinBox.setRange(1, 72)  # 输出序列长度的范围

        self.curdatelabel.setAlignment(Qt.AlignCenter)
        self.inputlabel.setAlignment(Qt.AlignCenter)
        self.outputlabel.setAlignment(Qt.AlignCenter)

        self.curdateEdit.setDisplayFormat("yyyy/MM/dd HH:mm")
        # dateTimeEdit2.setDisplayFormat("yyyy/MM/dd HH-mm-ss")

    def set_Text(self):
        self.setWindowTitle('参数设置')
        self.inputdirEdit.setText(my_main_window.inputdir)
        self.outputdirEdit.setText(my_main_window.outputdir)

        year = int(f'20{my_main_window.curdate[0:2]}')     # 取1-2位数，转为具体年份2020
        month = int(my_main_window.curdate[2:4])
        day = int(my_main_window.curdate[4:6])
        hour = int(my_main_window.curdate[6:8])
        # self.curdateEdit.setDate(QDate(year, month, day))
        self.curdateEdit.setDateTime(QDateTime(year, month, day, hour, 0,0,0))
        self.set_Format()

    def inputdirButton_Clicked(self):
        # inputdir_temp 即为用户选择的输入路径
        inputdir = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "./")
        if inputdir:    # 选择路径不为空
            self.inputdir_temp = inputdir
        else:
            self.inputdir_temp = my_main_window.inputdir

        self.inputdirEdit.setText(self.inputdir_temp)
        self.inputdirEdit.setAlignment(Qt.AlignCenter)

    def outputdirButton_Clicked(self):
        # outputdir 即为用户选择的输出路径
        outputdir = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", "./")
        if outputdir:
            self.outputdir_temp = outputdir
        else:
            self.outputdir_temp = my_main_window.outputdir

        self.outputdirEdit.setText(self.outputdir_temp)
        self.outputdirEdit.setAlignment(Qt.AlignCenter)

    def curtime_Changed(self):
        curdate_temp_ = self.curdateEdit.textFromDateTime(self.curdateEdit.dateTime())
        # print(curdate_temp_)    # 得到日期形式为 2002/1/10 HH:mm
        self.curdate_temp = self.dateTrans(curdate_temp_)
        # print(self.curdate_temp)  # 得到字符串格式 02011000
        my_main_window.curdate = self.curdate_temp  # 更新值

    def inputspinBox_Changed(self):
        self.inputwidth_temp = self.inputspinBox.value()

    def outputspinBox_Changed(self):
        self.outputwidth_temp = self.outputspinBox.value()

    def okButton_Clicked(self):
        my_main_window.inputdir = self.inputdir_temp
        my_main_window.outputdir = self.outputdir_temp
        my_main_window.inputwidth = self.inputwidth_temp
        my_main_window.outputwidth = self.outputwidth_temp
        my_main_window.curdate = self.curdate_temp

        # 有问题
        my_main_window.MainWindow().textChange_Label()  # 实例不统一，改变的不是同一个标签
        # my_main_window.MainWindow.textChange_Label()  # ()中传入mainwindow中创建的实例

        self.close()

    def cancelButton_Clicked(self):
        self.close()

    def dateTrans(self, date):  # 输入为字符串，"2001/01/10 00：00"格式，输出为"20010110" 20年1月1日10时
        # 字符串先转换为时间数组,然后转换为其他格式
        timeStruct = time.strptime(date, "%Y/%m/%d %H:%M")
        date_ = time.strftime("%Y%m%d%H", timeStruct)
        date_ = date_[2:]
        return date_


if __name__ == "__main__":
    print('-----')




