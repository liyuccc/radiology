import numpy as np
import scipy.io as mat
import os
import pydicom


def rescale_range(I, N1, N2, range_data=None):
    """
    Rescale data into a specified range.
    RESCALE_RANGE(I,N1,N2) rescales the array I so that all elements fall in
    the range [N1,N2]. The output is double or single precision.
    :return:Iout,N2high
    """

    #  Convert input to double precision
    if I.dtype != 'float64':
        I = I.astype(float)
    N1 = float(N1)
    N2 = float(N2)

    #  Make sure the data can be rescaled with the current machine precision
    if range_data:
        range_data = float(range_data)
        datarange = np.max(range_data) - np.min(range_data)
    else:
        datarange = np.max(I) - np.min(I)

    EPS = 2.2204e-16
    if datarange>EPS:
        wantedrange = N2 - N1
        Iout = N1+(I-np.min(I))/(datarange/wantedrange)
    else:
        Iout = I

    return Iout

def topclip(data,*altdata,numstd=5):
    # Clipping the top end of the histogram/distribution
    data_noz = np.delete(data, np.where(data==0))
    topclipval = np.median(data_noz) + numstd*np.std(data_noz)
    data_clipped = data

    numvals_top = len(np.where(data_clipped>topclipval))
    data_clipped[np.where(data_clipped>topclipval)] = np.round(
        np.linspace(topclipval, topclipval-np.std(data[np.where(data!=0)]), numvals_top))
    if altdata:
        altdata = altdata[0]
        topclipval = topclipval * np.max(altdata[np.where(altdata!=0)])/np.max(data[np.where(data!=0)])
        altdata_clipped = altdata
        numvals_top = len(np.where(altdata_clipped > topclipval))
        altdata_clipped[np.where(altdata_clipped > topclipval)] = np.round(
            np.linspace(topclipval - np.std(data(np.where(data != 0))), topclipval, numvals_top))


def botclip(data,*altdata,numstd=5):
    # Clipping the bottom end of the histogram/distribution
    global altdata_clipped
    data_noz = np.delete(data, np.where(data == 0))
    botclipval = np.median(data_noz) - numstd * np.std(data_noz)
    data_clipped = data
    numvals_bot = len(np.where(data_clipped < botclipval))
    data_clipped[np.where(data_clipped < botclipval)] = np.round(
        np.linspace(botclipval+ np.std(data[np.where(data != 0)]), botclipval, numvals_bot))
    if altdata:
        altdata = altdata[0]
        botclipval = botclipval * np.max(altdata)/np.max(data)
        altdata_clipped = altdata
        numvals_bot = len(np.where(altdata_clipped[np.where(altdata_clipped!=0)] < botclipval))
        altdata_clipped[np.where(altdata_clipped[np.where(altdata_clipped!=0)] < botclipval)] = np.round(
            np.linspace(botclipval + np.std(data[np.where(data != 0)]), botclipval, numvals_bot))
    return data_clipped,altdata_clipped


def dicomInformation():

    path = '/media/zzr/My Passport/newMRI/Raw'
    data = []
    for idx, case in enumerate(os.listdir(path)):
        print(idx)
        case_path = os.path.join(path, case)
        for i in os.listdir(case_path):
            nrrd = [j for j in os.listdir(os.path.join(case_path, i)) if j.endswith('nrrd') & ('T1' in j)]
            if nrrd:
                dicom_file = [jj for jj in os.listdir(os.path.join(case_path, i)) if jj.endswith('dcm')]
                dicom = pydicom.read_file(os.path.join(os.path.join(case_path, i), dicom_file[0]))
                spacing = str(dicom.PixelSpacing[0])
                rows = str(dicom.Rows)
                columns = str(dicom.Columns)
                sliceThickness = str(dicom.SliceThickness)
                try:
                    sliceSpacing = str(dicom.SpacingBetweenSlices)
                except AttributeError:
                    sliceSpacing = str(dicom.SliceThickness)

                manufacturer = str(dicom.Manufacturer)
                data.append(case + '+' + spacing + '+' + rows + '+' + columns + '+'
                            + manufacturer + '+' + sliceThickness + '+' + sliceSpacing)
                break

    mat.savemat('/media/zzr/My Passport/newMRI/T1Information.mat', {'data': data})