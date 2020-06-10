from function1 import read_File
from function2 import Feature_format,read_survival,Lasso,split,compute_C_index
import numpy as np
from sklearn import preprocessing
import pandas as pd
from lifelines import CoxPHFitter
from collections import Counter


"""
1.数据分五个ROI分别LASSO,筛除大部分冗余特征
2.合在一起再次进行LASSO特征选择
3.COX
"""

# 1.read feature
zhongliu_inputpath = "/home/lyu/PythonProjects/radiomics/Feature/Multi model/multi_modal_zhongliu.xlsx"
zhongliu_3DT1 = read_File(zhongliu_inputpath,"3DT1")
# print(np.shape(zhongliu_3
zhongliu_3DT1p = Feature_format(zhongliu_3DT1)
zhongliu_rCBF = read_File(zhongliu_inputpath,"rCBF")
zhongliu_rCBFp = Feature_format(zhongliu_rCBF)
zhongliu_ADC = read_File(zhongliu_inputpath,"ADC")
zhongliu_ADCp = Feature_format(zhongliu_ADC)
zhongliu_Dfast = read_File(zhongliu_inputpath,"Dfast")
zhongliu_Dfastp = Feature_format(zhongliu_Dfast)
zhongliu_Dslow = read_File(zhongliu_inputpath,"Dslow")
zhongliu_Dslowp = Feature_format(zhongliu_Dslow)
zhongliu__f = read_File(zhongliu_inputpath,"_f")
zhongliu__fp = Feature_format(zhongliu__f)
# # print(zhongliu__fp.shape)DT1))
# print(zhongliu_3DT1p.shape,zhongliu_rCBFp.shape,zhongliu_ADCp.shape,\
#       zhongliu_Dfastp.shape,zhongliu_Dslowp.shape,zhongliu__fp.shape)
# feature = np.append(zhongliu_3DT1p, zhongliu_rCBFp,zhongliu_ADCp,\
#                     zhongliu_Dfastp,zhongliu_Dslowp,zhongliu__fp, axis=1)
feature = np.append(zhongliu_3DT1p, zhongliu_rCBFp,axis=1)
feature = np.append(feature, zhongliu_ADCp, axis=1)
feature = np.append(feature, zhongliu_Dfastp, axis=1)
feature = np.append(feature, zhongliu_Dslowp, axis=1)
feature = np.append(feature, zhongliu__fp, axis=1)
# feature = np.concatenate(feature)
# print(feature.shape)

# 读取生存时间,生存状态
data_path = "/home/lyu/PythonProjects/radiomics/Feature/Multi model/Data.xlsx"
data_sheet = "valid"
time, status = read_survival(data_path, data_sheet, zhongliu_3DT1, 30, 28)
# print(time, status,time.shape,status.shape)
survival = np.append(time, status,axis=1)

# 特征标准化
min_max_scaler = preprocessing.MinMaxScaler()
future_min_max = min_max_scaler.fit_transform(feature)
feature_scaled = preprocessing.scale(future_min_max)
# feature_scaled = preprocessing.normalize(feature_scaled, norm='l2')
# 交叉验证

