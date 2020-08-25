import pandas as pd
import numpy as np
import cv2


# TODO: add check if img & params already exist
# TODO: add clean-up of old files whne app starts
# TODO: fit image width to size of browser

class ImageEditor():

    def __init__(self, input_img):

        # open image
        self.image_name = input_img.split('.')[0]
        self.original_img = cv2.imread('input/' + input_img, 1)
        self.original_img = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)

        #self.img = self.original_img

        # chart parameters
        self.n_colours = None
        self.n_stitches = None
        self.n_rows = None
        self.row_gauge = None
        self.stitch_gauge = None

        # pixels per stitch, pixels per row

        # TODO: find a better solution than hardcoding this value
        self.PPS = 10
        self.PPR = None


    def resize(self, image):

        # resize to display 5-pixels wide per stitch
        final_width = self.n_stitches * self.PPS
        final_height = self.n_rows * self.PPR

        # resize from the original img so no info is lost
        resized_img = cv2.resize(image, dsize=(final_width, final_height))

        print(f'Verify image size (n_rows * PPR = final_height): {self.n_rows} * {self.PPR} = {final_height}')
        if self.n_rows * self.PPR != final_height:
            raise Exception("TIFF - check the row math for rounding errors")
        else:
            print('OK')

        return resized_img



    def add_gridlines(self, image, gridline_colour = (0,255,0)):

        # veritcal lines
        for i in range(0, self.n_stitches*self.PPS, self.PPS):
            cv2.line(
                img = image,
                pt1 = (i, 0),
                pt2 = (i, self.n_rows*self.PPR),
                color = gridline_colour,
                thickness = 1
            )

        # horizontal lines
        for i in range(0, self.n_rows*self.PPR, self.PPR):
            cv2.line(
                img = image,
                pt1 = (0, i),
                pt2 = (self.n_stitches*self.PPS, i),
                color = gridline_colour,
                thickness = 1
            )

        return image



    def save_img(self, image):

        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

        save_img_name = 'static/'+'_'.join([
            self.image_name,
            str(self.n_colours),
            str(self.n_stitches),
            str(self.row_gauge),
            str(self.stitch_gauge)
        ])+'.png'

        cv2.imwrite(save_img_name, image)
        print('Image saved as {}'.format(save_img_name))



    def fit(self, n_colours, n_stitches, row_gauge, stitch_gauge):

        self.n_colours = n_colours
        self.n_stitches = n_stitches
        self.row_gauge = row_gauge
        self.stitch_gauge = stitch_gauge

        self.PPR = int(self.PPS * self.row_gauge / self.stitch_gauge)
        self.n_rows = int(self.n_stitches * self.PPR / self.PPS)

        img = self.resize(self.original_img)


        Z = img.reshape((-1, 3))
        Z = np.float32(Z)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(Z, self.n_colours, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)


        label_result = label.reshape(img.shape[0], img.shape[1])
        center = np.uint8(center)
        #result = center[label.flatten()]
        #result = result.reshape((img.shape))

        label_colour = {i: center[i] for i in range(len(center))}

        for r in range(0, self.n_rows*self.PPR, self.PPR):
            for s in range(0, self.n_stitches*self.PPS, self.PPS):
                labels_in_stitch = label_result[r:r+self.PPR, s:s+self.PPS].flatten()
                most_frequent_label = np.argmax(np.bincount(labels_in_stitch))
                img[r:r+self.PPR,s:s+self.PPS,:] = label_colour[most_frequent_label]
        img = self.add_gridlines(img)
        self.save_img(img)