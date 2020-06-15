import numpy as np
from collections import Counter
import scipy.signal as signal
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def plotdist(data,linecolor):
    # Check if data Int
    checkdata = np.reshape(data, (-1,1))
    for i in range(0, data.shape[0]*data.shape[1]):
        if checkdata[i]!=0:
            checkifInt = checkdata[i]
            break

    if np.ceil(checkifInt)!=np.floor(checkifInt):
        print('Rounding non-integer values in DATA')
        data = np.round(data)

    # Statistical histogram
    count = Counter(np.squeeze(data))
    keys = list(count.keys())
    values = list(count.values())
    if 0 in keys:
        index = keys.index(0)
        keys.remove(0)
        values.remove(values[index])
    keys = np.reshape(np.array(keys),(1,-1))
    values = np.reshape(np.array(values),(1,-1))

    k = np.ones((1, 25))*(1/25)
    smoothhist = signal.convolve(values/np.sum(values), k, mode='same')
    plt.plot(keys,smoothhist,'r', lw=0.5)
    plt.show()
