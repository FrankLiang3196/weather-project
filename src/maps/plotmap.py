# encdoing: utf-8
"""
@Project: pm25_v1
@File:    plotmap2
@Author:  Jiachen Zhao
@Time:    2021/8/2 14:30
@Description: 
"""

import os
# noinspection PyUnresolvedReferences
import numpy as np
import pandas as pd
import folium
import datetime
from IPython.display import HTML
from src.utils.utils import *
from folium.plugins import HeatMap

root_path = os.path.abspath('.')
data_path = rf'{root_path}/Datasets'
# data_path = rf'F:/data-list/PycharmProjects/Datasets/'
# data_path = r'/data1/zhaojiachen/Datasets/PM25/'
data_path_2021 = data_path + 'pm25-2021/'
data_path_2020 = data_path + 'pm25-2020/'
preprocess_data_path = data_path + 'pm25-preprocess_data/'
preprocess_EachHour_2021 = preprocess_data_path + '21-EachHourEachFile'
preprocess_EachStation_2021 = preprocess_data_path + '21-EachStationEachFile'

preprocess_EachHour_2020 = preprocess_data_path + '20-EachHourEachFile'
preprocess_EachStation_2020 = preprocess_data_path + '20-EachStationEachFile'
preprocess_EachStation_NotFilled_2020 = preprocess_EachStation_2020 + '/NotFilled'
preprocess_EachStation_Filled_2020 = preprocess_EachStation_2020 + '/Filled'

project_folder = "F:/data-list/PycharmProjects/pm25_v1"
lookup_folder = project_folder + "/lookup"
stationMap_folder = project_folder + "/StationMap"
neighborMap_folder = project_folder + "/StationNeighborMap"


def plot_baseMap():
    ch_map = folium.Map(location=[35, 100], zoom_start=4)
    # ch_map = folium.Map(
    #     location=[38.96, 117.78],
    #     zoom_start=4,
    #     # tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', # 高德街道图
    #     # tiles='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', # 高德卫星图
    #     tiles='https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',  # google 卫星图
    #     # tiles='https://mt.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', # google 地图
    #     attr='default'
    # )

    folium.Choropleth(
        geo_data='china.json',
        name='China regions',
        fill_opacity=0.1,
        line_opacity=0.2,
    ).add_to(ch_map)
    return ch_map


def plot_stationIcon_fun(query="华北地区", map=None):  # 将输入地区省份的所有站点，在地图上标注出来
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    provinces = provinces_fun()  # csv中的所有省份
    print(provinces)

    if query in provinces:
        query = [query]
    elif query == "全国":
        query = provinces
    elif query == "华北地区":
        query = ('北京市', '天津市', '河北省', '山西省', '内蒙古自治区')
    elif query == "华东地区":
        query = ('上海市', '江苏省', '浙江省', '山东省', '安徽省')
    elif query == "东北地区":
        query = ('辽宁省', '吉林省', '黑龙江省')
    elif query == "华中地区":
        query = ('湖北省', '湖南省', '河南省', '江西省')
    elif query == "华南地区":
        query = ('广东省', '广西壮族自治区', '海南省', '福建省')
    elif query == "西南地区":
        query = ('四川省', '重庆市', '贵州省', '云南省', '西藏自治区')
    elif query == '西北地区':
        query = ('陕西省', '甘肃省', '新疆维吾尔自治区', '青海省', '宁夏回族自治区')
    else:
        print(f"{query}, 错误的省份")
    print(query)
    stations_query_df = stations_df[stations_df['province'].isin(query)]  # 过滤出所选地区的省份数据
    print(stations_query_df.shape)

    folium.LayerControl().add_to(map)
    for idx, row in stations_query_df.iterrows():  # 编号，行信息
        s1 = f"ID: {int(row['id'])}"
        s2 = f"{row['latitude'], row['longitude']}"
        s3 = f"{row['province'], row['city'], row['district']}"
        WIDTH = max(len(s1.encode('utf-8')), len(s2.encode('utf-8')), len(s3.encode('utf-8')))
        pop = folium.Popup(html=folium.Html("""
                            {}</br>
                            {}</br>
                            {}</br>
                            """.format(s1, s2, s3),
                                            script=True,
                                            width=WIDTH * 4),
                           parse_html=True,
                           max_width=3000)
        folium.Marker(location=[row['latitude'], row['longitude']],
                      popup=pop).add_to(map)
    return map


