import numpy as np
import pandas as pd

# Person correlation coefficient
def person(vector1, vector2):
    data = pd.DataFrame({
        'vector1': vector1,
        'vector2': vector2})
    person = data.corr()
    return person.values[0, 1]

# rank-sum test   ???

#
if __name__=='__main__':
    vector1 = [2, 7, 18, 88, 157, 90, 177, 570]
    vector2 = [3, 5, 15, 90, 180, 88, 160, 580]
    del vector1[1]
    print(vector1)
