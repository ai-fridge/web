import os
import json
import cv2
from utils.utils import get_yolo_boxes, makedirs
from utils.bbox import draw_boxes
from keras.models import load_model
import numpy as np
from django.conf import settings


# infer_model = None
#
#
#
# def init_model(config_path):
#     with open(config_path) as config_buffer:
#         config = json.load(config_buffer)
#     infer_model = load_model(settings.BASE_DIR+config['train']['saved_weights_name'])

def _main_(config_path,input_path, output_path):
    with open(config_path) as config_buffer:
        config = json.load(config_buffer)
    makedirs(output_path)

    ###############################
    #   Set some parameter
    ###############################
    net_h, net_w = 416, 416  # a multiple of 32, the smaller the faster
    obj_thresh, nms_thresh = 0.5, 0.45

    ###############################
    #   Load the model
    ###############################
    os.environ['CUDA_VISIBLE_DEVICES'] = config['train']['gpus']
    infer_model = load_model(settings.BASE_DIR+config['train']['saved_weights_name'])

    ###############################
    #   Predict bounding boxes
    ###############################

    # do detection on an image or a set of images
    image_paths = []

    if os.path.isdir(input_path):
        for inp_file in os.listdir(input_path):
            image_paths += [input_path + inp_file]
    else:
        image_paths += [input_path]
    image_paths = [inp_file for inp_file in image_paths if (inp_file[-4:] in ['.jpg', '.png', 'JPEG'])]
    # the main loop
    for image_path in image_paths:
        image = cv2.imread(image_path)
        # predict the bounding boxes
        boxes = get_yolo_boxes(infer_model, [image], net_h, net_w, config['model']['anchors'], obj_thresh, nms_thresh)[
            0]

        # draw bounding boxes on the image using labels
        image_new, label_result = draw_boxes(image, boxes, config['model']['labels'], obj_thresh)
        # write the image with bounding boxes to file
        cv2.imwrite(output_path + image_path.split('/')[-1], np.uint8(image_new))
        return label_result,output_path + image_path.split('/')[-1]

