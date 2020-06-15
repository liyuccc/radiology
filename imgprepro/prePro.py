# -*-coding:utf-8-*-
import os
import shutil
import SimpleITK as sitk
import warnings
import glob
import numpy as np
from nipype.interfaces.ants import N4BiasFieldCorrection

from dipy.align.reslice import reslice
from dipy.io.image import load_nifti, save_nifti


def correct_bias(in_file, out_file, image_type=sitk.sitkFloat64):
    """
    Corrects the bias using ANTs N4BiasFieldCorrection. If this fails, will then attempt to correct bias using SimpleITK
    :param in_file: nii文件的输入路径
    :param out_file: 校正后的文件保存路径名
    :return: 校正后的nii文件全路径名
    """
    # 使用N4BiasFieldCorrection校正MRI图像的偏置场
    correct = N4BiasFieldCorrection()
    correct.inputs.input_image = in_file
    correct.inputs.output_image = out_file
    try:
        done = correct.run()
        return done.outputs.output_image
    except IOError:
        warnings.warn(RuntimeWarning("ANTs N4BIasFieldCorrection could not be found."
                                     "Will try using SimpleITK for bias field correction"
                                     " which will take much longer. To fix this problem, add N4BiasFieldCorrection"
                                     " to your PATH system variable. (example: EXPORT PATH=${PATH}:/path/to/ants/bin)"))
        input_image = sitk.ReadImage(in_file, image_type)
        output_image = sitk.N4BiasFieldCorrection(input_image, input_image > 0)
        sitk.WriteImage(output_image, out_file)
        return os.path.abspath(out_file)


def normalize_image(in_file, out_file, bias_correction=True):
    # bias_correction：是否需要校正
    if bias_correction:
        correct_bias(in_file, out_file)
    else:
        shutil.copy(in_file, out_file)
    return out_file


def corr_field(input_path, output_path, modal, modal_corr):
    # input_patient_list = sorted([os.path.join(input_path, item, modal)
    #                              for item in os.listdir(input_path)])
    #
    # output_patient_list = sorted([os.path.join(output_path, item, modal_corr)
    #                               for item in os.listdir(input_path)])

    input_patient_list = sorted([os.path.join(input_path, item)
                                 for item in os.listdir(input_path)])

    output_patient_list = sorted([os.path.join(output_path, item[:-4]+modal_corr)
                                  for item in os.listdir(input_path)])
    for id, path in enumerate(input_patient_list):
        if not os.path.exists(os.path.split(output_patient_list[id])[0]):
            os.makedirs(os.path.split(output_patient_list[id])[0])
        print(f'Correcting the offset field of',
              os.path.split(os.path.split(input_patient_list[id])[0])[1],
              'and storing it to ', os.path.split(output_patient_list[id]))
        normalize_image(input_patient_list[id],output_patient_list[id])


def re_sample(input_path_img, input_path_label, output_path_img, out_path_label, new_voxel_size):

    data, affine, voxel_size = load_nifti(input_path_img, return_voxsize=True)
    label, affine_label, voxel_size1 = load_nifti(input_path_label, return_voxsize=True)
    print('Before', data.shape, voxel_size)
    print('label Before', label.shape, voxel_size1)

    data2, affine2 = reslice(data, affine, voxel_size, new_voxel_size)
    print('After resample:', data2.shape, new_voxel_size)

    label2, affine_label2 = reslice(label, affine_label, voxel_size1, new_voxel_size)
    print('label After resample:', label2.shape, new_voxel_size)

    save_nifti(output_path_img, data2, affine2)
    save_nifti(out_path_label, label2, affine_label2)



