# import logging
# import time
# from contextlib import contextmanager
# from unittest import TestCase
#
# import imagehash
# # import numpy as numpy
# # import vptree as vptree
# from sqlalchemy.orm import Session
#
# from tdb.cardbot.crud.card import Card
# from tdb.cardbot.database import SessionLocal
#
# # from typing import List
#
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('PIL').setLevel(logging.WARNING)
#
#
# @contextmanager
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# class TestMTGJson(TestCase):
#     # def test_process_all_printings(self):
#     #     print()
#
#     def test_hash(self):
#         files = [
#             '/home/tdblack/Downloads/Regeneration.png',
#             '/home/tdblack/Downloads/Counterspell.png',
#             '/home/tdblack/Downloads/Swamp.png'
#         ]
#
#         hash_sizes = [8, 16, 32, 64, 128]
#
#         for filename in files:
#             for hash_size in range(48, 49):
#                 store_time = time.time()
#                 h = hashing.Hash.compute_hash(filename=filename, hash_size=hash_size, crop_box='TOP')
#                 # hash_time = (time.time() - store_time)
#                 # print('record_time', record_time)
#                 p = f'filename: {filename} | hash_size: {hash_size} | {len(str(h))} | {h}|'
#                 print('hash_time', (time.time() - store_time), p)
#                 # print('')
#
#             print('')
#             print('')
#
#     def test_hash_table_memory(self):
#         files = [
#             '/home/tdblack/Downloads/Regeneration.png',
#             '/home/tdblack/Downloads/Counterspell.png',
#             '/home/tdblack/Downloads/Swamp.png'
#         ]
#
#         hash_column = [
#             'phash_32',
#             # 'top_48',
#             # 'bottom_48'
#         ]
#
#         db: Session
#         with get_db() as db:
#             # hashes = {}
#
#             hash_records = {
#                 hash_size: {}
#                 for hash_size in hash_column
#             }
#
#             store_time = time.time()
#
#             records = Card.read_all_hashes(db)
#
#             record_time = (time.time() - store_time)
#             print('record_time', record_time)
#
#             # ids = []
#
#             # hash8 = []
#             # hash16 = []
#             # hash32 = []
#
#             # hash8_records = {}
#             # hash16_records = {}
#             # hash32_records = {}
#
#             store_time = time.time()
#
#             for record in records:
#                 # hash8.append(record.phash_48)
#                 # hash16.append(record.phash_64)
#
#                 for hash_size in hash_column:
#                     record_hash = getattr(record, hash_size)
#                     if record_hash:
#                         hash_records[hash_size][record_hash] = {
#                             'record': record,
#                             'imagehash': imagehash.hex_to_hash(record_hash)
#                         }
#
#                 # if record.phash_32:
#                 #     # ids.append(record.uuid)
#                 #
#                 #     # hash32_uuid[record.phash_32] = record.uuid
#                 #     hash32_records[record.phash_32] = record
#                 #
#                 #     hash32.append(imagehash.hex_to_hash(record.phash_32))
#
#             dict_time = (time.time() - store_time)
#             print('dict_time', dict_time)
#
#             # hash32_np = numpy.array(hash32)
#             print()
#
#             # store_time = time.time()
#             #
#             # def hamming(a, b):
#             #     # compute and return the Hamming distance between the integers
#             #     # return bin(int(a) ^ int(b)).count("1")
#             #     return a - b
#             #
#             # trees = {
#             #     hash_size: vptree.VPTree(hash_records[hash_size].keys(), hamming)
#             #     for hash_size in hash_sizes
#             # }
#             #
#             # tree_time = (time.time() - store_time)
#             # print('tree_time', tree_time)
#
#             for filename in files:
#                 store_time = time.time()
#
#                 test_values = {}
#
#                 image = hashing.Hash._open_image(filename)
#                 test_values['phash_32'] = hashing.Hash.phash(image, hash_size=32, high_freq_factor=16)
#
#                 dict_time = (time.time() - store_time)
#                 print(filename.split('/')[-1], 'phash_32', dict_time)
#
#                 # store_time = time.time()
#                 #
#                 # top_image = hashing.Hash.crop(image, 'TOP')
#                 # test_values['top_48'] = hashing.Hash.phash(top_image, hash_size=48)
#                 #
#                 # dict_time = (time.time() - store_time)
#                 # print(filename.split('/')[-1], 'top_48', dict_time)
#                 #
#                 # store_time = time.time()
#                 #
#                 # bottom_image = hashing.Hash.crop(image, 'BOTTOM')
#                 # test_values['bottom_48'] = hashing.Hash.phash(bottom_image, hash_size=48)
#                 #
#                 # dict_time = (time.time() - store_time)
#                 # print(filename.split('/')[-1], 'bottom_48', dict_time)
#
#                 for hash_size in hash_column:
#                     store_time = time.time()
#
#                     for _ in range(1):
#                         diffs = {
#                             key: details['imagehash'] - test_values[hash_size]
#                             for key, details in hash_records[hash_size].items()
#                             # if details['imagehash'] - test < 300
#                         }
#
#                     dict_time = (time.time() - store_time)
#                     print(filename.split('/')[-1], hash_size, 'imagehash', dict_time)
#
#                     store_time = time.time()
#
#                     closest_key = min(diffs, key=diffs.get)
#                     closest_val = min(diffs.values())
#                     avg_val = sum(diffs.values()) / len(diffs)
#                     max_val = max(diffs.values())
#
#                     record: Card = hash_records[hash_size][closest_key]['record']
#
#                     dict_time = (time.time() - store_time)
#                     print(filename.split('/')[-1], hash_size, 'record', closest_val, avg_val, max_val, dict_time, record.searchName, record.setCode)
#                     print()
