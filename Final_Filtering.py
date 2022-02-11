import pandas as pd
import numpy as np
from csv import reader

from sys import exit
from haversine import haversine
import math
from operator import itemgetter

#시각화 도구
import folium
from folium.features import DivIcon

# 전역 변수 설정
PATIENT_UID = '2DDB3706DE4F7B45'# 감염자 UID
# TARGET_UID =  # 조사 대상자 UID

FILE_SAVE_DIR = './' #있다면 추가 해주기 (상대경로)
line_color_list = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
                    'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white',
                    'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'] 

#Call CSV file
def load_GPS_set(UID): # Data load
    try:
        data_set = pd.read_csv(FILE_SAVE_DIR + UID +"_gps"+".csv", sep=",", dtype='unicode')
        data_set['TIME STAMP'] = pd.to_datetime(data_set['LOG TIME'])
        data_set['TIME'] = data_set['TIME STAMP'].dt.strftime('%Y-%m-%d %H:%M') # 초단위 자르기
        re_data_set = data_set[["TIME","UID","altitude","latitude","longitude","provider"]]
        return re_data_set
    
    except FileNotFoundError as e:
        pass
def load_Sateillate_set(UID): # Data load
    try:
        data_set = pd.read_csv(FILE_SAVE_DIR + UID +"_sate"+".csv", sep=",", dtype='unicode')
        data_set['TIME STAMP'] = pd.to_datetime(data_set['LOG TIME'])
        data_set['TIME'] = data_set['TIME STAMP'].dt.strftime('%Y-%m-%d %H:%M') # 초단위 자르기
        re_data_set = data_set[["TIME","UID","SNR AVERAGE","SATELLITE COUNT"]]
        return re_data_set
    
    except FileNotFoundError as e:
        pass

def merge_gps_sati_set(gps_df, UID): # for weight_filter
    merge_df = pd.merge(gps_df,load_Sateillate_set(UID), how='left', on = ['TIME','UID'])
    return merge_df

test_df = load_GPS_set(PATIENT_UID)
merge_df = merge_gps_sati_set(test_df,PATIENT_UID)


#GPS FIllering by Clustering for Centriod Filter
Mass_map = folium.Map(location = [37.5505938572,127.074236903], zoom_start =100) # 세종대학교 중심 조사
Mass_cluster_list = [] #clustering list
clustering_size = 5
res_list = []
Centriod_point_list = [] # filtering point list
######################################################################

for count in test_df.index.values[120:223]:
    marker_point_lati = float(test_df.loc[count,'latitude'])
    marker_point_long = float(test_df.loc[count,'longitude'])
    marker_point = [marker_point_lati, marker_point_long]

    # 전처리 과정
    if len(Mass_cluster_list) < clustering_size: # cluster_list isnot full
        Mass_cluster_list.append(marker_point)
        if len(Mass_cluster_list) != 1:
            gps_dis = haversine(Mass_cluster_list[len(Mass_cluster_list)-1], marker_point) * 1000 #(m) 
            if gps_dis > 50:
                replace_point_x = (Mass_cluster_list[len(Mass_cluster_list)-1][0] + marker_point[0]) / 2
                replace_point_y = (Mass_cluster_list[len(Mass_cluster_list)-1][1] + marker_point[1]) / 2
                replace_point = [replace_point_x, replace_point_y]
                # Mass_cluster_list.append(Mass_cluster_list[len(Mass_cluster_list)-1]) # 이전 포인트를 그대로 넣느냐
                Mass_cluster_list.append(replace_point) # Mean Point로 대체해서 넣느냐
            else :
                Mass_cluster_list.append(marker_point)
   
    if len(Mass_cluster_list) == clustering_size: # cluster_list full
        sum_point_x = 0
        sum_point_y = 0
        for idx in range(0,clustering_size):
            sum_point_x += Mass_cluster_list[idx][0]
            sum_point_y += Mass_cluster_list[idx][1]
        mass_point = [sum_point_x/clustering_size, sum_point_y/clustering_size]
        res_list.append(mass_point)
        Mass_cluster_list.pop(0)

        

print(res_list)
folium.PolyLine(locations=res_list,tooltip='Polyline', color='blue').add_to(Mass_map) # draw line

# for index in range(0, len(res_list)):
#     folium.PolyLine(locations=res_list[index],tooltip='Polyline', color=line_color_list[index]).add_to(Centriod_map)


