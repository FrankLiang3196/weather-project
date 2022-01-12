# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    main
@Author:  Jiachen Zhao
@Time:    2021/11/7 18:25
@Description:
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from src.my_main_window import MainWindow
from datetime import datetime, timedelta
from sktime.utils.plotting import plot_series

from src.utils import my_main
from src.utils.model import NaiveTorchForecaster
from src.utils.develop_utils import load_parameter
from src.utils import utils

# from src.my_config_dialog import ConfigDialog


# global INPUT_DIR  # string, the input file direction
# global OUTPUT_DIR  # string, the output file direction
# global INPUT_WINDOW_WIDTH  # int, the input window width
# global OUTPUT_WINDOW_WIDTH  # int, the output window width
# global CURRENT_TIME  # string, the system time

# INPUT_DIR = "./input_files/20-EachHourEachFile"
# OUTPUT_DIR = "./output_files"
# MODEL_DIR = "./model_files"
# INPUT_WINDOW_WIDTH = 6
# OUTPUT_WINDOW_WIDTH = 48
# CURRENT_TIME = "20010110"


# model related parameters
# STATION_BATCH_SIZE = 10  # 在预测时，每次输入模型几个站点的数据
# INPUT_FEATURES = ['pm25']


# def read_data_at_a_time():
#     filename = os.path.join(INPUT_DIR, CURRENT_TIME) + '.csv'
#     df = pd.read_csv(filename, index_col=0)
#     return df


def read_past_data(args, current_time, each_station=False, id=54399):  # current_time为字符串
    # 将前几个小时的数据合并成一个DataFrame
    if not each_station:  # 读的是 EachHourEachFile 文件，不需要传入id
        t = datetime.strptime(current_time, '%y%m%d%H')
        past_times = [(t - timedelta(hours=i)).strftime('%y%m%d%H') for i in range(args.input_window_width)]  # 当前时刻t特征数值假设已知
        df_list = []
        for i, t in enumerate(past_times):
            filename = os.path.join(args.input_dir, t) + '.csv'
            df = pd.read_csv(filename, index_col=0)
            if i > 0:
                df.drop('id', axis=1, inplace=True)
                df.columns = df.columns + f'(t-{i})'
            df_list.append(df)
        df = pd.concat(df_list, axis=1)
        return df  # df为二维形式，列名最终为：[id, wind_direction, wind_speed, pm10, pm25, ……全部特征, wind_direction(t-1), wind_speed(t-1), pm10(t-1), pm25(t-1), ……全部特征,]
    else:  # 读的是 EachStationEachFile 文件，需要传入id
        t = datetime.strptime(current_time, '%y%m%d%H')
        past_times = [(t - timedelta(hours=i)).strftime('%y%m%d%H') for i in range(args.input_window_width)]
        df_id = pd.DataFrame(columns=['id'])
        df_list = [df_id]
        filename = os.path.join(args.input_dir, f'20-EachStationEachFile/Filled_{id}_20{current_time[0:2]}') + '.csv'
        df = pd.read_csv(filename, index_col='time')  # 文件中time的类型为int
        for i, t in enumerate(past_times):
            df_ = df.loc[[int(t)],['wind_direction', 'wind_speed', 'pm10', 'pm25', 'humidity', 'dew', 'visibility', 'temperature']]  # 读取所有特征，保持结构统一
            if i > 0:
                df_.columns = df_.columns + f'(t-{i})'
            df_ = df_.reset_index(drop=True)
            df_list.append(df_)
        df = pd.concat(df_list, axis=1)
        df['id'].fillna(54399, inplace=True)
        return df  # 保持格式与上一种情况一致，二维数组， 1*N


