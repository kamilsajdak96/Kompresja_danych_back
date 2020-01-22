import cv2
import numpy as np
import time

from myapp.imageTester import saveImage


class LusakujaAlgorithm:
    # decide if want to use a mask for y channel
    use_mask = True

    # value used when calculating how pixel can differ from each other
    # and we decide that we assign 0 instead of this value
    # should be <2,5>
    diff_threshold_value = 3
    diff_threshold_vale_max = 5

    # parameters for display for each channel in ycrcb
    start_size = [0, 0, 0]
    mask_size = [0, 0, 0]
    difference_size = [0, 0, 0]
    rlc_size = [0, 0, 0]
    size_before = 0
    size_after = 0

    compression_result_time = 0
    decompression_result_time = 0
    @staticmethod
    def get_difference_between_img(img_1, img_2):
        height_1, width_1, channel_1 = img_1.shape
        height_2, width_2, channel_2 = img_2.shape
        if height_1 != height_2 or width_1 != width_2 or channel_1 != channel_2:
            return -1

        sum_channel = [0, 0, 0]

        for c in range(channel_1):
            for h in range(height_1):
                for w in range(width_1):
                    sum_channel[c] = sum_channel[c] + abs(int(img_1[h][w][c]) - int(img_2[h][w][c]))

        sum = sum_channel[0] + sum_channel[1] + sum_channel[2]
        return sum, sum_channel

    @staticmethod
    def convert_to_rlc(input: list) -> list:
        """
        Converting to rlc list
        :param input: list
        :return:
        """
        rlc = []
        last_val = input[0]
        count = 1
        # iterate over vars to get rlc list
        for i in range(1, len(input)):
            if last_val == input[i]:
                count = count + 1
            else:
                rlc.append(count)
                rlc.append(last_val)
                last_val = input[i]
                count = 1
        # add last element
        rlc.append(count)
        rlc.append(last_val)
        return rlc

    def convert_to_difference_list(self, input: list) -> list:
        """
        Convert list to list composed of first pixel + different value to previous pixel
        :param input: list to convert
        :return:
        """
        diff_list = []
        diff_list.append(input[0])
        residue = 0
        append_var = 0
        converted_var = input[0]
        for i in range(1, len(input)):
            # calculate difference value between two pixels
            diff = int(input[i]) - int(input[i - 1])

            # if difference is less than diff_max_value
            if abs(diff) < self.diff_threshold_value:
                residue = residue + diff
                diff = 0

            if abs(residue) > self.diff_threshold_vale_max or converted_var + diff > 254 or converted_var+diff<0:
                append_var = diff + residue
                residue = 0
            else:
                append_var = diff
            diff_list.append(append_var)
            converted_var = converted_var + append_var
        return diff_list

    def apply_luminance_mask(self, input) -> list:
        mask_list = []

        if self.use_mask:
            for i in range(len(input)):
                # first or third row from three row pattern
                if i % 3 != 1:
                    for j in range(len(input[i])):
                        mask_list.append(input[i][j])
                # second row from three row pattern
                else:
                    for j in range(len(input[i])):
                        # get only first or third pixel in second row
                        if j % 3 == 0 or j % 3 == 2:
                            mask_list.append(input[i][j])
        else:
            for i in range(len(input)):
                for j in range(len(input[i])):
                    mask_list.append(input[i][j])
                    #print(input[i][j])
        return mask_list

    def apply_chromaticity_mask(self, input):
        mask_list = []
        for i in range(len(input)):
            if i % 3 == 1:
                for j in range(len(input[i])):
                    if j % 3 == 1:
                        mask_list.append(input[i][j])
        return mask_list

    def compute_conversion_list(self, channel, display_num: int, channel_type: str) -> list:
        """
        Get converted list for y channel
        :param channel: input array from opencv for one channel
        :param display_num: nummer of channel in display
        :param channel_type: 'y' - luminance, 'c' - chromaticity
        :return: list after conversion
        """
        # display
        self.start_size[display_num] = len(channel)*len(channel[0])

        # iterate over pixels with the mask pattern for y channel
        if channel_type == 'y':
            mask_list = self.apply_luminance_mask(channel)
        elif channel_type == 'c':
            mask_list = self.apply_chromaticity_mask(channel)

        # display
        self.mask_size[display_num] = len(mask_list)

        # make list with difference pixel values
        diff_list = self.convert_to_difference_list(mask_list)

        #display
        self.difference_size[display_num] = len(diff_list)

        # rlc conversion
        rlc_list = self.convert_to_rlc(diff_list)
        self.rlc_size[display_num] = len(rlc_list)

        return rlc_list



    def decompress_rlc(self, input: list) -> list:
        """
        # decompression from rlc
        :param input: compressed list using RLC method
        :return: decompresed list
        """
        d_rlc = []
        for i in range(0, int(len(input) / 2)):
            for j in range(input[2 * i]):
                d_rlc.append(input[2 * i + 1])
        return d_rlc

    def decompress_difference_computation(self, input : list):
        """
        Decompressing from difference computation
        :param input: compressed list using difference computation
        :return: decompressed list
        """
        d_dif = []
        d_dif.append(input[0])
        # get from dif
        for i in range(0, len(input)-1):
            dif = d_dif[i]+input[i+1]
            d_dif.append(dif)
        return d_dif

    def unapply_luminance_mask(self, input: list, width: int) -> list:
        output = []
        index = 0
        row = 0

        if self.use_mask:
            while True:
                if index == len(input):
                    break
                if row == 0 or row == 2:
                    for j in range(width):
                        if index == len(input):
                            break
                        output.append(input[index])
                        index = index + 1
                    row = row + 1
                    if row > 2:
                        row = 0
                else:
                    for j in range(width):
                        if j % 3 == 0 or j % 3 == 2:
                            output.append(input[index])
                            index = index + 1
                        else:
                            output.append(input[index-1])
                    row = row + 1
        else:
            while True:
                if index == len(input):
                    break

                for j in range(width):
                    if index == len(input):
                        break
                    output.append(input[index])
                    index = index + 1
        return output

    def unapply_chromaticity_mask(self, input, width, height) -> list:
        output = []

        tmp_row = []
        index = 0
        row_counter = 0
        pixels_in_row = int(width/3)
        if width % 3 > 0:
            pixels_in_row = pixels_in_row + 1

        for i in range(len(input)):
            if index < pixels_in_row:
                tmp_row.append(input[i])
                index = index + 1

                if index == pixels_in_row:
                    index = 0
                    for col in range(3):
                        if row_counter < height:
                            index_counter = 0
                            for j in range(len(tmp_row)):
                                for k in range(3):
                                    if index_counter < width:
                                        output.append(tmp_row[j])
                                    index_counter = index_counter + 1
                            row_counter = row_counter + 1
                    if i + 1 != len(input):
                        tmp_row = []
        if row_counter != height:
            for j in range(len(tmp_row)):
                for k in range(3):
                    output.append(tmp_row[j])
        return output

    def decompress_channel(self, input_list, width, height, channel_type):

        d_rlc = self.decompress_rlc(input_list)

        d_dif = self.decompress_difference_computation(d_rlc)

        if channel_type == 'y':
            decompressed = self.unapply_luminance_mask(d_dif, width)
        elif channel_type == 'c':
            decompressed = self.unapply_chromaticity_mask(d_dif, width, height)
        else:
            decompressed = None

        return decompressed

    def reshape_to_arrays(self, y_list, cr_list, cb_list, height, width):
        y = np.reshape(y_list, (int(width), int(height)))
        cr = np.reshape(cr_list, (int(width), int(height)))
        cb = np.reshape(cb_list, (int(width), int(height)))
        y_out = y.astype(np.uint8)
        cr_out = cr.astype(np.uint8)
        cb_out = cb.astype(np.uint8)

        return y_out, cr_out, cb_out

    def decompress_image(self, input_img):
        startTime = time.time()
        width = input_img[0]
        height = input_img[1]
        y_input = input_img[2]
        cr_input = input_img[3]
        cb_input = input_img[4]
        y_output = self.decompress_channel(y_input, width, None, 'y')
        cr_output = self.decompress_channel(cr_input, width, height, 'c')
        cb_output = self.decompress_channel(cb_input, width, height, 'c')
        endTime = time.time()
        self.decompression_result_time = endTime - startTime

        return self.reshape_to_arrays(y_output, cr_output, cb_output, width, height)

    def display_size(self):
        for i in range(3):
            print(i)
            print(self.start_size[i])
            print(self.mask_size[i])
            print(self.difference_size[i])
            print(self.rlc_size[i])

        print("Przed kompresja: "+ str(self.size_before))
        print("Po kompresji: " + str(self.size_after))
        print("Stopień kompresja: " + str(self.size_after/self.size_before))

    def start(self, image_path: str):
        startTime = time.time()
        # reading image
        img = cv2.imread(image_path)
        height, width, channel = img.shape
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        b, g, r = cv2.split(img)
        y, cr, cb = cv2.split(ycrcb)

        # data compression
        y_arr = self.compute_conversion_list(y, 0, 'y')
        cr_arr = self.compute_conversion_list(cr, 1, 'c')
        cb_arr = self.compute_conversion_list(cb, 2, 'c')
        # end of data compression

        img_compressed = [width, height, y_arr, cr_arr, cb_arr]

        # data decompression
        y_after, cr_after, cb_after = self.decompress_image(img_compressed)
        ycrcb_image = cv2.merge([y_after, cr_after, cb_after])
        rgb = cv2.cvtColor(ycrcb_image, cv2.COLOR_YCrCb2BGR)

        # compression parameters
        self.size_before = height * width * channel
        self.size_after = len(y_arr) + len(cr_arr) + len(cb_arr) + 1

        # cv2.imshow('IMG', img)
        # cv2.imshow('RGB', rgb)
        cv2.imwrite('C:/Users/Kamil/Desktop/Kompresja/Kompresja/lusakuja.jpg', rgb)
        cv2.waitKey()
        dif, channel_dif = self.get_difference_between_img(img, rgb)
        print("Różnica między obrazkami: " + str(dif) + ". Kanały: " + str(channel_dif[0]) + " / " + str(
            channel_dif[1]) + " / " + str(channel_dif[2]) + " / ")
        print("Średnio na piksel: " + str(dif / height / width))
        endTime = time.time()
        self.compression_result_time = endTime - startTime
        print("Czas wykonania: ")
        print(self.compression_result_time)
        print("Czas wykonania dekompresji: ")
        print(self.decompression_result_time)
        saveImage("C:/Users/Kamil/Desktop/Kompresja/Kompresja/lusakuja.jpg",
                  "C:/Users/Kamil/Desktop/Kompresja/Kompresja/Lusakuja.txt")

        return [self.compression_result_time, self.decompression_result_time]

def main(path):
    alg = LusakujaAlgorithm()
    alg.start('C:/Users/Kamil/Desktop/Kompresja/Kompresja/imageTest.png')
    alg.display_size()

def times():
    alg = LusakujaAlgorithm()
    return alg.start('C:/Users/Kamil/Desktop/Kompresja/Kompresja/imageTest.png')

if __name__ == "__main__":
    main('C:/Users/Kamil/Desktop/Kompresja/Kompresja/imageTest.png')