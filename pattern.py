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
    pps = int(w/width)
    ppr = int(pps * st_ratio)

    # expand so divider lines stay thin
    if pps < 5:
        pixel_multiplier = 5
    else:
        pixel_multiplier = 1

    # find locations of grid marks
    wp_all = list(range(0, wo+pps, pps))
    hp_all = list(range(0, ho+ppr, ppr))

    final = np.zeros(shape=[max(hp_all)*pixel_multiplier, max(wp_all)*pixel_multiplier, c], dtype=np.uint8)
    hf, wf, cf = final.shape

    for i in range(1,len(wp_all)):
        for j in range(1,len(hp_all)):
            wl = wp_all[i-1]
            wu = wp_all[i]

            hl = hp_all[j-1]
            hu = hp_all[j]

            labels = label_result[hl:hu, wl:wu]
            labels = list(labels[0])
            most_frequent_label = max(set(labels), key = labels.count)

            final[pixel_multiplier*hl:pixel_multiplier*hu, pixel_multiplier*wl:pixel_multiplier*wu, :] = label_colour[most_frequent_label]

    # draw gridlines
    for wp in wp_all:
        cv2.line(final, (pixel_multiplier*wp, 0), (pixel_multiplier*wp, pixel_multiplier*hf), (0, 255, 0), 1)
    for hp in hp_all:
        cv2.line(final, (0, pixel_multiplier*hp), (pixel_multiplier*wf, pixel_multiplier*hp), (0, 255, 0), 1)

    # save result
    cv2.imwrite('output/img.png', final)
    print('Result saves as output/img.png')


if __name__=='__main__':

    generate_pattern('input/flower1.jpg', N_COLOURS, ST_WIDTH)