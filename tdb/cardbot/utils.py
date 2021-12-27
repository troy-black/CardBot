import json
import logging
import lzma
import os
import tempfile
from pathlib import Path
from typing import TextIO

import requests


def download_file(url: str, *, filename: str = None) -> dict:
    request = requests.get(url, allow_redirects=True, stream=True)
    size: int = int(request.headers.get('Content-Length', 0))

    if filename:
        os.makedirs(Path(filename).parent, exist_ok=True)
        streamer = open(filename, 'wb')
    else:
        streamer = tempfile.TemporaryFile()
        filename = url.split('/')[-1]

    saved = 0
    data = {'filename': filename}

    with streamer as file:
        for chunk in request.iter_content(chunk_size=1048576):
            if chunk:
                file.write(chunk)
                saved += len(chunk)
                logging.debug(f'Downloading "{filename}": {round((saved / size) * 100, 2) if size else saved}%')

        if filename.lower().split('.')[-1] == 'xz':
            file.seek(0)
            data = decompress_json(file)

        elif filename.lower().split('.')[-1] == 'json' or filename == 'bulk-data':
            file.seek(0)
            data = json.load(file)

    return data


def decompress_json(file: TextIO):
    with lzma.open(file, mode='rt') as lzma_file:
        data = json.load(lzma_file)

    return data
