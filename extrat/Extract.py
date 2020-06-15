import os
import six
from radiomics import featureextractor, setVerbosity
from radiomics.featureextractor import RadiomicsFeatureExtractor
from openpyxl import Workbook
from extrat import fileHanding

# import settings file
params = './mine.yaml'
# obtain the feature extractor class with the setting file
extractor = RadiomicsFeatureExtractor(params)
# enable or disable
extractor.addProvenance(provenance_on=False)

setVerbosity(60)

file = Workbook()
table = file.create_sheet('data')
dataDir = '/media/lyu/841G/DATA/Gliomas/img'
ROIDir = '/media/lyu/841G/DATA/Gliomas/Converted_ROI'

# 分四个list存不同的ROI
nangbian_mask,shizhi_mask,zhongliu_mask,shuizhong_mask,bingbian_mask = fileHanding.classifyROI(ROIDir)
print(nangbian_mask)
# 分别读取不同的ROI对应的img
#fileHanding.extract_save(extractor, nangbian_mask, dataDir, ROIDir,'nangbian')
#fileHanding.extract_save(extractor, shizhi_mask, dataDir, ROIDir,'shizhi')
fileHanding.extract_save(extractor, zhongliu_mask, dataDir, ROIDir,'zhongliu')
#fileHanding.extract_save(extractor, shuizhong_mask, dataDir, ROIDir,'shuizhong')
#fileHanding.extract_save(extractor, bingbian_mask, dataDir, ROIDir,'bingbian')
