#!/usr/bin/python3
"""
This script gets the relative position to the camera of an orange circle with a diameter of 25cm.
"""

from dataclasses import dataclass
from typing import *
import sys
import os
import math
import uuid
import numpy as np
import cv2 as cv


REFERENCE_OBJECT_CALIBRATION_DISTANCE = 1
REFERENCE_OBJECT_CALIBRATION_DIAMETER_PIXELS = 230
REFERENCE_OBJECT_DIAMETER_METERS = 0.25

FOCAL_LENGTH = (REFERENCE_OBJECT_CALIBRATION_DIAMETER_PIXELS *
                REFERENCE_OBJECT_CALIBRATION_DISTANCE)/REFERENCE_OBJECT_DIAMETER_METERS

OPENCV_WINDOW_DIMENSIONS = (math.floor(16/9 * 400), 400)


def distance_to_reference_object_meters(size_in_px: int):
    return (FOCAL_LENGTH * REFERENCE_OBJECT_DIAMETER_METERS) / size_in_px


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
                              20, param1=40, param2=2*40, minRadius=0, maxRadius=0)
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
    # TODO: fill in correct x, y, and z coordinates
    return ReferenceObjectPosition(
        best_x,
        best_y,
        best_r,
        math.floor(distance_to_reference_object_meters(2*best_r) * 100) / 100,
        0,
        0,
        0
    )


WINDOW_PREVIEW_OBJECT = "preview object"
cv.namedWindow(WINDOW_PREVIEW_OBJECT, cv.WINDOW_NORMAL)


def preview_object(img: cv.typing.MatLike, obj: ReferenceObjectPosition):
    print(
        f"Distance to object is located at ({obj.x}m, {obj.y}m, {obj.z}m), {obj.distance}m far away.")
    img = cv.putText(
        img, f"({obj.x}m, {obj.y}m, {obj.z}m) ({obj.distance}m)", (obj.img_x -
                                                                   obj.img_r, obj.img_y - obj.img_r - 20),
        cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv.LINE_AA)

    # Markup outer circle and center
    cv.circle(img, (obj.img_x, obj.img_y), obj.img_r, (0, 255, 0), 2)
    # cv.circle(img, (obj.img_x, obj.img_y), obj.img_r, (0, 0, 255), 3)
    cv.imshow(WINDOW_PREVIEW_OBJECT, img)
    cv.resizeWindow(WINDOW_PREVIEW_OBJECT, *OPENCV_WINDOW_DIMENSIONS)


def save_measurement(img: cv.typing.MatLike, obj: ReferenceObjectPosition):
    id = uuid.uuid4()
    with open("measurements.csv", "a") as f:
        f.write(f"{obj.x},{obj.y},{obj.z},{obj.distance},0,{id}\n")
    img_name = f"x{obj.x}y{obj.y}z{obj.z}-{id}.png"
    path = os.path.join("measurements", img_name)
    cv.imwrite(path, img)


def preview_verify_and_save_measurement(img: cv.typing.MatLike, obj: ReferenceObjectPosition):
    preview_object(img, obj)

    print('Press "s" to save and "d" to discard.')
    while True:
        k = cv.waitKey(100)
        if k == 115:  # "s" for save
            save_measurement(img, obj)
            break
        elif k == 100:  # "d" for discard
            break


WINDOW_LIVE_FEED = "live feed"
cv.namedWindow(WINDOW_LIVE_FEED, cv.WINDOW_NORMAL)
if __name__ == "__main__":
    if len(sys.argv) <= 1:
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
                save_measurement(img, obj)
            else:
                preview_verify_and_save_measurement(img, obj)


# Math:
# Focal_Length = (Pixels x Distance) / Width = (230px * 1m) / 0.25m = 920px  | /Pixels; *Width
# Distance(p) = (Focal_Length * Width) / Pixels = (920px * 0.25m) / p = 230px*m / p
# Distance(200) = 230px*m / 200px = 1,15m; Real: 1,20m
# Distance(86) = 230px*m / 86px = 2,67m; Real: 2,70m
# Distance(66) = 230px*m / 66px = 3,48m
# Distance(98) = 230/98 = 2,34m; Real: 2,29m

# Distance from center of frame
# a^2 + b^2 = c^2
# AK^2 + GK^2 = HP^2  | -AK^2
# GK^2 = HP^2 - AK^2  | 
