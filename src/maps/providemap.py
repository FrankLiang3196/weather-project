import os
import webbrowser
import numpy as np
import pandas as pd
import folium
import datetime
from IPython.display import HTML
from src.utils.utils import *
from folium.plugins import HeatMap

# root_path = os.path.abspath('.')
root_path = os.path.dirname(os.path.dirname(os.path.abspath('.')))
data_path = rf'{root_path}/datasets'
lookup_folder = data_path + '/lookup'

preprocess_path = data_path + '/proprocess_data'
preprocess_EachStation_Filled_2020= preprocess_path + '/20-EachStationEachFile'

map_path = rf'{root_path}\map_files'
stationMap_path = rf'{map_path}\StationMap'
jsonfile_path = rf'{map_path}\china.json'
test_path = rf'{map_path}\test.html'

provinces = ['黑龙江省', '内蒙古自治区', '吉林省', '新疆维吾尔自治区', '青海省', '甘肃省', '河北省', '山西省', '宁夏回族自治区', '陕西省', '河南省', '辽宁省', '北京市', '天津市', '山东省', '西藏自治区', '四川省', '云南省', '贵州省', '湖北省', '重庆市', '湖南省', '江西省', '广西壮族自治区', '广东省', '江苏省', '安徽省', '上海市', '浙江省', '福建省', '海南省']

def plot_stationIcon_fun(query="华北地区", map=None):  # 将输入地区省份的所有站点，在地图上标注出来
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    provinces = provinces_fun()  # csv中的所有省份
    # print(provinces)
    # ['黑龙江省', '内蒙古自治区', '吉林省', '新疆维吾尔自治区', '青海省', '甘肃省', '河北省', '山西省', '宁夏回族自治区', '陕西省', '河南省', '辽宁省', '北京市', '天津市', '山东省', '西藏自治区', '四川省', '云南省', '贵州省', '湖北省', '重庆市', '湖南省', '江西省', '广西壮族自治区', '广东省', '江苏省', '安徽省', '上海市', '浙江省', '福建省', '海南省']

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
    # print(query)
    stations_query_df = stations_df[stations_df['province'].isin(query)]  # 过滤出所选地区的省份数据
    # print(stations_query_df.shape)
    # (2465, 7)

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
                      popup=pop,
                      icon=folium.Icon(icon="cloud")).add_to(map)
    return map

def plot_stationprovince_fun(province="北京市", map=None):
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    stations_province_df = stations_df[stations_df['province'].isin(province)]

    folium.LayerControl().add_to(map)
    for idx, row in stations_province_df.iterrows():  # 编号，行信息
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
                      popup=pop,
                      icon=folium.Icon(icon="cloud")).add_to(map)
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
    map_base.save(f'{map_path}/AQI_Dot_map/{query}_dotmap_{Time}.html')


def plot_provinceHeatMap(province=['北京市'], Time=20010100):
    # 可用字典存储 省份:[站点id]，避免每次读文件，降低消耗提高速度
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    # global provinces
    stations_query_df = stations_df[stations_df['province'].isin(province)]
    # print(stations_query_df)

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
    map_base.add_child(HeatMap(data, radius=28, gradient={0.16: 'green', 0.32: 'yellow', 0.48: 'orange',
                                                          0.49: 'red', 0.8: 'purple', 1: 'maroon'}))
    # TODO 修改heatmap，引入动态时间变化
    # heatmap 有问题，不能如实的反应aqi实际数值大小。gradient中的数字代表百分位数，也就是说heatmap是根据数据密度来作图的，和数据本身的数值无关
    # print(df_haetmap)
    map_base.save(rf'{map_path}/HeatMap_Province/{province[0]}_heatmap_{Time}.html')


def provinces_fun():  # 获取csv中所有的省份名，返回省份名列表
    stations_df = pd.read_csv(lookup_folder + '/StationCity.csv', index_col=0)
    provinces = []
    for ii in stations_df['province'].unique().tolist():
        if ii is not np.NAN:
            if '\u4e00' <= ii[0] <= '\u9fff':
                provinces.append(ii)
    return provinces

def plot_baseMap():
    # ch_map = folium.Map(location=[35, 100], zoom_start=4)
    # # ch_map = folium.Map(
    # #     location=[38.96, 117.78],
    # #     zoom_start=4,
    # #     # tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', # 高德街道图
    # #     # tiles='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', # 高德卫星图
    # #     tiles='https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',  # google 卫星图
    # #     # tiles='https://mt.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', # google 地图
    # #     attr='default'
    # # )

    ch_map = folium.Map(
        location=[40.2, 116.4],  # 北京市 ： 40.2, 116.4 ; 重庆市 --； 湖北省 31.25, 112.63；上海市 31.25, 121.43
        zoom_start=8,  # 北京市 : 9 ;重庆市 7 ；湖北省 7 ；上海市 10
        tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
        # style=6为卫星图，style=7为街道图，style=8为标注图。 7、8可用，均需联网
        # attr="&copy; <a href='https://ditu.amap.com/'>高德地图</a>")
        attr='高德地图')

    # ch_map = folium.Map(
    #     location=[35, 110],
    #     zoom_start=5,
    #     tiles='http://wprd02.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=6&ltype=1',
    #     # style=6为卫星图，style=7为街道图，style=8为标注图。6可用
    #     attr='高德地图')

    # folium.Choropleth(
    #     geo_data=f'{map_path}\china.json',
    #     # geo_data = 'china.json',
    #     name='China regions',
    #     fill_opacity=0.1,
    #     line_opacity=0.2,
    # ).add_to(ch_map)
    return ch_map


def plot_stationMaps():  # 画出所有的站点数据点
    # queries = [
    #     "全国",
    # #     "华北地区", "华东地区", "东北地区", "华中地区", "华南地区", "西南地区", "西北地区"
    # ]
    # #
    # for query in queries:
    #     # map_base = plot_baseMap()  # 多张图，所有区域都画出
    #     map_query = plot_stationIcon_fun(query, plot_baseMap())
    #     # map_query = plot_stationIcon_fun(query, map_base)
    #     map_query.save(f'{stationMap_path}/{query}.html')

    province = ['上海市']
    # "北京市", '天津市', '河北省', '山西省', '内蒙古自治区',
    # '上海市', '江苏省', '浙江省', '山东省', '安徽省',
    # '辽宁省', '吉林省', '黑龙江省',
    # '湖北省', '湖南省', '河南省', '江西省',
    # '广东省', '广西壮族自治区', '海南省', '福建省',
    # '四川省', '重庆市', '贵州省', '云南省', '西藏自治区',
    # '陕西省', '甘肃省', '新疆维吾尔自治区', '青海省', '宁夏回族自治区'
    map_province = plot_stationprovince_fun(province, plot_baseMap())
    map_province.save(f'{stationMap_path}/{province[0]}.html')  # 存文件时候的中心位置和缩放比例需自行设置

    # TODO 1.计算出某位置的监测站点中心（经纬度求和取平均），放大倍数适中；
    # # 2.重画图层（Mapbox使用？），重点强调省份边界，用一张全国站点图即可，只改变中心位置






if __name__ == "__main__":
    print('-----')
    # map = plot_baseMap()
    # plot_stationIcon_fun('全国', map)
    # map.save(test_path)
    # webbrowser.open(test_path)

    # plot_stationMaps()

    plot_provinceHeatMap(['北京市'], 20010210)

    print('Done')