count = []
train_c_index = []
test_c_index = []
for k in range(1):
    # 分测试验证集
    feature_train, feature_test, survival_train, survival_test = split(feature_scaled, survival, test_size=0.1)

    for i in range(10):
        print("第",k+1,"组",i+1,"次训练")
        X_train = feature_train[i]
        X_test = feature_test[i]
        y_train = survival_train[i]
        y_test = survival_test[i]
        print(X_train.shape,X_test.shape)
    # X_train = feature_train[0]
    # X_test = feature_test[0]
    # y_train = survival_train[0]
    # y_test = survival_test[0]
    # print(y_test)
    # np.savetxt('X_train.txt',X_train,fmt='%0.8f')
    # np.savetxt('X_test.txt',X_train,fmt='%0.8f')
    # np.savetxt('y_train.txt',y_train,fmt='%d')
    # np.savetxt('y_test.txt',y_test,fmt='%d')

    # Lasso
        # 分5个ROI分别LASSO
        print("begin")
        threeDT1_selected,ID1 = Lasso(X_train[:,0:1780], y_train[:, 0], 20)
        print("over")
        rCBF_selected,ID2 = Lasso(X_train[:,1781:3561], y_train[:, 0], 20)
        print("2")
        ADC_selected,ID3 = Lasso(X_train[:,3562:5342], y_train[:, 0], 20)
        print("3")
        Dfast_selected,ID4 = Lasso(X_train[:,5343:7123], y_train[:, 0], 20)
        print("4")
        Dslow_selected,ID5 = Lasso(X_train[:,7124:8904], y_train[:, 0], 20)
        print("5")
        f_selected,ID6 = Lasso(X_train[:,8905:10685], y_train[:, 0], 20)
        # x_selected1 = np.append(threeDT1_selected,rCBF_selected,ADC_selected,\
        #                         Dfast_selected,Dslow_selected,f_selected,axis=1)
        x_selected1 = np.append(threeDT1_selected, rCBF_selected, axis=1)
        x_selected1 = np.append(x_selected1, ADC_selected, axis=1)
        x_selected1 = np.append(x_selected1, Dfast_selected, axis=1)
        x_selected1 = np.append(x_selected1, Dslow_selected, axis=1)
        x_selected1 = np.append(x_selected1, f_selected, axis=1)
        print("x_selected1:",x_selected1.shape)
        ID_ALL = ID1+ID2+ID3+ID4+ID5+ID6
        # 合在一起再LASSO
        X_selected,ID_ = Lasso(x_selected1,y_train[:,0],5)
        ID = ID_
        for i,id in enumerate(ID_):
            ID[i] = ID_ALL[id]
        # ID = np.asarray(ID)
        count = count+ID
        print("X_selected:",X_selected.shape)
        name = []
        for id in (ID):
            if int(id/1781)==0:
                name.append("zhongliu_3DT1,"+zhongliu_3DT1[0][id % 1781])
            if int(id / 1781) == 1:
                name.append("zhongliu_rCBF," + zhongliu_3DT1[0][id % 1781])
            if int(id/1781)==2:
                name.append("zhongliu_ADC,"+zhongliu_3DT1[0][id % 1781])
            if int(id/1781)==3:
                name.append("zhongliu_Dfast,"+zhongliu_3DT1[0][id % 1781])
            if int(id/1781)==4:
                name.append("zhongliu_Dslow,"+zhongliu_3DT1[0][id % 1781])
            if int(id/1781)==5:
                name.append("zhongliu__f,"+zhongliu_3DT1[0][id % 1781])
        # print("name:",name[0],"\n",name[1],"\n",name[2],"\n",name[3],"\n",name[4],"\n")

        # COX
        data = {'T': y_train[:, 0],
                'E': y_train[:, 1],
                '%s' % name[0]: X_selected[:, 0],
                '%s' % name[1]: X_selected[:, 1],
                '%s' % name[2]: X_selected[:, 2],
                '%s' % name[3]: X_selected[:, 3],
                '%s' % name[4]: X_selected[:, 4],
                }
        df = pd.DataFrame(data)
        # cph = CoxPHFitter(penalizer=0.1, l1_ratio=1.0)
        cph = CoxPHFitter()
        cph.fit(df, duration_col='T', event_col='E')
        # c_index = COX(X_selected,y_train,name)
        train_c_index.append(cph.concordance_index_)
        print("Train_c_index:",cph.concordance_index_)
        # 预测c_index
        # data_test
        data_test = {'T': y_test[:, 0],
                'E': y_test[:, 1],
                '%s' % name[0]: X_test[:, ID[0]-1],
                '%s' % name[1]: X_test[:, ID[1]-1],
                '%s' % name[2]: X_test[:, ID[2]-1],
                '%s' % name[3]: X_test[:, ID[3]-1],
                '%s' % name[4]: X_test[:, ID[4]-1],
                #  '%s' % name[0]: X_test[:, ID[0]+1],
                #  '%s' % name[1]: X_test[:, ID[1]+1],
                #  '%s' % name[2]: X_test[:, ID[2]+1 ],
                #  '%s' % name[3]: X_test[:, ID[3]+1],
                #  '%s' % name[4]: X_test[:, ID[4]+1 ],
                }
        df_test = pd.DataFrame(data_test)
        predict = cph.predict_expectation(df_test)
        test_c_index.append(compute_C_index(predict,y_test))
train_c_index = np.asarray(train_c_index)
print("Train_c_index_mean:",np.mean(train_c_index))
test_c_index = np.asarray(test_c_index)
test_c_index = np.delete(test_c_index,0)
print("test:",test_c_index)
print("Test_c_index_mean:",np.mean(test_c_index))
# 将选出的
# print(count)
rank = Counter(count).most_common(7)
print(rank,rank[0][0])

name = []
for i in (rank):
    id = i[0]
    if int(id / 1781) == 0:
        name.append("zhongliu_3DT1," + zhongliu_3DT1[0][id % 1781])
    if int(id / 1781) == 1:
        name.append("zhongliu_rCBF," + zhongliu_3DT1[0][id % 1781])
    if int(id / 1781) == 2:
        name.append("zhongliu_ADC," + zhongliu_3DT1[0][id % 1781])
    if int(id / 1781) == 3:
        name.append("zhongliu_Dfast," + zhongliu_3DT1[0][id % 1781])
    if int(id / 1781) == 4:
        name.append("zhongliu_Dslow," + zhongliu_3DT1[0][id % 1781])
    if int(id / 1781) == 5:
        name.append("zhongliu__f," + zhongliu_3DT1[0][id % 1781])
print("name:",np.shape(name), "\n",name[0], "\n", name[1], "\n", name[2], "\n", name[3],
      "\n", name[4], "\n","count_top5:",rank[0:5])
