import numpy as np
import nibabel as nib
import skimage.io as io
import numpy as np


def normalize_data(data, mean, std):
    # data：[4,144,144,144]
    data -= mean[:, np.newaxis, np.newaxis, np.newaxis]
    data /= std[:, np.newaxis, np.newaxis, np.newaxis]
    return data


def normalize_data_storage(data_storage):
    means = list()
    stds = list()
    # [n_example,4,144,144,144]
    for index in range(data_storage.shape[0]):
        # [4,144,144,144]
        data = data_storage[index]
        # 分别求出每个模态的均值和标准差
        means.append(data.mean(axis=(1, 2, 3)))
        stds.append(data.std(axis=(1, 2, 3)))
    # 求每个模态在所有样本上的均值和标准差[n_example,4]==>[4]
    mean = np.asarray(means).mean(axis=0)
    std = np.asarray(stds).mean(axis=0)
    print(mean,std)
    for index in range(data_storage.shape[0]):
        # 根据均值和标准差对每一个样本归一化
        data_storage[index] = normalize_data(data_storage[index], mean, std)
    return data_storage