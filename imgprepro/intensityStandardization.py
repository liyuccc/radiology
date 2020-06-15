import numpy as np
from imgprepro.tool import rescale_range, topclip, botclip

# Have to figure out the top and bottom ends of the standardization map separately
def calc_stdn_map(indata, templdata, landmarks):
    in_01 = round(max(indata) * .01)
    in_99 = round(max(indata) * .99)
    in_max = round(max(indata))
    templ_01 = round(max(templdata) * .01)

    botperc = np.zeros((in_01, 2))
    botperc[:, 0]=np.reshape(np.arange(1,in_01+1),(in_01,1))
    topperc = np.zeros((in_max-in_99+1, 2))
    topperc[:, 0] = np.reshape(np.arange(in_99, in_max + 1), (in_max + 1 - in_99, 1))

    # Initialize the middle part of the standardization map
    intensity_range = in_99 - in_01
    standmap = np.zeros((intensity_range + 1, 2))
    standmap[:, 0] = np.arange(1, intensity_range + 2)

    # Now intialize the 'segments' within the map
    L = np.shape(landmarks)
    segments = np.ones((L[0]+2,L[1]))
    segments[segments.shape[0]-1,0] = intensity_range+1
    segments[segments.shape[0] - 1, 1] = max(templdata) - min(templdata) + 1

    # Set the minimum of 'segments' as 1
    segments[0, 0] = 1
    segments[0, 1] = 1

    # Check for landmarks, modify segments accordingly
    assert segments[1:L[0]+1,:].shape == landmarks.shape
    if landmarks.size>0:
        segments[1:L[0]+1,:] = landmarks

    # Scale within each 'segment'
    for seg in range(0,segments.shape[0]-1):
        # Initialize
        segms = np.arange(segments[seg,0],segments[seg+1,0])
        pre_scaling = np.reshape(np.round(segms),(len(segms),1))

        # Scale
        post_scaling = pre_scaling - min(pre_scaling)
        scalefactor = (segments[seg + 1, 1] - segments[seg, 1]) / \
                      (max(post_scaling) - min(post_scaling))
        post_scaling = post_scaling * scalefactor
        post_scaling = post_scaling + segments[seg, 2]

        # Storing the scale factors to apply to the top and bottom ends of the map later
        if seg==0:
            scalefactends = scalefactor
        elif seg == segments.shape[0]-2:
            scalefactends = scalefactends.append(scalefactor)

        standmap[pre_scaling[0]:pre_scaling[len(pre_scaling)-1],1] = post_scaling

    # Apply scale factors to the top and bottom ends of the map
    botperc[:, 1]=botperc[:, 0]*scalefactends[0]
    topperc[:, 1] = topperc[:, 0] * scalefactends[1]

    # Add back the minimums
    standmap[:, 0]=standmap[:, 0]+in_01 - 1
    standmap[:, 1]=standmap[:, 1]+templ_01 - 1
    standardization_map = np.append(botperc,standmap,topperc,axis=0)

    # Round off any decimals
    standardization_map = np.round(standardization_map)

    return standardization_map


def apply_stdn_map(input_volume,standardization_map):
    input_volume[np.where(np.isnan(input_volume) == True)] = min[input_volume]
    input_volints = list(set(input_volume.reshape(input_volume.size,)))
    output_volume = input_volume
    for i in range(1,len(input_volints)):
        output_volume[np.where(input_volume == input_volints[i])] = \
            standardization_map(np.round(input_volints[i]), 1)

    return output_volume


def int_stdn_landmarks_multiTemplate(inputvolume, templatedata, templvol_lm, **dict):
    # get information in dict
    # cancer masks for input non-standardized data
    if 'incancermasks' not in dict.keys():
        incancermasks = []
    else:
        incancermasks = dict['incancermasks']

    # Data values WILL be top-clipped (improves contrast)   (need topclip)
    if 'numstdtopclip' not in dict.keys():
        numstdtopclip = 5
    else:
        numstdtopclip = dict['numstdtopclip']

    # bottom-clipped    (need botclip)
    if 'numstdbotclip' not in dict.keys():
        numstdbotclip = 0
    else:
        numstdbotclip = dict['numstdbotclip']

    # zeroval
    if 'zeroval' not in dict.keys():
        zeroval = 0
    else:
        zeroval = dict['zeroval']

    # dorescale         (need rescale_range)
    if 'dorescale' not in dict.keys():
        dorescale = True
    else:
        dorescale = dict['dorescale']

    # rescaleMax
    if 'rescaleMax' not in dict.keys():
        rescaleMax = 4095
    else:
        rescaleMax = dict['rescaleMax']

    # check if (inputvolume[:] int)
    checkifInt = np.where(inputvolume!=0)
    checkifInt = inputvolume(checkifInt[1])
    if np.ceil(checkifInt)!=np.floor(checkifInt):
        inputvolume = np.round(inputvolume)

    # Linear rescaling of intensity ranges
    if dorescale:
        inputvolume = np.round(rescale_range(inputvolume, 0, rescaleMax))

    # Sorting,vectorizing
    inputdata = np.reshape(np.sort(np.reshape(inputvolume,(np.size(inputvolume),))),
                           (-1,1))

    # Remove zeros
    inputdata = np.delete(inputdata, np.where(inputdata==0))

    # Remove cancer masks
    indata_forlm = inputvolume
    indata_forlm[np.where(incancermasks==1)] = 0
    indata_forlm = np.delete(indata_forlm,np.where(indata_forlm<=0))

    # Vectorize if not already vector (can happen for 2D images)
    if indata_forlm.shape[0]!=1 and indata_forlm.shape[1]!=1:
        indata_forlm = np.reshape(indata_forlm,(-1, 1))

    # Find landmarks at every 10th percentile
    percentiles = np.arange(10, 100, 10)
    inputvol_lm = np.reshape(np.percentile(indata_forlm, percentiles),(-1,1))
    landmarks = np.append(inputvol_lm, templvol_lm, axis=1)

    # Calculate standardization_map
    standardization_map = calc_stdn_map(inputdata, templatedata, landmarks)

    # Apply standardization_map to standardize the inputvolume
    outputvolume = apply_stdn_map(inputvolume, standardization_map)

    # Clip outliers coz they mess up the image
    if numstdtopclip:
        outputdata = np.reshape(np.sort(np.reshape(outputvolume, (-1,1))),(-1, 1))
        outputdata = np.delete(outputdata, np.where(outputdata<=0))
        if np.where(outputvolume > np.median(outputdata)+numstdtopclip*np.std(outputdata)):
            outputvolume = topclip(outputvolume, [], numstdtopclip)
            if numstdbotclip:
                if np.where(outputvolume<np.median(outputdata)-numstdbotclip*np.std(outputdata)):
                    outputvolume = botclip(outputvolume, [], numstdbotclip)

    return outputvolume, standardization_map