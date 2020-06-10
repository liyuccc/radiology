# data处理,Lasso特征选择,COX回归
from function1 import read_File
import numpy as np
from sklearn import linear_model
from sklearn.feature_selection import SelectFromModel
import math
from lifelines.utils import k_fold_cross_validation
from lifelines import CoxPHFitter
import pandas as pd
# import time
# import eventlet#导入eventlet这个模块

# 将特征名行和序号列去掉
def Feature_format(feature):
    m = len(feature)
    n = len(feature[0])
    Feature = np.zeros((m-1,n-1))
    for i in range(1,m):
        for j in range(1,n):
            Feature[i-1,j-1] = feature[i][j]
    return Feature

# 读取OS以及status
def read_survival(input_path,sheet,feature,time_col,status_col):
    data = read_File(input_path, sheet)
    time = np.zeros((len(feature) - 1, 1))
    status = np.zeros((len(feature) - 1, 1))
    for i in range(1, len(feature)):
        for j in range(len(data)):
            if feature[i][0][41:44].find(str(data[j][0])) != -1:
                time[i - 1] = data[j][time_col]
                status[i - 1] = data[j][status_col]
    return time,status

# 整数拆分
def ints(num,part):
    b = np.floor(num / part)
    for c in range(part+1):
        if c * b + (10 - c) * (b + 1) == num:
            return int(b),c
# 随机划分训练测试集
def split(X,y,test_size):
    X_train = []
    X_test = []
    y_train = []
    y_test = []

    batch = int(1/test_size)
    m = X.shape[0]
    mini,s = ints(m,batch)
    # print(mini,s)
    # 获得打乱的id
    ID = np.zeros((m, 1))
    for id in range(m):
        ID[id] = id
    np.random.shuffle(ID)
    for t in range(batch):
        if t <s:
            train_x = X
            test_x = np.zeros((mini, X.shape[1]))
            train_y = y
            test_y = np.zeros((mini, y.shape[1]))
            test = []
            for i in range(mini):
                test.append(int(ID[i + mini * t]))
                test_x[i] = X[int(ID[i + mini * t])]
                test_y[i] = y[int(ID[i + mini * t])]
            train_x = np.delete(train_x, test, axis=0)
            train_y = np.delete(train_y, test, axis=0)
            X_train.append(train_x)
            X_test.append(test_x)
            y_train.append(train_y)
            y_test.append(test_y)
            # print("test:",test_x.shape,"train",train_x.shape)
        else:
            train_x = X
            test_x = np.zeros((mini+1, X.shape[1]))
            train_y = y
            test_y = np.zeros((mini+1, y.shape[1]))
            test = []
            for i in range(mini+1):
                test.append(int(ID[i + mini * s+(mini+1)*(t-s)]))
                test_x[i] = X[int(ID[i + mini * s+(mini+1)*(t-s)])]
                test_y[i] = y[int(ID[i + mini * s+(mini+1)*(t-s)])]
            train_x = np.delete(train_x, test, axis=0)
            train_y = np.delete(train_y, test, axis=0)
            X_train.append(train_x)
            X_test.append(test_x)
            y_train.append(train_y)
            y_test.append(test_y)
            # print("test:", test_y.shape, "train", train_y.shape)
    return X_train,X_test,y_train,y_test

# 皮尔逊相关系数

# Lasso
def Lasso(X,y,k):
    # model = linear_model.LassoCV(cv=5, normalize=True).fit(X, y)
    # clf = linear_model.Lasso(alpha= model.alphas_[k + 1], normalize=True)
    # clf = linear_model.Lasso(alpha=(model.alphas_[k]+model.alphas_[k+1])/2,normalize=True)
    if k == 5:
        alpha = 0.52
    if k == 20:
        alpha = 0.15
    judge = 1
    while(judge):
        clf = linear_model.Lasso(alpha=alpha, normalize=True)
        clf.fit(X, y)
        ID = []
        for id,coef in enumerate(clf.coef_):
            if (abs(coef)) >= 0.00001:
                ID.append(id+1)
        model = SelectFromModel(clf, prefit=True)
        X_new = model.transform(X)
        if k == 20:
            if X_new.shape[1] == k+1 or X_new.shape[1] == k or X_new.shape[1] == k-1:
                judge = 0
        if k == 5:
            if X_new.shape[1] == k:
                judge = 0
        if X_new.shape[1] < k:
            alpha = alpha - 0.0001
        else:
            alpha = alpha + 0.0001
    return X_new,ID
# name
def name(ID,X):
    name = []
    for id in (ID):
        name.append(X[0][id%1024])
    return name
# COX
def COX(X,y,name):
    data = {'T': y[:, 0],
            'E': y[:, 1],
            '%s'%name[0]: X[:, 0],
            '%s'%name[1]: X[:, 1],
            '%s'%name[2]: X[:, 2],
            '%s'%name[3]: X[:, 3],
            '%s'%name[4]: X[:, 4],
            }
    df = pd.DataFrame(data)
    # cph = CoxPHFitter(penalizer=0.1, l1_ratio=1.0)
    cph = CoxPHFitter()
    # scores = k_fold_cross_validation(cph, df, 'T', event_col='E', k=k, scoring_method="concordance_index")
    cph.fit(df, duration_col='T', event_col='E')
    # # cph.print_summary()
    # # cph.check_assumptions(df,p_value_threshold=0.05)
    return cph.concordance_index_

# C_index
def compute_C_index(predict,y_test):
    y_test = np.asarray(y_test)
    m = 0
    t = 0
    for a in range(y_test.shape[0]):
            for b in range(1,y_test.shape[0]):
                    if (y_test[a,1]==0 and y_test[b,1]==0) or\
                            (y_test[a,1]==0 and (y_test[a,0]<y_test[b,0])) or\
                            y_test[b,1]==0 and (y_test[b,0]<y_test[a,0]):
                            break
                    m = m+1
                    if (y_test[a,0]<y_test[b,0]) and predict[a]<predict[b] or \
                            (y_test[a, 0] > y_test[b, 0]) and predict[a] > predict[b]:
                            t = t+1
    if m == 0:
        cindex = 0
    else :
        cindex = t/m
    return cindex