def feed_in_pred_phase(df, args):
    # 主要筛选需要的特征列
    feature_columns = [feature if i == 0 else f'{feature}(t-{i})'
                       for i in range(args.input_window_width)
                       for feature in args.input_features
                       ]
    df_input = df[feature_columns]  # 选出感兴趣的特征数据
    input_array = df_input.to_numpy()  # input_array为二维形式，第一维表示站点id，第二维为特征[pm25, pm10, pm25(t-1), pm10(t-1), ……]
    # reshape the input array into [num of stations, past time length, num of features]. 可变为多站点联合预测
    input_array = input_array.reshape([input_array.shape[0],
                                       args.input_window_width,
                                       len(args.input_features)])  # time axis order is t, t-1, t-2, ..., t-5
    input_array = np.flip(input_array, 1, ).copy()  # reverse the time order to t-5, t-4, ..., t-1, t, if necessary
    # input_array = input_array[:, ::-1, :]
    # TODO: 简单填充，检验流程，后期必须完善
    input_array[np.isnan(input_array)] = 0  # 空缺值填补为零，或者改变文件读取方式，读 Filled_50353_2020 类文件，无空缺值
    return input_array  # 输出input_array为二维形式，第一维表示站点id，第二维为特征[pm25(t-5), pm10(t-5),……,pm25(t-1), pm10(t-1), pm25, pm10], input_window_width=6时

def update_input(X, Y_hat):  # 多步预测时，用预测数值作为下一时刻的输入
    """
    多步预测中，根据此步模型的输入，和此步模型的预测结果，更新下一步模型的输入
    X shape: [num of stations, past time length, num of features]
    Y_hat: [num of stations, num of features]
    """
    updated_X = np.concatenate([X[:, 1:, :], Y_hat[:, None, :]], axis=1)
    return updated_X

def update_input_realdata(X, args, current_time, id=54399):  # 多步预测时，用真实数值作为下一时刻的输入
    """
    多步预测中，根据此步模型的输入，和此步模型的预测结果，更新下一步模型的输入
    X shape: [num of stations, past time length, num of features]
    Y_hat: [num of stations, num of features]
    """
    real_filename = os.path.join(args.input_dir,
                                 f'20-EachStationEachFile/Filled_{id}_20{current_time[0:2]}') + '.csv'
    feature_columns = [feature for feature in args.input_features]

    if os.path.exists(real_filename):
        real_df = pd.read_csv(real_filename, index_col='time')  # 文件中time的类型为int，过去值
    else:
        raise ValueError(f'Do NOT exist this csv in {args.output_dir}!')

    Y_hat = real_df.loc[[int(current_time)],feature_columns]  # 当前时刻的真实值
    # Y_hat = Y_hat.reset_index()
    # Y_hat = Y_hat[feature_columns]
    Y_hat = Y_hat.values  # 取值，转为array格式
    # print(type(Y_hat))
    # print(X)
    updated_X = np.concatenate([X[:, 1:, :], Y_hat[:, None, :]], axis=1)
    return updated_X


def update_time(current_time: str):  # 时间更新到下一时刻 current_time + 1hour
    t = datetime.strptime(current_time, '%y%m%d%H')
    updated_time = (t + timedelta(hours=1)).strftime('%y%m%d%H')
    return updated_time


def initialize_foecaster(args):  # 参设设置在config文件中，为其他文件留出接口
    if args.model_type == "naive_torch_forecaster":
        forcaster = NaiveTorchForecaster(args)

    else:
        raise ValueError('Do NOT exist this model type')
    forcaster.load_model()

    return forcaster

