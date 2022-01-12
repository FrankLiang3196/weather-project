# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    my_main_window
@Author:  Jiachen Zhao
@Time:    2021/11/7 19:31
@Description: 
"""
import io, os, chardet, folium
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from .main_window import Ui_MainWindow
from .my_config_dialog import ConfigDialog

#TODO 需要把重要的参数设置放在yaml文件中，程序关闭前保存
inputdir = os.path.abspath('.')
outputdir = os.path.abspath('.')
inputwidth = 6  # 输入的时间序列长度，单位小时
outputwidth = 48  # 输出的时间序列长度
curdate = '20010210'  # 当前系统时间，字符串类型

select_province = '北京市'
select_id = 54399

root_path = os.path.abspath('.')
map_path = rf'{root_path}\map_files'
figure_path = rf'{root_path}\output_files\Curves'
stationMap_path = rf'{map_path}\StationMap'


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.initUI()
        self.initHeading()
        self.initMenu()
        self.initStatusBar()
        self.initMap()
        self.initcomboBox()

    def initUI(self):
        self.setWindowTitle('AQI Forecast')
        self.setWinCenter()
        self.root_ = os.path.abspath('.')  # 表示当前(my_main_window)所处的文件夹的绝对路径(F:\data-list\PycharmProjects\AQI)
        self.setWindowIcon(QIcon(QPixmap(self.root_+'\other_files\icon.jpeg')))
        # self.mapLabel()

    def initHeading(self):
        self.headinglabel.setText("全国空气质量预报及可视化软件平台")
        self.headinglabel.setFont(QFont('SimSun', 20, QFont.Black))
        self.headinglabel.setAlignment(Qt.AlignCenter)

        self.showtime_Label.setText(f'当前时间：20{curdate[0:2]}年{curdate[2:4]}月{curdate[4:6]}日{curdate[6:8]}时')
        self.prelength_Label.setText(f'预报长度：{outputwidth}')

        self.figure_label.setScaledContents(True)  # 图片自适应窗口大小

    def initMenu(self):
        self.menubar.setNativeMenuBar(False)
        self.actionopen.triggered.connect(self.actionOpen)
        self.actionsave.triggered.connect(self.actionSave)
        self.actionerror.triggered.connect(self.actionError)
        self.actionsetting.triggered.connect(self.actionSetting)
        self.actionabout.triggered.connect(self.actionAbout)

    def initStatusBar(self):
        self.setStatusBar(self.statusbar)

    def initcomboBox(self):
        self.comboBox_province.addItems(['全国', '北京市', '天津市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区', '海南省', '重庆市', '四川省', '贵州省', '云南省', '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区'])
        self.comboBox_province.setStyleSheet("QAbstractItemView::item {height: 20px;}")
        self.comboBox_province.setView(QListView())
        self.comboBox_province.currentIndexChanged.connect(self.selectionChange_province)
        # TODO 完善后续多选框，应该是一个动态多选连接
        # self.comboBox_city.addItem()
        # self.comboBox_district.addItem()

        self.comboBox_id.addItems(['54399', '57513'])  # 54399为北京市海淀区，57513为重庆渝北区
        self.comboBox_id.setStyleSheet("QAbstractItemView::item {height: 20px;}")
        self.comboBox_id.setView(QListView())
        self.comboBox_id.currentIndexChanged.connect(self.selectionChange_id)

        self.selectionButton_ok.clicked.connect(self.selectionButton_ok_Clicked)
        self.selectionButton_next.clicked.connect(self.selectionButton_next_Clicked)


    def initMap(self):
        # QWebEngineView控件打开html网页显示地图，html网页在后端生成
        # TODO 暂未实现地图交互，需要解决
        # map = folium.Map(
        #     location=[45.5236, -122.6750], tiles="Stamen Toner", zoom_start=13
        # )
        # map = folium.Map(location=[53.073635, 8.806422], zoom_start=15, tiles='Stamen Terrain')
        # 需要attr格式，不然打包会报错，暂时还没有解决
        # map = folium.Map(tiles="tiles/{z}/{x}/{y}.png", attr="<a href=https://endless-sky.github.io/>Endless Sky</a>")

        map = folium.Map(
            location=[35, 110],
            zoom_start=5,
            tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
            # style=6为卫星图，style=7为街道图，style=8为标注图。 7、8可用，均需联网
            # attr="&copy; <a href='https://ditu.amap.com/'>高德地图</a>")
            attr='高德地图')

        # map = folium.Map(
        #     location=[35, 110],
        #     zoom_start=5,
        #     tiles= QUrl.fromUserInput(rf'{stationMap_path}\{select_province}.html'),
        #     # style=6为卫星图，style=7为街道图，style=8为标注图。 7、8可用，均需联网
        #     # attr="&copy; <a href='https://ditu.amap.com/'>高德地图</a>")
        #     attr='高德地图')

        # map = folium.Map(
        #     location=[35, 110],
        #     zoom_start=5,
        #     tiles='http://wprd02.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=6&ltype=1',
        #     # style=6为卫星图，style=7为街道图，style=8为标注图。6可用
        #     attr='高德地图')
        # data = io.BytesIO()
        # map.save(data, close_file=False)
        # self.mapHtml.setHtml(data.getvalue().decode())

        self.mapShow(map)

    def mapShow(self, map):  # 输入folium.Map类型
        data = io.BytesIO()
        map.save(data, close_file=False)
        self.mapHtml.setHtml(data.getvalue().decode())

    def setWinCenter(self):
        screen = QDesktopWidget().availableGeometry()    # 获取屏幕工作区域大小（长与宽）
        window = self.geometry()  # 获取UI窗口大小（长与宽）
        newLetf = int((screen.width() - window.width())/2)
        newTop = int((screen.height() - window.height())/3)
        self.move(newLetf,newTop)

    # def mapLabel(self):
    #     map = self.root_+'\other_files\chinamap.jpg'
    #     self.maplabel.setPixmap(QPixmap(map))
    #     self.maplabel.setAlignment(Qt.AlignCenter)  # 图片在控件中居中
    #     self.maplabel.setScaledContents(True)   # 允许图片缩放，充满整个控件
    #     # QMessageBox.about

    def actionOpen(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)

        if dialog.exec():  # 如果对话框打开成功
            filenames = dialog.selectedFiles()
            encoding = get_encoding(filenames[0])
            # 编码类型自适应
            searchObjFile = open(filenames[0], encoding=encoding, errors='ignore')
            with searchObjFile:
                data = searchObjFile.read()
                self.test.setText(data)
                self.statusbar.showMessage("已导入文件", 4000)


    def actionSave(self):

        pass

    def actionError(self):

        pass

    def actionSetting(self):
        dialog = ConfigDialog(self)
        dialog.okButton.clicked.connect(self.textChange_Label)  # 对话框（子窗口的信号绑定在主窗口上）
        # ConfigDialog().exec()
        dialog.show()

    def actionAbout(self):
        QMessageBox.about()

        pass

    def selectionChange_province(self):
        global select_province
        select_province = self.comboBox_province.currentText()
        # print(select_province)

    def selectionChange_id(self):
        global select_id
        select_id = self.comboBox_id.currentText()
        # print(select_id)

    def selectionButton_ok_Clicked(self):
        global select_province
        global select_id
        select_province = self.comboBox_province.currentText()
        select_id = self.comboBox_id.currentText()
        self.mapHtml.load(QUrl.fromLocalFile(rf'{stationMap_path}\{select_province}.html'))
        self.heatHtml.load(QUrl.fromLocalFile(rf'{map_path}\HeatMap_Province\{select_province}_heatmap_{curdate}.html'))
        self.figure_label.setPixmap(QPixmap(rf'{figure_path}\curve_AQI_{54399}_{curdate}_Predhour{outputwidth}'))

        self.textChange_Label()
        # TODO 现在显示heatmap是离线的，需变成在线作图的形式
        # print(rf'{stationMap_path}\{select_province}.html')
        # self.mapHtml.load(QUrl("http://www.baidu.com"))
        # self.mapHtml.setHtml(rf'{stationMap_path}\{select_province}.html')

        # print('ok')

    def selectionButton_next_Clicked(self):
        print('next')


    def textChange_Label(self):
        # print(self.showtime_Label)
        # print(curdate)
        # print(outputwidth)
        self.showtime_Label.setText(f'当前时间：20{curdate[0:2]}年{curdate[2:4]}月{curdate[4:6]}日{curdate[6:8]}时')
        self.prelength_Label.setText(f'预报长度：{outputwidth}')

    # def get_StationMap(self, str):  # 输入省份字符串，输出保存好的html文件地址
    #     switcher = {
    #         '北京市':
    #     }
    #     pass


# 定义获取文件编码的函数
def get_encoding(file):
    with open(file, 'rb') as f:  # 用二进制打开，获取字节数据，检测类型
        return chardet.detect(f.read())['encoding']

if __name__ == "__main__":
    print('-----')




