import json
import logging
import lzma
from typing import TextIO

import requests
import tempfile

from pathlib import Path


# def decompress_lzma(filename: str):
#     new_filename = filename[:filename.rindex('.')]
#
#     chunks = 0
#     with open(new_filename, 'w') as new_file:
#         with lzma.open(filename, mode='rt') as file:
#             while True:
#                 data = str(file.read(1024))
#
#                 if data:
#                     new_file.write(data)
#                     chunks += len(data)
#                     print(chunks)
#
#                 else:
#                     print('COMPLETE!!!')
#                     break
#
#

def download_file(url: str, *, filename: str = None) -> dict:
    request = requests.get(url, allow_redirects=True, stream=True)
    size: int = int(request.headers['Content-Length'])

    if filename:
        streamer = open(filename, 'wb')
    else:
        streamer = tempfile.TemporaryFile()
        filename = url.split('/')[-1]

    chunks = 0
    data = {'filename': filename}

    with streamer as file:
        for chunk in request.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                chunks += len(chunk)
                logging.debug(f'Downloading "{filename}": {round((chunks / size) * 100, 2)}%')

        if Path(filename).suffix.lower() == '.xz':
            file.seek(0)
            data = decompress_json(file)

    return data


def decompress_json(file: TextIO):
    with lzma.open(file, mode='rt') as lzma_file:
        data = json.load(lzma_file)

    return data


# def read_json(filename: str):
#     with open(filename) as file:
#         data = json.load(file)
#
#     return data
