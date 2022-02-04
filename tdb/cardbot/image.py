import logging
from pathlib import Path

import imagehash
import numpy
import scipy.fftpack
from PIL import ImageFile, Image as PillowImage

from tdb.cardbot import config

ImageFile.LOAD_TRUNCATED_IMAGES = True


class Image:
    def __init__(self, path: Path, *, alpha_filter: bool = True):
        """
        Load an image (png) file into memory to perform image filtering and cropping before building a phash

        :param path: Path of image to load
        :param alpha_filter: Run an alpha filter on image before building phash
        """
        self.path = path

        self.pillow_image = None
        self._open_image()

        if alpha_filter:
            self._alpha_filter()

    def _alpha_filter(self):
        """
        Perform alpha filter on image to convert to pure RGB
        """
        if self.pillow_image.mode == 'RGBA':
            canvas = PillowImage.new('RGBA', self.pillow_image.size, (255, 255, 255, 255))
            canvas.paste(self.pillow_image, mask=self.pillow_image)

            self.pillow_image = canvas.convert('RGB')

    def _open_image(self):
        """
        Open image (png) and resize to a base height (1000px)
        """
        # logging.debug(f'{self.thread_id}Opening Image: {self.filename}')

        image = PillowImage.open(self.path)
        width, height = image.size

        # resize image to have a set base height
        size_diff = config.Config.hash_pixels_height / height
        new_width = int(width * size_diff)
        new_height = int(height * size_diff)

        self.pillow_image = image.resize((new_width, new_height))

    def image_hash(self, hash_size: int = 48, high_freq_factor: int = 4, transform: bool = True) -> imagehash.ImageHash:
        """
        Perform phash on loaded image

        :param hash_size: Hash size to use for phash algorythm
        :param high_freq_factor: Frequency used for phash algorythm
        :param transform: Run a z-transform on image before building phash
        :return: imagehash.ImageHash containing phash and tools to compare
        """
        # try:
        img_size = hash_size * high_freq_factor
        image = self.pillow_image.convert("L").resize((img_size, img_size), PillowImage.ANTIALIAS)

        if transform:
            image = self.z_transform(image)

        pixels = numpy.asarray(image)
        dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
        dct_low_freq = dct[:hash_size, :hash_size]
        med = numpy.median(dct_low_freq)
        diff = dct_low_freq > med
        image_hash = imagehash.ImageHash(diff)

        logging.debug(f'ImageHash: {image_hash}')

        return image_hash
        # except Exception as e:
        #     logging.error(f'Unable to perform phash [{filename}]: {e}', exc_info=True)
        #     return {}

    @staticmethod
    def z_transform(image: PillowImage) -> PillowImage:
        """
        Perform z-transform on image

        :param image: PIL Image
        :return: PIL Image
        """
        # logging.debug(f'{self.thread_id}Performing z_transform')

        data = image.getdata()
        quantiles = numpy.arange(100)
        quantiles_values = numpy.percentile(data, quantiles)
        z_data = (numpy.interp(data, quantiles_values, quantiles) / 100 * 255).astype(numpy.uint8)
        image.putdata(z_data)

        return image
