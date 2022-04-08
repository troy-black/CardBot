import io
import logging
import math
from itertools import product
from pathlib import Path
from typing import List, Optional, IO
from typing import Union

import cv2
import imagehash
import numpy
import scipy.fftpack
import scipy.fftpack
from PIL import ImageFile, Image as PillowImage
from numpy.typing import NDArray
from shapely.affinity import scale
from shapely.geometry import Polygon, LineString
from sklearn.neighbors import NearestNeighbors
from sqlalchemy.engine import Row

from tdb.cardbot.core import database
from tdb.cardbot.core.crud import card

ImageFile.LOAD_TRUNCATED_IMAGES = True


class HashImage:
    original_image: PillowImage.Image
    modified_image: PillowImage.Image
    hashed_image: PillowImage.Image
    phash_diff_image: PillowImage.Image

    image_hash: imagehash.ImageHash

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    # TODO - This should be config via WebUI
    target_coords = [
        (68, 414),
        (954, 429),
        (940, 1690),
        (41, 1658)
    ]

    def __init__(self, context: Union[Path, io.BytesIO, Optional[IO]], hash_size: int = 32, high_freq: int = 4):
        self.original_image = image = PillowImage.open(context)

        nparray: NDArray = self.histogram_adjust(image.__array__())

        if not isinstance(context, Path):
            # Only run transforms on uploaded images
            nparray = self.contour_image(nparray)

        original_pillow_image = PillowImage.fromarray(nparray)

        max_height = 500

        resize_ratio = max_height / original_pillow_image.size[1]

        new_size = (
            int(original_pillow_image.size[0] * resize_ratio), int(original_pillow_image.size[1] * resize_ratio))

        self.modified_image = original_pillow_image.resize(new_size)

        # if not hash_size:
        #     return
        #
        # if hash_size == 128:
        #     high_freq = 1

        self.hashed_image: PillowImage.Image = self.new_prep_phash_img(
            img_size=(hash_size * high_freq, hash_size * high_freq))
        diff = self.new_calculate_phash_diff(self.hashed_image.__array__(), hash_size=(hash_size, hash_size))

        self.phash_diff_image: PillowImage.Image = PillowImage.fromarray(diff)

        self.image_hash = imagehash.ImageHash(diff)

        # base_w, base_h = 745, 1040
        # w, h = original_pillow_image.size
        #
        # pw = w / base_w
        # ph = h / base_h
        #
        # # left, top, right, bottom
        # rc = (int(643 * pw), int(588 * ph), int(692 * pw), int(642 * ph))
        # header = (int(96 * pw), int(30 * ph), int(352 * pw), int(130 * ph))
        # footer = (int(23 * pw), int(971 * ph), int(45 * pw), int(1015 * ph))
        #
        # self.modified_image_header = original_pillow_image.crop(header)
        # self.modified_image_footer = original_pillow_image.crop(footer)
        # self.modified_image_rc = original_pillow_image.crop(rc)
        #
        # # header
        # self.hashed_image_header = self.new_prep_phash_img(img_size=(hash_size, hash_size),
        #                                                    pillow_image=self.modified_image_header)
        # diff_header = self.new_calculate_phash_diff(self.hashed_image_header.__array__(),
        #                                             hash_size=(hash_size, hash_size))
        # self.phash_diff_image_header: PillowImage.Image = PillowImage.fromarray(diff_header)
        #
        # # footer
        # self.hashed_image_footer = self.new_prep_phash_img(img_size=(hash_size, hash_size),
        #                                                    pillow_image=self.modified_image_footer)
        # diff_footer = self.new_calculate_phash_diff(self.hashed_image_footer.__array__(),
        #                                             hash_size=(hash_size, hash_size))
        # self.phash_diff_image_footer: PillowImage.Image = PillowImage.fromarray(diff_footer)
        #
        # # set symbol
        # self.hashed_image_rc = self.new_prep_phash_img(img_size=(hash_size, hash_size),
        #                                                pillow_image=self.modified_image_rc)
        # diff_rc = self.new_calculate_phash_diff(self.hashed_image_rc.__array__(),
        #                                         hash_size=(hash_size, hash_size))
        # self.phash_diff_image_rc: PillowImage.Image = PillowImage.fromarray(diff_rc)
        #
        # self.image_hash_header = imagehash.ImageHash(diff_header)
        # self.image_hash_footer = imagehash.ImageHash(diff_footer)
        # self.image_hash_rc = imagehash.ImageHash(diff_rc)

    def new_prep_phash_img(self, img_size: tuple[int, int],
                           pillow_image: PillowImage.Image = None) -> PillowImage.Image:
        image = pillow_image or self.modified_image

        image = image.convert("L")

        image = image.resize(img_size, PillowImage.ANTIALIAS)

        return image

    @staticmethod
    def new_calculate_phash_diff(ndarray: NDArray, hash_size: tuple[int, int]) -> NDArray:
        pixels = numpy.asarray(ndarray)

        dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)

        dctlowfreq = dct[:hash_size[1], :hash_size[0]]

        med = numpy.median(dctlowfreq)

        diff = dctlowfreq > med

        return diff

    # ################################################## #
    # Magic Card Detecter... TODO
    # ################################################## #
    @classmethod
    def contour_image(cls, cv2_img) -> NDArray:
        possible_card_contours = {}

        # contours = cls.contour_image_gray(cv2_img, thresholding='simple')
        contours = cls.contour_image_gray(cv2_img, thresholding='adaptive')
        contours += cls.contour_image_rgb(cv2_img)

        image_area = cv2_img.shape[0] * cv2_img.shape[1]

        for contour in contours:
            try:
                if contour.shape[0] < 3:
                    continue

                convex_hull_polygon = cls.convex_hull_polygon(contour)

                if not convex_hull_polygon or convex_hull_polygon.area < image_area / 1000:
                    continue

                bounding_polygon = cls.get_bounding_quad(convex_hull_polygon)

                if not bounding_polygon:
                    continue

                crop_factor = min(1., (1. - cls.quad_corner_diff(convex_hull_polygon, bounding_polygon) * 22. / 100.))

                scaled_polygon = scale(bounding_polygon,
                                       xfact=crop_factor,
                                       yfact=crop_factor,
                                       origin='centroid')

                coords = list(zip(*scaled_polygon.exterior.coords.xy))[:-1]

                coords_diff = [
                    math.sqrt(
                        (coords[r][0] - cls.target_coords[r][0]) ** 2 + (coords[r][1] - cls.target_coords[r][1]) ** 2)
                    for r in range(4)
                ]

                if max(coords_diff) < 25:
                    warped = cls.four_point_transform(cv2_img, scaled_polygon)
                    possible_card_contours[min(coords_diff)] = (coords, warped)

            except Exception as e:
                print(e)

        if possible_card_contours:
            coords, closest_contour_image = possible_card_contours[min(possible_card_contours.keys())]

            # cls.average_coords = [
            #     ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2)
            #     for c, a in zip(coords, cls.average_coords)
            # ]
        else:
            closest_contour_image = cls.four_point_transform(cv2_img, Polygon(cls.target_coords))

        return closest_contour_image

    @classmethod
    def contour_image_gray(cls, full_image, thresholding='adaptive'):
        """
        Grayscale transform, thresholding, countouring and sorting by area.
        """
        gray = cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)
        if thresholding == 'adaptive':
            fltr_size = 1 + 2 * (min(full_image.shape[0], full_image.shape[1]) // 20)
            thresh = cv2.adaptiveThreshold(gray,
                                           255,
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY,
                                           fltr_size,
                                           10)
        else:
            thresh = cv2.threshold(gray,
                                   70,
                                   255,
                                   cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(numpy.uint8(thresh), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours

    @classmethod
    def contour_image_rgb(cls, full_image):
        """
        Grayscale transform, thresholding, countouring and sorting by area.
        """
        blue, green, red = cv2.split(full_image)
        blue = cls.clahe.apply(blue)
        green = cls.clahe.apply(green)
        red = cls.clahe.apply(red)
        _, thr_b = cv2.threshold(blue, 110, 255, cv2.THRESH_BINARY)
        _, thr_g = cv2.threshold(green, 110, 255, cv2.THRESH_BINARY)
        _, thr_r = cv2.threshold(red, 110, 255, cv2.THRESH_BINARY)
        contours_b, _ = cv2.findContours(numpy.uint8(thr_b), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_g, _ = cv2.findContours(numpy.uint8(thr_g), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_r, _ = cv2.findContours(numpy.uint8(thr_r), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours_b + contours_g + contours_r

        return contours

    @classmethod
    def convex_hull_polygon(cls, contour):
        """
        Returns the convex hull of the given contour as a polygon.
        """
        hull = cv2.convexHull(contour)
        phull = Polygon([[x, y] for (x, y) in
                         zip(hull[:, :, 0], hull[:, :, 1])])
        return phull

    @classmethod
    def four_point_transform(cls, image, poly):
        """
        A perspective transform for a quadrilateral polygon.
        Slightly modified version of the same function from
        https://github.com/EdjeElectronics/OpenCV-Playing-Card-Detector
        """
        pts = numpy.zeros((4, 2))
        pts[:, 0] = numpy.asarray(poly.exterior.coords)[:-1, 0]
        pts[:, 1] = numpy.asarray(poly.exterior.coords)[:-1, 1]
        # obtain a consistent order of the points and unpack them
        # individually
        rect = numpy.zeros((4, 2))
        (rect[:, 0], rect[:, 1]) = cls.order_polygon_points(pts[:, 0], pts[:, 1])

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        # width_a = numpy.sqrt(((b_r[0] - b_l[0]) ** 2) + ((b_r[1] - b_l[1]) ** 2))
        # width_b = numpy.sqrt(((t_r[0] - t_l[0]) ** 2) + ((t_r[1] - t_l[1]) ** 2))
        width_a = numpy.sqrt(((rect[1, 0] - rect[0, 0]) ** 2) +
                             ((rect[1, 1] - rect[0, 1]) ** 2))
        width_b = numpy.sqrt(((rect[3, 0] - rect[2, 0]) ** 2) +
                             ((rect[3, 1] - rect[2, 1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        height_a = numpy.sqrt(((rect[0, 0] - rect[3, 0]) ** 2) +
                              ((rect[0, 1] - rect[3, 1]) ** 2))
        height_b = numpy.sqrt(((rect[1, 0] - rect[2, 0]) ** 2) +
                              ((rect[1, 1] - rect[2, 1]) ** 2))
        max_height = max(int(height_a), int(height_b))

        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order

        rect = numpy.array([
            [rect[0, 0], rect[0, 1]],
            [rect[1, 0], rect[1, 1]],
            [rect[2, 0], rect[2, 1]],
            [rect[3, 0], rect[3, 1]]], dtype="float32")

        dst = numpy.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        # compute the perspective transform matrix and then apply it
        transform = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, transform, (max_width, max_height))

        # return the warped image
        return warped

    @classmethod
    def generate_point_indices(cls, index_1, index_2, max_len):
        """
        Returns the four indices that give the end points of
        polygon segments corresponding to index_1 and index_2,
        modulo the number of points (max_len).
        """
        return numpy.array([index_1 % max_len, (index_1 + 1) % max_len,
                            index_2 % max_len, (index_2 + 1) % max_len])

    @classmethod
    def generate_quad_candidates(cls, in_poly):
        """
        Generates a list of bounding quadrilaterals for a polygon,
        using all possible combinations of four intersection points
        derived from four extended polygon segments.
        The number of combinations increases rapidly with the order
        of the polygon, so simplification should be applied first to
        remove very short segments from the polygon.
        """
        # make sure that the points are ordered
        (x_s, y_s) = cls.order_polygon_points(
            numpy.asarray(in_poly.exterior.coords)[:-1, 0],
            numpy.asarray(in_poly.exterior.coords)[:-1, 1])
        x_s_ave = numpy.average(x_s)
        y_s_ave = numpy.average(y_s)
        x_shrunk = x_s_ave + 0.9999 * (x_s - x_s_ave)
        y_shrunk = y_s_ave + 0.9999 * (y_s - y_s_ave)
        shrunk_poly = Polygon([[x, y] for (x, y) in
                               zip(x_shrunk, y_shrunk)])
        quads = []
        len_poly = len(x_s)

        for indices in product(range(len_poly), repeat=4):
            (xis, yis) = cls.generate_quad_corners(indices, x_s, y_s)
            if (numpy.sum(numpy.isnan(xis)) + numpy.sum(numpy.isnan(yis))) > 0:
                # no intersection point for some of the lines
                pass
            else:
                (xis, yis) = cls.order_polygon_points(xis, yis)
                enclose = True
                quad = Polygon([(xis[0], yis[0]),
                                (xis[1], yis[1]),
                                (xis[2], yis[2]),
                                (xis[3], yis[3])])
                if not quad.contains(shrunk_poly):
                    enclose = False
                if enclose:
                    quads.append(quad)
        return quads

    @classmethod
    def generate_quad_corners(cls, indices, x, y):
        """
        Returns the four intersection points from the
        segments defined by the x coordinates (x),
        y coordinates (y), and the indices.
        """
        (i, j, k, l) = indices

        def gpi(index_1, index_2):
            return cls.generate_point_indices(index_1, index_2, len(x))

        xis = numpy.empty(4)
        yis = numpy.empty(4)
        xis.fill(numpy.nan)
        yis.fill(numpy.nan)

        if j <= i or k <= j or l <= k:
            ...
        else:
            (xis[0], yis[0]) = cls.line_intersection(x[gpi(i, j)], y[gpi(i, j)])
            (xis[1], yis[1]) = cls.line_intersection(x[gpi(j, k)], y[gpi(j, k)])
            (xis[2], yis[2]) = cls.line_intersection(x[gpi(k, l)], y[gpi(k, l)])
            (xis[3], yis[3]) = cls.line_intersection(x[gpi(l, i)], y[gpi(l, i)])

        return xis, yis

    @classmethod
    def get_bounding_quad(cls, hull_poly):
        """
        Returns the minimum area quadrilateral that contains (bounds)
        the convex hull (openCV format) given as input.
        """
        simple_poly = cls.simplify_polygon(hull_poly)
        bounding_quads = cls.generate_quad_candidates(simple_poly)
        bquad_areas = numpy.zeros(len(bounding_quads))
        for iquad, bquad in enumerate(bounding_quads):
            bquad_areas[iquad] = bquad.area
        min_area_quad = bounding_quads[numpy.argmin(bquad_areas)]

        return min_area_quad

    @classmethod
    def histogram_adjust(cls, nparray: NDArray) -> NDArray:
        """
        Adjusts the image by contrast limited histogram adjustmend (clahe)
        """
        lab = cv2.cvtColor(nparray, cv2.COLOR_BGR2LAB)
        blue, green, red = cv2.split(lab)
        corrected_blue = cls.clahe.apply(blue)
        corrected_image = cv2.merge((corrected_blue, green, red))
        adjusted = cv2.cvtColor(corrected_image, cv2.COLOR_LAB2BGR)

        return adjusted

    @classmethod
    def line_intersection(cls, x, y):
        """
        Calculates the intersection point of two lines, defined by the points
        (x1, y1) and (x2, y2) (first line), and
        (x3, y3) and (x4, y4) (second line).
        If the lines are parallel, (nan, nan) is returned.
        """
        slope_0 = (x[0] - x[1]) * (y[2] - y[3])
        slope_2 = (y[0] - y[1]) * (x[2] - x[3])
        if slope_0 == slope_2:
            # parallel lines
            xis = numpy.nan
            yis = numpy.nan
        else:
            xy_01 = x[0] * y[1] - y[0] * x[1]
            xy_23 = x[2] * y[3] - y[2] * x[3]
            denom = slope_0 - slope_2

            xis = (xy_01 * (x[2] - x[3]) - (x[0] - x[1]) * xy_23) / denom
            yis = (xy_01 * (y[2] - y[3]) - (y[0] - y[1]) * xy_23) / denom

        return xis, yis

    @classmethod
    def order_polygon_points(cls, x, y):
        """
        Orders polygon points into a counterclockwise order.
        x_p, y_p are the x and y coordinates of the polygon points.
        """
        angle = numpy.arctan2(y - numpy.average(y), x - numpy.average(x))
        ind = numpy.argsort(angle)
        return x[ind], y[ind]

    @classmethod
    def quad_corner_diff(cls, hull_poly, bquad_poly, region_size=0.9):
        """
        Returns the difference between areas in the corners of a rounded
        corner and the aproximating sharp corner quadrilateral.
        region_size (param) determines the region around the corner where
        the comparison is done.
        """
        bquad_corners = numpy.zeros((4, 2))
        bquad_corners[:, 0] = numpy.asarray(bquad_poly.exterior.coords)[:-1, 0]
        bquad_corners[:, 1] = numpy.asarray(bquad_poly.exterior.coords)[:-1, 1]

        # The point inside the quadrilateral, region_size towards the quad center
        interior_points = numpy.zeros((4, 2))
        interior_points[:, 0] = numpy.average(bquad_corners[:, 0]) + region_size * (
                bquad_corners[:, 0] - numpy.average(bquad_corners[:, 0]))
        interior_points[:, 1] = numpy.average(bquad_corners[:, 1]) + region_size * (
                bquad_corners[:, 1] - numpy.average(bquad_corners[:, 1]))

        # The points p0 and p1 (at each corner) define the line whose intersections
        # with the quad together with the corner point define the triangular
        # area where the roundness of the convex hull in relation to the bounding
        # quadrilateral is evaluated.
        # The line (out of p0 and p1) is constructed such that it goes through the
        # "interior_point" and is orthogonal to the line going from the corner to
        # the center of the quad.
        p0_x = interior_points[:, 0] + (bquad_corners[:, 1] - numpy.average(bquad_corners[:, 1]))
        p1_x = interior_points[:, 0] - (bquad_corners[:, 1] - numpy.average(bquad_corners[:, 1]))
        p0_y = interior_points[:, 1] - (bquad_corners[:, 0] - numpy.average(bquad_corners[:, 0]))
        p1_y = interior_points[:, 1] + (bquad_corners[:, 0] - numpy.average(bquad_corners[:, 0]))

        corner_area_polys = []
        for i in range(len(interior_points[:, 0])):
            bline = LineString([(p0_x[i], p0_y[i]), (p1_x[i], p1_y[i])])
            try:
                corner_area_polys.append(Polygon(
                    [bquad_poly.intersection(bline).coords[0],
                     bquad_poly.intersection(bline).coords[1],
                     (bquad_corners[i, 0], bquad_corners[i, 1])]))
            except Exception as e:
                print(e)

        hull_corner_area = 0
        quad_corner_area = 0
        for capoly in corner_area_polys:
            quad_corner_area += capoly.area
            hull_corner_area += capoly.intersection(hull_poly).area

        return 1. - hull_corner_area / quad_corner_area

    @classmethod
    def simplify_polygon(cls, in_poly,
                         length_cutoff=0.15,
                         maxiter=None,
                         segment_to_remove=None):
        """
        Removes segments from a (convex) polygon by continuing neighboring
        segments to a new point of intersection. Purpose is to approximate
        rounded polygons (quadrilaterals) with more sharp-cornered ones.
        """

        x_in = numpy.asarray(in_poly.exterior.coords)[:-1, 0]
        y_in = numpy.asarray(in_poly.exterior.coords)[:-1, 1]
        len_poly = len(x_in)
        niter = 0
        if segment_to_remove is not None:
            maxiter = 1
        while len_poly > 4:
            d_in = numpy.sqrt(numpy.ediff1d(x_in, to_end=x_in[0] - x_in[-1]) ** 2. +
                              numpy.ediff1d(y_in, to_end=y_in[0] - y_in[-1]) ** 2.)
            d_tot = numpy.sum(d_in)
            if segment_to_remove is not None:
                k = segment_to_remove
            else:
                k = numpy.argmin(d_in)
            if d_in[k] < length_cutoff * d_tot:
                ind = cls.generate_point_indices(k - 1, k + 1, len_poly)
                (xis, yis) = cls.line_intersection(x_in[ind], y_in[ind])
                x_in[k] = xis
                y_in[k] = yis
                x_in = numpy.delete(x_in, (k + 1) % len_poly)
                y_in = numpy.delete(y_in, (k + 1) % len_poly)
                len_poly = len(x_in)
                niter += 1
                if (maxiter is not None) and (niter >= maxiter):
                    break
            else:
                break

        out_poly = Polygon([[ix, iy] for (ix, iy) in zip(x_in, y_in)])

        return out_poly


class HashRow:
    def __init__(self, _id: str, record_hash: str, hash_header: str = None, hash_footer: str = None,
                 hash_rc: str = None):
        self.id = _id

        self.image_hash = imagehash.hex_to_hash(record_hash).hash.flatten()


class HashTable:
    _rows: List[HashRow] = []

    _nn_image: NearestNeighbors = None
    _nn_image_header: NearestNeighbors = None
    _nn_image_footer: NearestNeighbors = None
    _nn_image_rc: NearestNeighbors = None

    @classmethod
    def load(cls):
        offset = 0
        limit = results = 100_000

        logging.debug('Loading hashed values from DB')

        with database.Database.db_contextmanager() as db:
            while results == limit:
                records: List[Row] = card.Card.new_read_all_hashes(db, offset=offset, limit=limit)
                results = len(records)

                cls._rows.extend([
                    HashRow(*list(row))
                    for row in records
                ])

                offset += results

        print()

        if cls._rows:
            cls._nn_image = NearestNeighbors(metric='hamming', n_neighbors=10, n_jobs=-1)
            cls._nn_image.fit([
                h.image_hash
                for h in cls._rows
            ])

    @classmethod
    def rows(cls) -> List[HashRow]:
        if not cls._rows:
            cls.load()

        return cls._rows

    @classmethod
    def nn_image(cls) -> NearestNeighbors:
        if not cls._nn_image:
            cls.load()

        return cls._nn_image

    @classmethod
    def get_closest_matches(cls, numpy_array: NDArray, matches: int = None) -> List[str]:
        results = cls.nn_image().kneighbors([numpy_array.flatten()], n_neighbors=matches)

        return [
            cls.rows()[index].id
            for index in results[1].tolist()[0]
        ]