def provinces_fun():  # 获取csv中所有的省份名，返回省份名列表
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    provinces = []
    for ii in stations_df['province'].unique().tolist():
        if ii is not np.NAN:
            if '\u4e00' <= ii[0] <= '\u9fff':
                provinces.append(ii)
    return provinces


def plot_stationMaps():  # 画出所有的站点数据点
    queries = [
        "全国",
        "华北地区", "华东地区", "东北地区", "华中地区", "华南地区", "西南地区", "西北地区",
        # "北京市", '天津市', '河北省', '山西省', '内蒙古自治区',
        # '上海市', '江苏省', '浙江省', '山东省', '安徽省',
        # '辽宁省', '吉林省', '黑龙江省',
        # '湖北省', '湖南省', '河南省', '江西省',
        # '广东省', '广西壮族自治区', '海南省', '福建省',
        # '四川省', '重庆市', '贵州省', '云南省', '西藏自治区',
        # '陕西省', '甘肃省', '新疆维吾尔自治区', '青海省', '宁夏回族自治区'
    ]
    for query in queries:
        map_base = plot_baseMap()  # 多张图，所有区域都画出
        plot_stationIcon_fun(query)
        # map_query = plot_stationIcon_fun(query, map_base)
        # map_query.save(f'{stationMap_folder}/{query}.html')


def add_StationByDF(map, df):  # 将传入的 dataframe 中的所有站点数据点显示在Map上
    for idx, row in df.iterrows():
        s1 = f"ID: {int(row['id'])}"
        s2 = f"{row['latitude'], row['longitude']}"
        s3 = f"{row['province'], row['city'], row['district']}"
        WIDTH = max(len(s1.encode('utf-8')), len(s2.encode('utf-8')), len(s3.encode('utf-8')))
        pop = folium.Popup(html=folium.Html("""
                            {}</br>
                            {}</br>
                            {}</br>
                            """.format(s1, s2, s3),
                                            script=True,
                                            width=WIDTH * 4),
                           parse_html=True,
                           max_width=3000)
        folium.Marker(location=[row['latitude'], row['longitude']],
                      popup=pop).add_to(map)
    return map


def plot_OneStationNeighbor_fun(query_id=None):
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    station_net_df = pd.read_csv(lookup_folder + '/StationNeighbors.csv', index_col=0)
    # print(station_net_df.head())
    # print(stations_df.head())
    map_base = plot_baseMap()
    folium.LayerControl().add_to(map_base)
    query_station = stations_df[stations_df['id'] == query_id]  # 选出输入序号站点的数据
    map = add_StationByDF(map_base, query_station)  # 将输入序号站点加入地图
    for i in range(1, 10):  # 若干相邻点
        neighbor_id_i = station_net_df[station_net_df['id'] == query_id][f'{i}_neighbor'].values[0]  # 得到目标站点对应的附近站点id值
        neighbor_dist_i = station_net_df[station_net_df['id'] == query_id][f'{i}_distance'].values[0]
        # print(neighbor_id_i, neighbor_dist_i)
        neighbor_station_i = stations_df[stations_df['id'] == neighbor_id_i]  # 得到附近站点的相关信息
        # print(neighbor_station_i)
        # print([query_station['latitude'].values[0], query_station['longitude'].values[0]])
        # print([neighbor_station_i['latitude'].values[0], neighbor_station_i['longitude'].values[0]])
        folium.PolyLine([[query_station['latitude'].values[0], query_station['longitude'].values[0]],
                         [neighbor_station_i['latitude'].values[0], neighbor_station_i['longitude'].values[0]]],
                        color='red').add_to(map)
        map = add_StationByDF(map, neighbor_station_i)  # 给出对应附近站点的标记
    return map


