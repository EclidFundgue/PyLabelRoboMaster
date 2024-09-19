import cv2
import numpy as np


def txt2target(txt, img_h, img_w):
    target = []

    boxes = txt.split('\n')
    boxes = list(filter(None, boxes))

    for box in boxes:
        target_item = []
        box = box.split(' ')

        box = list(filter(lambda x: x != "", box))

        if len(box) != 13:
            continue

        # class
        label = int(box[0])
        target_item.append(label)

        # detection box
        pose_information = list(map(float, box[1:]))
        pose_information = np.array(pose_information)
        pose_information[::2] = pose_information[::2] * img_w
        pose_information[1::2] = pose_information[1::2] * img_h
        target_item.extend(pose_information)

        target.append(target_item)

    return target


def target2txt(target, img_h, img_w):
    txt = ''
    for target_item in target:
        target_item[0]

        target_item[1::2] = (np.array(target_item[1::2]) / img_w).tolist()
        target_item[2::2] = (np.array(target_item[2::2]) / img_h).tolist()

        target_item = list(map(str, target_item))
        txt += ' '.join(target_item) + '\n'

    return txt

def result2target(result, offset_x =0,offset_y=0,remain_conf =False):
    target = []
    for box, kp in zip(result.boxes, result.keypoints):
        target_item = []
        cls_id = int(box.cls[0])
        target_item.append(cls_id)

        x1, y1, x2, y2 = box.xyxy[0]
        x1, y1, x2, y2 = int(x1)+offset_x, int(y1)+offset_y, int(x2)+offset_x, int(y2)+offset_y
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        w = x2 - x1
        h = y2 - y1
        target_item.extend([x,y,w,h])

        keypoints = kp.xy[0]
        for i in range(0, len(keypoints)):
            x, y = int(keypoints[i][0])+offset_x, int(keypoints[i][1])+offset_y
            target_item.extend([x, y])

        if(remain_conf):
            target_item.append(float(box.conf))
        target.append(target_item)
    return target

def split_image(image, tile_size=(640, 640), overlap=32):
    ''' Separate an image into tiles. '''
    h, w = image.shape[:2]
    tiles = []
    # handle horizontal splits
    for y in range(0, h-tile_size[1]+1, tile_size[1]-overlap):
        for x in range(0, w-tile_size[0]+1, tile_size[0]-overlap):
            tile = image[y:y+tile_size[1], x:x+tile_size[0]]
            tiles.append((tile, (x, y)))
    # handle last row
    if h > tile_size[1]:
        for x in range(0, w-tile_size[0]+1, tile_size[0]-overlap):
            tile = image[h-tile_size[1]:h, x:x+tile_size[0]]
            tiles.append((tile, (x, h-tile_size[1])))
        # last column, may be smaller than tile_size
        if w > tile_size[0]:
            tile = image[h-tile_size[1]:h, w-tile_size[0]:w]
            tiles.append((tile, (w-tile_size[0], h-tile_size[1])))
    # if w > tile_size, handle last column
    elif w > tile_size[0]:
        tile = image[0:h, w-tile_size[0]:w]
        tiles.append((tile, (w-tile_size[0], 0)))

    return tiles

def nms_target(targets):
    boxes = []
    scores = []
    class_ids = []
    for target in targets:
        boxes.append(target[1:5])
        scores.append(target[9])
        class_ids.append(target[0])
    boxes = np.array(boxes)
    scores = np.array(scores).astype(np.float32)
    keep = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.5,nms_threshold=0.2)
    return [targets[i] for i in keep]

def merge_predictions(tiles, predictions):
    target =[]

    for (tile, (x, y)), pred in zip(tiles, predictions):
        refactor_target = result2target(pred, x, y,True)
        target.extend(refactor_target)
    target = nms_target(target)

    return target

def predict_with_split_windows(model, image, window_size):
    # Some images are too small to split, so we just predict on the whole image
    if(image.shape[0] < window_size or image.shape[1] < window_size):
        predictions=model.predict(image)
        prediction = predictions[0]
        target = result2target(prediction)
        return target
    tiles = split_image(image, tile_size=(window_size, window_size), overlap=64)
    predictions = [model.predict(tile[0])[0] for tile in tiles]
    target = merge_predictions(tiles, predictions)
    return target