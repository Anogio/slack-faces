from io import BytesIO

import requests
from PIL import Image
from cachetools import cached, LRUCache

from flask import send_file


def send_picture_file(picture_to_guess):
    img_io = BytesIO()
    picture_to_guess.save(img_io, "JPEG", quality=100)
    img_io.seek(0)
    picture_to_send = send_file(img_io, mimetype="image/jpeg")
    return picture_to_send


@cached(cache=LRUCache(maxsize=1024))
def get_downscaled_image(image_url: str, target_resolution: int) -> Image:
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_small = img.resize(
        (target_resolution, target_resolution), resample=Image.BILINEAR
    )
    return img_small.resize(img.size, Image.NEAREST)
