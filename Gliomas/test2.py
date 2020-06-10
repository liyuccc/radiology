from lifelines import CoxPHFitter
import pandas as pd
import numpy as np
import os
from function1 import read_File

# Data
path = '/home/lyu/PythonProjects/Glioma/Info'
py_3DT1 = '3DT1_zhongliu_Normed.xlsx'
collage_3DT1 = 'collage_3DT1_zl_Normed.xlsx'
comp_scaled = 'comp_Scaled.xlsx'
Data = 'Data.xlsx'
Feature = read_File(os.path.join(path,comp_scaled),'3DT1')
info = read_File(os.path.join(path,Data),'valid')
feature = Feature[1:,1:].astype(float)

# Dataframe
# df =pd.DataFrame([feature[0]],columns=Feature[0, 1:])
# for i in range(1,feature.shape[0]):
#   df_below = pd.DataFrame([feature[i]],columns=Feature[0, 1:])
#   df = pd.concat([df,df_below],ignore_index=True)

# df_info = pd.DataFrame({
#   'status':info[1:,28],
#   'os':info[1:,30]
# })
# status = df_info.pop('status')
# os = df_info.pop('os')
# df['status'] = status
# df['os'] = os

# 单因素
concordance_index_list = []
selected_id_list = []
for i in range(feature.shape[1]):
  # if i>1:
  #   break
  data = pd.DataFrame({
    Feature[0,i+1]:feature[:,i],
    'status':info[1:,28],
    'os':info[1:,30]
  })
  try:
    cph = CoxPHFitter()
    cph.fit(data, duration_col='os', event_col='status')
    print(cph.summary['p'].array[0])
    if cph.summary['p'].array[0] < 0.05 :
      selected_id_list.append(i)
  except:
    print(Feature[0,i+1],'has problems')

print(len(selected_id_list))


