from imgprepro.prePro import corr_field,re_sample
import os

# MRI offset field correction
''''''
input_path = '/media/lyu/841G/DATA/Gliomas/New/3DT1_lianying'
output_path = '/media/lyu/841G/DATA/Gliomas/New/img_corr'
modal = '3DT1.nii'
modal_corr = '_corr.nii'
corr_field(input_path,output_path,modal,modal_corr)



# # Resample
# input_path_img = '/media/lyu/841G/DATA/Gliomas/ALL_img'
# output_path = '/media/lyu/841G/DATA/Gliomas/img_Resample'
# modal = '3DT1.nii'
# modal_resample = '3DT1_resample.nii'
# input_patient_list = sorted([os.path.join(input_path_img, item, modal)
#                                  for item in os.listdir(input_path_img)])
#
# input_path_label = '/media/lyu/841G/DATA/Gliomas/Converted_ROI'
# ROI = 'zhongliu.nii'
# label_resample = 'zhongliu_resample.nii'
# input_label_list = sorted(os.path.join(input_path_label,item,roi)
#                     for item in os.listdir(input_path_label)
#                     for roi in os.listdir(os.path.join(input_path_label,item))
#                     if roi.endswith(ROI))
#
# new_voxel_size_list = [(1., 1., 1.), (2., 2., 2.), (3., 3., 3.), (4., 4., 4.), (5., 5., 5.)]
#
# for new_voxel_size in new_voxel_size_list:
#     modal_resample_path = os.path.join(str(int(new_voxel_size[0])), modal_resample)
#     output_patient_list = sorted([os.path.join(output_path, item, modal_resample_path)
#                                   for item in os.listdir(input_path_img)])
#     roi_resample_path = os.path.join(str(int(new_voxel_size[0])), label_resample)
#     output_label_list = sorted([os.path.join(output_path, item, roi_resample_path)
#                                   for item in os.listdir(input_path_img)])
#     for id, path in enumerate(input_patient_list):
#         if not os.path.exists(os.path.split(output_patient_list[id])[0]):
#             os.makedirs(os.path.split(output_patient_list[id])[0])
#         print(os.path.split(os.path.split(input_patient_list[id])[0])[1],modal,
#               'is now being resampled and stored to', os.path.split(output_patient_list[id])[0])
#         re_sample(input_patient_list[id], input_label_list[id], output_patient_list[id], output_label_list[id],new_voxel_size=new_voxel_size)