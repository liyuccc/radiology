import os
import six
from radiomics import featureextractor, setVerbosity
from radiomics.featureextractor import RadiomicsFeatureExtractor
from openpyxl import Workbook
from extrat import fileHanding

# import settings file
params = './MR.yaml'
# obtain the feature extractor class with the setting file
extractor = RadiomicsFeatureExtractor(params)
# enable or disable
extractor.addProvenance(provenance_on=False)

setVerbosity(60)

file = Workbook()
table = file.create_sheet('data')
dataDir = '/media/lyu/841G/DATA/Gliomas/IntensityStandardizationNii'
ROIDir = '/media/lyu/841G/DATA/Gliomas/IntensityStandardizationNii'
Resample = ['Original', '1', '2', '3', '4', '5']
fileHanding.extract_save(extractor, dataDir,'zhongliu', Resample)