def plot_DotMap(query=None, Time=None):  # 某个时间下，某个地区范围内所有站点的空气质量等级颜色图（某站点一定半径范围内）
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    provinces = provinces_fun()

    if query in provinces:
        querys = [query]
    elif query == "全国":
        querys = provinces
    elif query == "华北地区":
        querys = ('北京市', '天津市', '河北省', '山西省', '内蒙古自治区')
    elif query == "华东地区":
        querys = ('上海市', '江苏省', '浙江省', '山东省', '安徽省')
    elif query == "东北地区":
        querys = ('辽宁省', '吉林省', '黑龙江省')
    elif query == "华中地区":
        querys = ('湖北省', '湖南省', '河南省', '江西省')
    elif query == "华南地区":
        querys = ('广东省', '广西壮族自治区', '海南省', '福建省')
    elif query == "西南地区":
        querys = ('四川省', '重庆市', '贵州省', '云南省', '西藏自治区')
    elif query == '西北地区':
        querys = ('陕西省', '甘肃省', '新疆维吾尔自治区', '青海省', '宁夏回族自治区')
    else:
        print(f"{query}, 错误的省份")
    stations_query_df = stations_df[stations_df['province'].isin(querys)]

    map_base = plot_baseMap()
    # folium.LayerControl().add_to(map_base)
    aqi_map_feature = folium.map.FeatureGroup()

    for idx, row in stations_query_df.iterrows():
        id = row['id']
        try:
            file = f'{preprocess_EachStation_Filled_2020}/Filled_{id}_2020.csv'
            df_station_observation = pd.read_csv(file, index_col=0)
            # print(df_station_observation.head())
            df_station_time = df_station_observation[df_station_observation['time'] == Time]  # 获取某个时间点下站点的数据
            pm25_value = df_station_time['pm25'].values[0]
            aqi, rank, quality, alarm_color = compute_iaqi(cp=pm25_value, return_rank=True)  # 空气质量指数aqi，等级，质量评价，警报等级
            # print(f"AQI: {np.round(aqi, 2)}, rank: {rank}, quality: {quality}, alarm_color: {alarm_color}")
            # print(pm25_value)
            # print([row['latitude'], row['longitude']])
            aqi_map_feature.add_child(  # 站点附近一定范围内，显示空气质量aqi对应颜色
                folium.CircleMarker(
                    [row['latitude'], row['longitude']],
                    radius=7,
                    color=None,
                    fill=True,
                    fill_color=alarm_color,
                    fillopacity=10
                )
            )
        except FileNotFoundError:
            print(f'There is no fill {preprocess_EachStation_Filled_2020}/Filled_{id}_2020.csv')
            continue
    map_base.add_child(aqi_map_feature)
    map_base.save(f'{project_folder}/AQI_Dot_map/{query}_dotmap_{Time}.html')

def plot_HeatMap(query='全国', Time=20020520):
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    provinces = provinces_fun()

    if query in provinces:
        querys = [query]
    elif query == "全国":
        querys = provinces
    elif query == "华北地区":
        querys = ('北京市', '天津市', '河北省', '山西省', '内蒙古自治区')
    elif query == "华东地区":
        querys = ('上海市', '江苏省', '浙江省', '山东省', '安徽省')
    elif query == "东北地区":
        querys = ('辽宁省', '吉林省', '黑龙江省')
    elif query == "华中地区":
        querys = ('湖北省', '湖南省', '河南省', '江西省')
    elif query == "华南地区":
        querys = ('广东省', '广西壮族自治区', '海南省', '福建省')
    elif query == "西南地区":
        querys = ('四川省', '重庆市', '贵州省', '云南省', '西藏自治区')
    elif query == '西北地区':
        querys = ('陕西省', '甘肃省', '新疆维吾尔自治区', '青海省', '宁夏回族自治区')
    else:
        print(f"{query}, 错误的省份")
    stations_query_df = stations_df[stations_df['province'].isin(querys)]

    map_base = plot_baseMap()

    df_haetmap = pd.DataFrame({'id': [], 'latitude': [], 'longitude': [], 'aqi': []})
    for idx, row in stations_query_df.iterrows():
        id = row['id']
        try:
            file = f'{preprocess_EachStation_Filled_2020}/Filled_{id}_2020.csv'
            df_station_observation = pd.read_csv(file, index_col=0)
            df_station_time = df_station_observation[df_station_observation['time'] == Time]  # 所选区域中某站点id，在所选时间下的站点数据
            pm25_value = df_station_time['pm25'].values[0]  # 取PM2.5浓度数据
            aqi, rank, quality, alarm_color = compute_iaqi(cp=pm25_value, return_rank=True)
            df_haetmap = df_haetmap.append({
                                            'id': id,
                                            'latitude': row['latitude'],
                                            'longitude': row['longitude'],
                                            'aqi': aqi
                                            }, ignore_index=True)  # 重建 df ，专为热力图，是输入 Time 下的某id站点的空气质量
        except FileNotFoundError:
            print(f'There is no fill {preprocess_EachStation_Filled_2020}/Filled_{id}_2020.csv')
            continue
    data = df_haetmap[['latitude', 'longitude', 'aqi']].values.tolist()  # 从 df 转为 array,最后转为 list
    map_base.add_child(HeatMap(data, radius=10, gradient={0.16: 'green', 0.32: 'yellow', 0.48: 'orange',
                                                         0.49: 'red', 0.8: 'purple', 1: 'maroon'}))
    print(df_haetmap)
    map_base.save(f'{project_folder}/AQI_heat_map/{query}_heatmap_{Time}.html')

