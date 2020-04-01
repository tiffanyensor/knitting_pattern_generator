from config import *
import pandas as pd
import numpy as np
import cv2

def generate_pattern(input_img, n_col, width):

    # read in img
    img = cv2.imread(input_img, 1)
    ho, wo, co = img.shape

    Z = img.reshape((-1, 3))
    Z = np.float32(Z)

    # apply k means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(Z, n_col, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # map label to colours
    label_colour = {i:center[i] for i in range(len(center))}

    label_result = label.reshape(ho,wo)
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape((img.shape))

    # calculate number of pixels per row (ppr) and pixels per stitch (pps)
    h, w, c = result.shape
    st_ratio = 5/7  # assume 5:7 stitch height:width

    # TODO: round these down
    pps = round(w/width)
    ppr = round(pps * st_ratio)

    height = int(h * ppr)


    # find locations of grid marks
    wp_all = list(range(0, wo, pps))
    hp_all = list(range(0, ho, ppr))

    # crop image to remove partial stitches
    result = result[0:max(hp_all), 0:max(wp_all), :]

    for i in range(1,len(wp_all)):
        for j in range(1,len(hp_all)):
            wl = wp_all[i-1]
            wu = wp_all[i]

            hl = hp_all[j-1]
            hu = hp_all[j]

            labels = label_result[hl:hu, wl:wu]
            #if len(labels)==0:
            #    continue
            #else:
            labels = list(labels[0])
            most_frequent_label = max(set(labels), key = labels.count)
            result[hl:hu, wl:wu, :] = label_colour[most_frequent_label]

    #TODO: resize image larger so grid lines appear thin
    # draw gridlines
    for wp in wp_all:
        cv2.line(result, (wp, 0), (wp, ho), (0, 255, 0), 1)
    for hp in hp_all:
        cv2.line(result, (0, hp), (wo, hp), (0, 255, 0), 1)

    # save result
    cv2.imwrite('output/img.png', result)
    print('Result saves as output/img.png')


if __name__=='__main__':

    generate_pattern('input/flower1.jpg', N_COLOURS, ST_WIDTH)