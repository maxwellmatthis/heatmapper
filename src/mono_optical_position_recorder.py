#!/usr/bin/python3

from dataclasses import dataclass
from typing import *
import sys
import os
import math
from pathlib import Path
from processing import dataset
import numpy as np
import cv2 as cv

OPENCV_WINDOW_DIMENSIONS = (math.floor(16/9 * 400), 400)
MEASUREMENTS_CSV = "measurements.csv"
MEASUREMENTS_IMAGES = "measurements"

REFERENCE_OBJECT_CALIBRATION_DISTANCE = 1
REFERENCE_OBJECT_CALIBRATION_DIAMETER_PIXELS = 230
REFERENCE_OBJECT_DIAMETER_METERS = 0.25
FOCAL_LENGTH = (REFERENCE_OBJECT_CALIBRATION_DIAMETER_PIXELS *
                REFERENCE_OBJECT_CALIBRATION_DISTANCE)/REFERENCE_OBJECT_DIAMETER_METERS


def distance_to_reference_object_meters(size_in_px: int):
    """
    # Some tests with real world data:

    ```
    Distance(200) = 230px*m / 200px = 1,15m; Real: 1,20m
    Distance(86) = 230px*m / 86px = 2,67m; Real: 2,70m
    Distance(66) = 230px*m / 66px = 3,48m;
    Distance(98) = 230/98 = 2,34m; Real: 2,29m
    ```
    """
    return (FOCAL_LENGTH * REFERENCE_OBJECT_DIAMETER_METERS) / size_in_px


CAMERA_HORIZONTAL_FIELD_OF_VIEW_RAD = 2
CAMERA_HORIZONTAL_PIXELS = 1280


def horizontal_angle_to_reference_object_rad(x_pixel: int):
    return ((x_pixel - CAMERA_HORIZONTAL_PIXELS / 2) / CAMERA_HORIZONTAL_PIXELS * 2) * CAMERA_HORIZONTAL_FIELD_OF_VIEW_RAD / 2


CAMERA_VERTICAL_FIELD_OF_VIEW_RAD = 2
CAMERA_VERTICAL_PIXELS = 720


def vertical_angle_to_reference_object_rad(y_pixel: int):
    return ((y_pixel - CAMERA_VERTICAL_PIXELS / 2) / CAMERA_VERTICAL_PIXELS * 2) * CAMERA_VERTICAL_FIELD_OF_VIEW_RAD / 2


cam = None


def capture_image() -> cv.typing.MatLike:
    global cam
    if cam is None:
        cam = cv.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
    return frame


def find_circles(img) -> np.uint16 | None:
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (5, 5), 0)
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1,
                              20, param1=35, param2=2*35, minRadius=30, maxRadius=600)
    if circles is None:
        return None
    return np.uint16(np.around(circles))


@dataclass
class ReferenceObjectPosition:
    img_x: int
    img_y: int
    img_r: int
    distance: float
    x: float
    y: float
    z: float


def find_reference_object(img) -> ReferenceObjectPosition | None:
    circles = find_circles(img)
    if circles is None:
        return None
    best_x = 0
    best_y = 0
    best_r = 0
    for x, y, r in circles[0, :]:
        if r > best_r:
            best_x = x
            best_y = y
            best_r = r
        # debug
        cv.circle(img, (x, y), r, (255, 0, 0), 1)
    distance = math.floor(
        distance_to_reference_object_meters(2*best_r) * 100) / 100
    alpha_x = horizontal_angle_to_reference_object_rad(best_x)
    rop = ReferenceObjectPosition(
        best_x,
        best_y,
        best_r,
        distance,
        math.floor(math.sin(alpha_x) * distance * 100) / 100,
        math.floor(math.sin(vertical_angle_to_reference_object_rad(
            best_y)) * distance * 100) / 100,
        math.floor(math.cos(alpha_x) * distance * 100) / 100
    )
    return rop


WINDOW_PREVIEW_OBJECT = "preview object"
cv.namedWindow(WINDOW_PREVIEW_OBJECT, cv.WINDOW_NORMAL)


def preview_object(img: cv.typing.MatLike, obj: ReferenceObjectPosition):
    text_pos_x = 0 if obj.img_r > obj.img_x else obj.img_x - obj.img_r
    text_pos_y = 0 if obj.img_r + 20 > obj.img_y else obj.img_y - obj.img_r - 20
    img = cv.putText(
        img, f"({obj.x}m, {obj.y}m, {obj.z}m) ({obj.distance}m)", (text_pos_x, text_pos_y),
        cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv.LINE_AA)

    # Markup outer circle and center
    cv.circle(img, (obj.img_x, obj.img_y), obj.img_r, (0, 255, 0), 2)
    cv.circle(img, (obj.img_x, obj.img_y), 2, (0, 0, 255), 2)
    cv.imshow(WINDOW_PREVIEW_OBJECT, img)
    cv.resizeWindow(WINDOW_PREVIEW_OBJECT, *OPENCV_WINDOW_DIMENSIONS)


def save_measurement(img: cv.typing.MatLike, obj: ReferenceObjectPosition):
    uuid = dataset.append_csv(MEASUREMENTS_CSV, obj.x, obj.y, obj.z, 0)
    img_name = f"x{obj.x}y{obj.y}z{obj.z}-{uuid}.png"
    Path(MEASUREMENTS_IMAGES).mkdir(parents=True, exist_ok=True)
    path = os.path.join(MEASUREMENTS_IMAGES, img_name)
    if not cv.imwrite(path, img):
        print(
            f"There was an issue saving the image for measurement {uuid}. Make sure the {MEASUREMENTS_IMAGES} directory exists.")
    print(f"Successfully saved measurement position {uuid}.")


def preview_verify_and_save_measurement(img: cv.typing.MatLike, obj: ReferenceObjectPosition):
    preview_object(img, obj)

    while True:
        k = cv.waitKey(100)
        if k == 115:  # "s" for save
            save_measurement(img, obj)
            break
        elif k == 100:  # "d" for discard
            break


WINDOW_LIVE_FEED = "live feed"
if __name__ == "__main__":
    print('Press "s" to save and "d" to discard images in preview and verify mode.')
    if len(sys.argv) <= 1:
        cv.namedWindow(WINDOW_LIVE_FEED, cv.WINDOW_NORMAL)
        while True:
            img = capture_image()
            cv.imshow(WINDOW_LIVE_FEED, img)
            cv.resizeWindow(WINDOW_LIVE_FEED, *OPENCV_WINDOW_DIMENSIONS)
            cv.waitKey(10)
            obj = find_reference_object(img)
            if obj is not None:
                preview_verify_and_save_measurement(img, obj)
    else:
        img = cv.imread(sys.argv[1])
        obj = find_reference_object(img)
        if obj is None:
            print("Unable to detect object.")
        else:
            if len(sys.argv) > 1 and sys.argv[2] == "--no-verify":
                print("here!")
                save_measurement(img, obj)
            else:
                preview_verify_and_save_measurement(img, obj)
