import os
import shutil
import time

import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup

FILEPATH = "tmp/image_downloads"


def set_up():
    os.makedirs(FILEPATH, exist_ok=True)
    pass


def clean_up():
    if os.path.exists(FILEPATH):
        shutil.rmtree(FILEPATH)
        os.removedirs("tmp/")


def download_images(url):
    print("Downloading Cards...")
    start = time.perf_counter()
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features="html.parser")
    img_tags = soup.find_all("img")
    img_srcs = []
    
    for img in img_tags:
        try:
            if img["name"].startswith("card") and img["src"].endswith(".png"):
                img_srcs.append((img["name"], img["src"]))
        except KeyError:
            continue

    for name, src in img_srcs:
        img_url = "https://www.setgame.com/" + src
        img_data = requests.get(img_url).content
        
        filename = f"{name}.png"
        with open(os.path.join(FILEPATH, filename), "wb") as f:
            f.write(img_data)

    elapsed = time.perf_counter() - start
    print(f"Retrieved Cards in {elapsed:.2f} seconds.")


def dummy_download(url):
    for i in range(1, 82):
        img_url = f"https://www.setgame.com/sites/all/modules/setgame_set/assets/images/new/{i}.png"
        img_data = requests.get(img_url).content
        with open(os.path.join(FILEPATH, f"card{i}.png"), "wb") as f:
            f.write(img_data)


def analyze_images():
    print("Analyzing Images...")
    start = time.perf_counter()

    cards = {}

    for img_file in os.listdir(FILEPATH):
        if img_file.endswith(".png"):
            img_path = os.path.join(FILEPATH, img_file)
            img = cv2.imread(img_path)

            colour = classify_colour(img)
            count = classify_count(img)
            fill = classify_fill(img)
            shape = classify_shape(img)

            cards[img_file] = {
                "colour": colour,
                "count": count,
                "fill": fill,
                "shape": shape
            }
            # print(img_file, colour, count, fill, shape)
            # cv2.imshow("Analyzed Image", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

    elapsed = time.perf_counter() - start
    print(f"Analyzed Cards in {elapsed:.2f} seconds.")
    return cards


def classify_colour(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (10, 10, 10), (255, 255, 255))
    mean = cv2.mean(hsv, mask=mask)

    h = mean[0]
    if h < 15 or h > 160:
        return "RED"
    elif 30 < h < 90:
        return "GREEN"
    elif 120 < h < 160:
        return "PURPLE"
    else:
        return "unknown"


def classify_count(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    shapes = [cnt for cnt in contours if cv2.contourArea(cnt) > 500]
    return len(shapes)


def classify_fill(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fills = []
    debug_img = img.copy()

    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < 500:
            continue

        cv2.drawContours(debug_img, [cnt], -1, (0, 255, 0), 2)

        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [cnt], -1, 255, -1)

        shape_pixels = cv2.countNonZero(mask)
        content_pixels = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))

        fill_ratio = content_pixels / shape_pixels if shape_pixels else 0
        fills.append(fill_ratio)

    if not fills:
        print("No valid shapes found.")
        return "unknown"

    avg_fill = sum(fills) / len(fills)

    result = ""
    if avg_fill > 0.95:
        result = "SOLID"
    elif avg_fill > 0.5:
        result = "STRIPED"
    else:
        result = "OPEN"

    return result


def classify_shape(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 500]
    if not contours:
        return "unknown"

    cnt = max(contours, key=cv2.contourArea)

    area = cv2.contourArea(cnt)
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area > 0 else 0

    approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
    vertices = len(approx)

    if vertices <= 6 and solidity > 0.9:
        return "DIAMOND"
    elif solidity > 0.95:
        return "OVAL"
    else:
        return "SQUIGGLE"