def read_one_observation(id=None, Time=None, columns=['pm25', 'pm10']):  # 某站点id，单个时间点下，某些特征
    file = f'{preprocess_EachStation_Filled_2020}/Filled_{id}_2020.csv'
    df_station_observation = pd.read_csv(file, index_col=0)
    dfrow_station_time = df_station_observation[df_station_observation['time'] == Time]
    df_observation = dfrow_station_time[columns]
    return df_observation


def read_multiple_time(id=None, start_t=None, hours=6, direction='backward', columns=['time','pm25', 'pm10']):
    # a = '/'.join(['20'+str(start_t)[i:i+2] if i==0 else str(start_t)[i:i+2] for i in range(0, len(str(start_t)), 2)])
    begin = datetime.datetime.strptime(f'20{start_t}', '%Y%m%d%H')
    if direction == 'forward':
        delta = datetime.timedelta(hours=1)  # 时间差往前一小时
        tt = [(begin + delta * i).strftime('%Y%m%d%H')[2:] for i in range(hours)]  # 得到一个时间列表 [20010100, 20010101, ……]之类的
    elif direction == 'backward':
        delta = datetime.timedelta(hours=-1)
        tt = [(begin + delta * i).strftime('%Y%m%d%H')[2:] for i in range(hours)][::-1]  # 列表取反，时间仍然转为正序，与 'forward' 保持一致：时间点靠前的序号小
    tt = list(map(int, tt))  # 将字符串转换为int型
    dfs = pd.concat([read_one_observation(id=id, Time=t, columns=columns) for t in tt])
    dfs.reset_index(inplace=True, drop=True)  # 重置索引
    print(dfs)  # 时间前靠前的数据，索引小


def plot_OneStation_pm25_pop(id=None, Time=None):
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    station_info = stations_df[stations_df['id']==id]
    for idx, row in station_info.iterrows():
        observation = read_one_observation(id=id, Time=Time, columns=['pm25'])
        aqi, rank, quality, alarm_color = compute_iaqi(cp=observation.values, return_rank=True)
        print(f"AQI: {np.round(aqi, 2)}, rank: {rank}, quality: {quality}, alarm_color: {alarm_color}")
        map_base = plot_baseMap()
        folium.LayerControl().add_to(map_base)
        s1 = f"ID: {int(row['id'])}"
        s2 = f"{row['latitude'], row['longitude']}"
        s3 = f"{row['province'], row['city'], row['district']}"
        s4 = f"AQI:      {np.round(aqi, 2)}"
        s5 = f"RANK:     {rank}"
        s6 = f"QUALITY:  {quality}"
        s7 = f"ALARM:    {alarm_color}"
        WIDTH = max(len(s1.encode('utf-8')), len(s2.encode('utf-8')), len(s3.encode('utf-8')))

        pop = folium.Popup(html=folium.Html("""
                                    {}</br>
                                    {}</br>
                                    {}</br>
                                    {}</br>
                                    {}</br>
                                    {}</br>
                                    {}</br>
                                    {}</br>
                                    """.format(s1, s2, s3, '-'*len(s2), s4, s5, s6, s7),
                                            script=True,
                                            width=WIDTH * 4),
                           parse_html=True,
                           max_width=3000)
        folium.Marker(location=[row['latitude'], row['longitude']],
                      popup=pop).add_to(map_base)

        map_base.save(f'{project_folder}/AQI_pop_map/{id}_{Time}.html')




if __name__ == "__main__":
    print('-----')
    # plot_stationMaps()
    # query_plotOneStationNeighbor = [54499, 54511, 58367, 58035]
    # for query_id in query_plotOneStationNeighbor:
    #     map_OneStationNeighbor = plot_OneStationNeighbor_fun(query_id)
    #     map_OneStationNeighbor.save(f'{neighborMap_folder}/{query_id}_neighbors.html')
    # plot_DotMap(query='全国', Time=20020520)
    # read_one_observation(id = 54499, Time=20010508, columns=['pm25', 'pm10'])
    # read_multiple_time(id=54499, start_t=20010501, hours=6)
    # plot_OneStation_pm25_pop(id=58035, Time=20070107)
    # plot_OneStation_pm25_pop(id=54499, Time=20121109)
    # plot_HeatMap(query='河北省', Time=20112520)
