# encdoing: utf-8
"""
@Project: aqi_qixiangju
@File:    utils
@Author:  Jiachen Zhao
@Time:    2021/11/9 20:38
@Description: 
"""

import numpy as np

# import pickle5 as pickle
import os
import pickle

def save_obj(obj, name, path='./'):
    with open(os.path.dirname(os.path.dirname(os.path.abspath('.'))) + path + '/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, path=',/'):
    with open(path + '/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def compute_iaqi(obs='pm25', cp=29, return_rank=False):
    if obs == 'pm25':
        if 0 < cp <=35:
            bpl, bph = 0, 35
            iaqil, iaqih = 0, 50
        elif 35 < cp <= 75:
            bpl, bph = 35, 75
            iaqil, iaqih = 50, 100
        elif 75 < cp <= 115:
            bpl, bph = 75, 115
            iaqil, iaqih = 100, 150
        elif 115 < cp <= 150:
            bpl, bph = 115, 150
            iaqil, iaqih = 150, 200
        elif 150 < cp <= 250:
            bpl, bph = 150, 250
            iaqil, iaqih = 200, 300
        elif 250 < cp <= 350:
            bpl, bph = 250, 350
            iaqil, iaqih = 300, 400
        elif 350 < cp <= 500:
            bpl, bph = 350, 500
            iaqil, iaqih =400, 500
    iaqip = (iaqih - iaqil) / (bph - bpl) * (float(cp) - bpl) + iaqil
    if return_rank:
        rank, quality, alarm_color = aqi2rank(iaqip)
        return iaqip, rank, quality, alarm_color
    else:
        return iaqip, None, None, None


def map_compute_iaqi(cp=29):
    if 0 < cp <=35:
        bpl, bph = 0, 35
        iaqil, iaqih = 0, 50
    elif 35 < cp <= 75:
        bpl, bph = 35, 75
        iaqil, iaqih = 50, 100
    elif 75 < cp <= 115:
        bpl, bph = 75, 115
        iaqil, iaqih = 100, 150
    elif 115 < cp <= 150:
        bpl, bph = 115, 150
        iaqil, iaqih = 150, 200
    elif 150 < cp <= 250:
        bpl, bph = 150, 250
        iaqil, iaqih = 200, 300
    elif 250 < cp <= 350:
        bpl, bph = 250, 350
        iaqil, iaqih = 300, 400
    elif 350 < cp <= 500:
        bpl, bph = 350, 500
        iaqil, iaqih =400, 500
    iaqip = (iaqih - iaqil) / (bph - bpl) * (float(cp) - bpl) + iaqil
    return iaqip


def aqi2rank(aqi=23):
    if aqi <= 50:
        rank, quality, alarm_color = 1, 'excellent', 'green'
    elif aqi <= 100:
        rank, quality, alarm_color = 2, 'good', 'yellow'
    elif aqi <= 150:
        rank, quality, alarm_color = 3, 'light pollution', 'orange'
    elif aqi <= 200:
        rank, quality, alarm_color = 4, 'moderate pollution', 'red'
    elif aqi <= 300:
        rank, quality, alarm_color = 5, 'heavy pollution', 'purple'
    elif aqi >300:
        rank, quality, alarm_color = 6, 'severe pollution', 'maroon'
    return rank, quality, alarm_color





if __name__ == "__main__":
    print('-----')
    aqi = compute_iaqi(obs='pm25', cp=239, return_rank=True)
    print(aqi)





