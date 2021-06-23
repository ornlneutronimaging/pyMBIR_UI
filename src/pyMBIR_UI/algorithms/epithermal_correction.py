import numpy as np


def epithermal_correction(image=None, threshold=0):
    if threshold == 0:
        return image

    image_temp = np.array(image, dtype=np.float32)
    thr = np.logical_xor(image_temp > (threshold*np.median(image_temp)),
                         image_temp < (np.median(image_temp)/threshold))
    img_adp = np.copy(image_temp)
    index = np.nonzero(thr)
    thresh = np.shape(index)[1]
    sub = np.copy(np.median(image_temp))
    for i in range(thresh):
        img_adp[index[0][i], index[1][i]] = sub
    for i in range(thresh):
        img_adp[index[0][i], index[1][i]] = np.median(img_adp[index[0][i]-2:index[0][i]+3,
                                                      index[1][i]-2:index[1][i]+3])

    return img_adp
