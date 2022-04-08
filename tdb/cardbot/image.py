import io
import pathlib
from typing import Union, Optional, IO

from PIL import Image as PillowImage


class Image:
    def __init__(self, context: Union[pathlib.Path, io.BytesIO, Optional[IO]]):
        self.original_image = PillowImage.open(context)

        max_height = 500

        resize_ratio = max_height / self.original_image.size[1]

        new_size = (int(self.original_image.size[0] * resize_ratio), int(self.original_image.size[1] * resize_ratio))

        self.modified_image = self.original_image.resize(new_size)


class ImageStore:
    def __init__(self):
        self.img: Optional[Image] = None
