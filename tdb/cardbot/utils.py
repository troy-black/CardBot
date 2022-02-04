import json
import logging
import lzma
import os
import tempfile
from pathlib import Path
from typing import TextIO

import requests


def download_file(url: str, *, filename: str = None) -> dict:
    """
    Download file from url

    :param url: URL to download from
    :param filename: Optional filename to save download to. If not provided a TemporaryFile will be used.
    :return: Dict with details on the downloaded file. If the file is serializable; its internal data will be returned.
             Otherwise, information on the downloaded file's location will be returned.
    """
    request = requests.get(url, allow_redirects=True, stream=True)
    size: int = int(request.headers.get('Content-Length', 0))

    if filename:
        # Open filename location for streaming
        os.makedirs(Path(filename).parent, exist_ok=True)
        streamer = open(filename, 'wb')

    else:
        # Create temp file location for streaming
        filename = url.split('/')[-1]
        streamer = tempfile.TemporaryFile()

    data = {
        'filename': filename
    }

    saved = 0
    with streamer as file:
        # Chunk file and provide details as received
        for chunk in request.iter_content(chunk_size=1048576):
            if chunk:
                file.write(chunk)
                saved += len(chunk)
                logging.debug(f'Downloading "{filename}": {round((saved / size) * 100, 2) if size else saved}%')

        if filename.lower().split('.')[-1] == 'xz':
            # Decompress LZMA/LZMA2 json file
            file.seek(0)
            data = decompress_json(file)

        elif filename.lower().split('.')[-1] == 'json' or filename == 'bulk-data':
            # Deserialize json file
            file.seek(0)
            data = json.load(file)

    logging.debug(f'Downloaded "{filename}": {max(saved, size)}b')

    return data


def decompress_json(file: TextIO):
    """
    Decompress a JSON file stored as LZMA/LZMA2
    :param file: TextIO bytes
    :return: dict from json
    """
    with lzma.open(file, mode='rt') as lzma_file:
        data = json.load(lzma_file)

    return data