class MultiStepForcaster():
    def __init__(self, args):
        self.args = args  # 加载参数
        self.forecaster = initialize_foecaster(args)  # 选择预测模型
        # self.current_time = args.start_time

    def forecast(self, current_time):  # 多步预测，预测步长由config文件决定
        # 读取过去数小时的数据
        past_df = read_past_data(self.args, current_time, each_station=True, id=54399)
        # 准备空的dataFrame来保存预测结果
        # result_df = pd.DataFrame(columns=["id"]+[f"t+{i+1}" for i in range(self.args.output_window_width)])
        columns = [f'{feature}(t+{i+1})' for i in range(self.args.output_window_width)  # [feature(t+1), feature(t+2), feature(t+3), feature(t+4), ……]
                   for feature in self.args.input_features]                             # feature为 pm25, pm10等
        result_df = pd.DataFrame(columns=['id', 'start_time']+columns)  # 列名合并，引入id
        result_df['id'] = past_df['id']  # 传入站点id数据
        id = past_df.iloc[0,0]
        result_df['start_time'] = int(current_time)

        current_time_process = current_time

        for i in range(self.args.output_window_width):  # 在单步上循环实现多步预测
            if i == 0:
                X = feed_in_pred_phase(past_df, self.args)  # 改变输入格式，选出感兴趣的特征
                y_hat_one_step = self.forecaster.predict(X)
                result_df[[f'{feature}(t+{i+1})' for feature in self.args.input_features]] = \
                    pd.DataFrame(y_hat_one_step.round(4))  # 传入预测数据(t+1)
                # X = update_input(X, y_hat_one_step)

                current_time_process = self.currentime_add(current_time_process)
                X = update_input_realdata(X, self.args, current_time_process, id=54399)
            else:
                y_hat_one_step = self.forecaster.predict(X)
                result_df[[f'{feature}(t+{i+1})' for feature in self.args.input_features]] = \
                    pd.DataFrame(y_hat_one_step.round(4))
                # X = update_input(X, y_hat_one_step)

                current_time_process = self.currentime_add(current_time_process)
                X = update_input_realdata(X, self.args, current_time_process, id=54399)
        result_df.to_csv(f'{self.args.output_dir}/Forecast_csv/Forecast_{current_time}_id{id}_outputwidth{self.args.output_window_width}_{self.args.model_type}.csv')
        return result_df

    def provide_curves(self, current_time, aqi_figure=False, id=54399):  # 传入current_time为str
        real_filename = os.path.join(self.args.input_dir, f'20-EachStationEachFile/Filled_{id}_20{current_time[0:2]}') + '.csv'
        pre_filename = f'{self.args.output_dir}/Forecast_csv/Forecast_{int(current_time)}_id{id}_outputwidth{self.args.output_window_width}_{self.args.model_type}.csv'
        if os.path.exists(real_filename):
            real_df = pd.read_csv(real_filename, index_col='time')  # 文件中time的类型为int，过去值
        else:
            raise ValueError(f'Do NOT exist this csv in {self.args.output_dir}!')
        if os.path.exists(pre_filename):
            pre_df = pd.read_csv(pre_filename)  # 预测值
        else:
            raise ValueError(f'Do NOT exist this csv in {self.args.output_dir}!')
        t = datetime.strptime(current_time, '%y%m%d%H')
        past_times = [(t - timedelta(hours=i)).strftime('%y%m%d%H') for i in range(11, -1, -1)]  # 过去值长度. self.args.input_window_width ;(t-12), (t-11), ……,t
        pre_times = [(t + timedelta(hours=i+1)).strftime('%y%m%d%H') for i in range(self.args.output_window_width)]  # 预测长度，从t+1时刻开始，t时刻为已知

        list_past = []
        list_pre_real = []  # 对应预测的真实值
        df_pre_pm25 = pd.DataFrame(columns=['time', 'pm25'])  # 画图数据格式
        # pre_columns = [f'pm25(t+{i + 1})' for i in range(self.args.output_window_width)]  # [feature(t+1), feature(t+2), feature(t+3), feature(t+4), ……]
        for i, t in enumerate(past_times):
            df = real_df.loc[[int(t)], ['pm25']]
            list_past.append(df)
        df_past_pm25 = pd.concat(list_past, axis=0)
        df_past_pm25 = self.index_to_datetime(df_past_pm25)  #  格式N*1，索引为datetime
        # return df_past_pm25

        for i, t in enumerate(pre_times):
            pre_data = pre_df.loc[0, [f'pm25(t+{i + 1})']]  # 输出预测值，数据结构为Series
            pre_real_df = real_df.loc[[int(t)], ['pm25']]  # 对应预测的真实值
            list_pre_real.append(pre_real_df)
            df_pre_pm25.loc[i] = [t, float(pre_data)]  # 填入预测值
        df_pre_real_pm25 = pd.concat(list_pre_real, axis=0)
        df_pre_real_pm25 = self.index_to_datetime(df_pre_real_pm25)
        df_pre_pm25.set_index('time', drop=True, inplace=True)
        df_pre_pm25 = self.index_to_datetime(df_pre_pm25)
        # return df_pre_pm25

        fig, ax = plot_series(df_past_pm25['pm25'], df_pre_pm25['pm25'], df_pre_real_pm25['pm25'],      # 取序列
                              labels=["History", "Prediction", "Real data"])
        current_time_ = pd.to_datetime(current_time, format='%y%m%d%H')
        fig.suptitle(f'Current Time: {current_time_}')
        plt.savefig(f"{self.args.output_dir}/Curves/curve_PM25_{id}_{current_time}_Predhour{self.args.output_window_width}")

        if aqi_figure:
            ## 将上面的pm25数值都转成aqi数值再画图
            df_past_aqi = df_past_pm25.applymap(utils.map_compute_iaqi)  # 对dataframe每个元素进行遍历
            df_past_aqi.rename(columns={'pm25':'aqi'}, inplace=True)
            # return df_past_aqi
            df_pre_aqi = df_pre_pm25.applymap(utils.map_compute_iaqi)  # 对dataframe每个元素进行遍历
            df_pre_aqi.rename(columns={'pm25':'aqi'}, inplace=True)
            df_pre_real_aqi = df_pre_real_pm25.applymap(utils.map_compute_iaqi)  # 对dataframe每个元素进行遍历
            df_pre_real_aqi.rename(columns={'pm25':'aqi'}, inplace=True)

            fig, ax = plot_series(df_past_aqi['aqi'], df_pre_aqi['aqi'], df_pre_real_aqi['aqi'],  # 取序列
                                  labels=["History", "Prediction", "Real data"])
            current_time_ = pd.to_datetime(current_time, format='%y%m%d%H')
            fig.suptitle(f'Current Time: {current_time_}')
            plt.savefig(f"{self.args.output_dir}/Curves/curve_AQI_{id}_{current_time}_Predhour{self.args.output_window_width}")


    def index_to_datetime(self, dataframe):  # 传入的dataframe的索引为time，如20010110，转换为datetime格式的索引
        dataframe = dataframe.reset_index()
        dataframe['time'] = pd.to_datetime(dataframe['time'], format='%y%m%d%H')
        dataframe = dataframe.set_index('time', drop=True)  # , inplace=True
        dataframe.index = pd.PeriodIndex(dataframe.index, freq="H")
        return dataframe

    def currentime_add(self, current_time):  # 传入str型current_time，current_time+1小时 并返回
        t = datetime.strptime(current_time, '%y%m%d%H')
        t = t + timedelta(hours=1)
        current_time_ = t.strftime('%y%m%d%H')
        return current_time_

