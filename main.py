# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    main
@Author:  Jiachen Zhao
@Time:    2021/11/7 18:25
@Description: 
"""
# this is a test message

import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from src.my_main_window import MainWindow
# from src.my_config_dialog import ConfigDialog


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('AQI Forecast')
    app.setWindowIcon(QIcon('./other_files/icon.jpeg'))  # ios系统下显示图标
    main_window = MainWindow()
    # config_diaglog = ConfigDialog()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()




