import pandas as pd
import numpy as np
import cv2
import glob

# TODO: fit image width to size of browser


class ImageEditor():

    def __init__(self, input_img):

        # files
        self.image_name = input_img.split('.')[0]
        self.image_ext = input_img.split('.')[1]
        self.saved_name = None

        # images
        self.original_img = cv2.cvtColor(cv2.imread('./input/'+input_img, 1), cv2.COLOR_BGR2RGB)
        self.image = self.original_img

        # chart parameters
        self.n_colours = None
        self.n_stitches = None
        self.n_rows = None
        self.row_gauge = None
        self.stitch_gauge = None
        self.blur = None
        self.colour_swatches = {}


    def prepare_img(self):

        print('n stitches = ', self.n_stitches)
        print('n rows = ', self.n_rows)

        # resize, bring back to original proportions, add gridlines
        pixels_per_st = 10
        #pixels_per_row = round(pixels_per_st * self.n_stitches/self.n_rows)
        pixels_per_row = round(pixels_per_st * self.stitch_gauge / self.row_gauge)
        #self.n_stitches * self.row_gauge / self.stitch_gauge

        print('pixels per stitch = ', pixels_per_st)
        print('pixels per row = ', pixels_per_row)

        desired_height = pixels_per_row*self.n_rows
        desired_width = pixels_per_st*self.n_stitches

        print('desired width = ', desired_width)
        print('desired height = ', desired_height)

        resized_img = np.zeros(shape=[desired_height, desired_width, self.image.shape[2]], dtype=np.uint8)

        for h in range(self.n_rows):
            for w in range(self.n_stitches):
                resized_img[h*pixels_per_row:(h+1)*pixels_per_row, w*pixels_per_st:(w+1)*pixels_per_st,:] = self.image[h,w,:]

        self.image = resized_img



    def draw_gridlines(self, w_major=10, h_major = 10, major_colour=(255,0,0), minor_colour=(255,255,255)):

        width_per_pixel = 10
        height_per_pixel = round(width_per_pixel * self.stitch_gauge / self.row_gauge)

        # vertical grid
        for w in range(self.n_stitches):
            gridline_colour = major_colour if w % w_major==0 else minor_colour
            cv2.line(
                img=self.image,
                pt1=(w * width_per_pixel, 0),
                pt2=(w * width_per_pixel, self.image.shape[0]),
                color=gridline_colour,
                thickness=1
            )

        # horizontal grid
        for h in range(self.n_rows):
            gridline_colour = major_colour if h % h_major==0 else minor_colour
            # horizontal grid
            cv2.line(
                img=self.image,
                pt1=(0, h * height_per_pixel),
                pt2=(self.image.shape[1], h * height_per_pixel),
                color=gridline_colour,
                thickness=1
            )


    def save_img(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGBA2BGRA)
        print('Image saved as {}'.format(self.saved_name))
        cv2.imwrite('./static/'+self.saved_name, self.image)


    def update_colour(self):
        # manually update one of the colours and re-cluster
        pass


    def cluster(self):

        pixelated_img = cv2.resize(self.image, dsize=(self.n_stitches, self.n_rows))

        # clustering on pixels
        Z = pixelated_img.reshape((-1, 3))
        Z = np.float32(Z)

        #self.image = cv2.GaussianBlur(self.image, (5, 5), 0)

        criteria = (cv2.TERM_CRITERIA_MAX_ITER, 200, 1.0)
        ret, label, center = cv2.kmeans(Z, self.n_colours, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        #label_result = label.reshape(img.shape[0], img.shape[1])
        center = np.uint8(center)

        self.colour_swatches[self.saved_name] = center
        self.image = center[label.flatten()].reshape((pixelated_img.shape))



    def fit(self, n_colours, n_stitches, row_gauge, stitch_gauge, blur):

        self.n_colours = n_colours
        self.n_stitches = n_stitches
        self.row_gauge = row_gauge
        self.stitch_gauge = stitch_gauge
        self.blur = blur

        self.n_rows = int(self.n_stitches * self.row_gauge / self.stitch_gauge)

        self.saved_name = '_'.join([
            self.image_name,
            str(self.n_colours),
            str(self.n_stitches),
            str(self.row_gauge),
            str(self.stitch_gauge),
            str(self.blur)
        ])+'.png'


        self.image = cv2.fastNlMeansDenoisingColored(
            self.image,
            None,
            h = self.blur,
            hColor = 10,
            templateWindowSize = 7,
            searchWindowSize = 21
        )
        #cv2.imwrite('./input/denoised.png', cv2.cvtColor(self.image, cv2.COLOR_RGBA2BGRA))


        # if the combination of params has been done already, img already exists
        if './static/'+self.saved_name not in glob.glob('./static/*.png'):
            self.cluster()
            self.prepare_img()
            self.draw_gridlines()
            self.save_img()

        else:
            self.cluster()