def main():
    args = load_parameter('config', main_load=True)

    # app = QApplication(sys.argv)
    # app.setApplicationName('AQI Forecast')
    # app.setWindowIcon(QIcon('./other_files/icon.jpeg'))  # ios系统下显示图标
    # main_window = MainWindow()
    # config_diaglog = ConfigDialog()
    # main_window.show()
    # sys.exit(app.exec_())

    # forecaster = initialize_foecaster(args)

    # read_data_at_a_time()
    # df = read_past_data(args, args.start_time)
    # input = feed_in_pred_phase(df, args)
    # print(input.shape)
    # y_hat = forecaster.predict(input)
    # print(y_hat.shape)

    multi_step_forecaster = MultiStepForcaster(args)
    current_time = args.start_time
    for i in range(13):  # 连续预测？或者是定时循环预测（一小时刷新一次或者按下一次按钮循环一次）
        multi_step_forecaster.forecast(current_time)
        current_time = update_time(current_time)
    df = multi_step_forecaster.provide_curves(args.start_time, aqi_figure=True, id=54399)
    print(df)


if __name__ == "__main__":
    print('-----------')
    main()

    print('Done')

    # args = load_parameter('config', main_load=True)
    # df=my_main.read_past_data(args, '20010110', each_station=True, id=54399)
    # print(df)

    # args = load_parameter('001')
    # input = np.array([[[1,2], [2,3], [3,4], [4,5], [5,6], [6,7]], [[3,2], [4,3], [6,5], [5,5], [7,7], [7,8]],
    #                   [[1,2], [1,3], [1,5], [1,5], [1,7], [1,8]]])

    # forecaster = NaiveTorchForecaster(args)
    # y_hat = forecaster.predict(input)
    # print(y_hat.round(2))
    # print(input.shape, y_hat.shape)
    # updated_input = np.concatenate([input[:, 1:, :], y_hat[:, None, :]], axis=1)
    # print(updated_input.round(2))

    # multi_step_forecaster = MultiStepForcaster(args)
    # multi_step_forecaster.forecast(args.start_time)


