# encoding:utf-8
# date:2021-01-16
# author: eric
# function: dp engine

import os
import cv2
import time
from logger import logger
from vw_utils import plot_one_box
from models_config import *
from flask import request, Flask, Response, send_file,url_for
from flask_cors import CORS
import base64
import requests
import cv2
import numpy as np
import json
import time

app = Flask(__name__)
CORS(app,resources=r'/*')
#接受任务请求
@app.route("/task", methods=['POST','GET'])
def get_task():
    global models_engine
    version = request.args.get("version")
    model_pattern = request.args.get("model_pattern")
    logger.info("----->>> url : {}".format(request.url))
    logger.info("----->>> version : {} ,model_pattern : {}".format(version,model_pattern))

    #解析图片数据
    img_src = base64.b64decode(str(request.form['src']))
    img_src = np.fromstring(img_src, np.uint8)
    img_src = cv2.imdecode(img_src, cv2.IMREAD_COLOR)
    try:
        output_ = models_engine[model_pattern].predict(img_src,vis = False)
    except:
        output_ = None

    resp = {
        "model_pattern":model_pattern,
        "result":output_,
        }
    return Response(json.dumps(resp),  mimetype='application/json')

if __name__ == "__main__":
    #------------------------------------------------------ models engine init
    global models_engine
    # model components
    models_list = {
        "face": {"model" : yolo_v3_face_class},
        "pose": {"model" : pose_class},
        "yolact": {"model" : yolact_class},
        "person": {"model" : yolo_v3_person_class},
        "hand": {"model" : yolo_v3_hand_class},
        }

    models_engine = {}
    for k_ in models_list:
        logger.info(" {} class init ~ ".format(k_))
        models_engine[k_] = models_list[k_]["model"]()

    #------------------------------------------------------ start algo engine server
    #多进程或多线程只能选择一个，不能同时开启
    # threaded=True
    # processes=True
    # 如果需要在通过flask 在不同计算机进行通信， host 需要设置为 0.0.0.0
    logger.info("/*************** video algorithm service start****************/")
    app.run(
        host = "127.0.0.1",
        # host = "0.0.0.0",
        port= 6666,
        debug = False,
        processes = True,
        )
