# encoding:utf-8
# date:2021-01-16
# author: eric
# function: dp client

import os
import requests
import base64
import cv2
import json
import numpy as np
import time
import traceback
import random
from multiprocessing import Process
from multiprocessing import Manager
from draw_utils.draw_utils import draw_bbox,draw_face,draw_pose,draw_person,draw_hand


def dp_client(src,pattern,host,port):
    request_url = host + port + "/task?model_pattern={}".format(pattern)
    r = requests.post(request_url,data=src)
    msg = r.json()
    # g_info_dict["{}_info".format(pattern)] = msg["result"]
    return msg["result"]

def dp_client_process(version,pattern,host,port,g_info_dict):
    while True:
        if g_info_dict["{}_src".format(pattern)] is not None:
            src = g_info_dict["{}_src".format(pattern)]
            request_url = host + port + "/task?version={}&model_pattern={}".format(version,pattern)
            r = requests.post(request_url,data=src)
            msg = r.json()
            g_info_dict["{}_result".format(pattern)] = msg["result"]
            g_info_dict["{}_src".format(pattern)] = None
            # print("dp_client_process - pattern {} ".format(pattern))
            time.sleep(0.006)
def business_task():
    pass
if __name__ == "__main__":

    models_dict = {
        "person":draw_person,
        "pose":draw_pose,
        "face":draw_face,
        "hand":draw_hand,
        }
    #--------------------------------------------------- 步骤 1 创建任务，发起服务请求
    host = "http://127.0.0.1:"
    port = "6666"
    version = "v0.1"
    #--------------------------------
    g_info_dict = Manager().dict()
    process_list = []
    for pattern in models_dict.keys():# 加载切片视频到不同的进程内
        t = Process(target=dp_client_process,args=(version,pattern,host,port,g_info_dict))
        g_info_dict["{}_src".format(pattern)] = None
        process_list.append(t)

    for i in range(len(process_list)):
        process_list[i].start()
    #--------------------------------
    print("init camera ~")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if ret:
            # h_,w_ = frame.shape[0:2]
            # frame = cv2.resize(frame, (int(w_/2),int(h_/2)))
            st_ = time.time()
            img_str = cv2.imencode('.jpg', frame)[1].tobytes()  # 将图片编码成流数据，放到内存缓存中，然后转化成string格式
            img_str = base64.b64encode(img_str) #将图片数据转成base64格式

            data_ = {"src" : img_str}
            if False:
                for pattern_ in models_dict.keys():
                    msg = dp_client(data_,pattern_,host,port)
                    if msg is not None:
                        models_dict[pattern_](frame,msg)
            else:
                for pattern in models_dict.keys():# 加载切片视频到不同的进程内
                    g_info_dict["{}_src".format(pattern)] = data_

                while True:
                    task_cnt = 0
                    for pattern in models_dict.keys():# 加载切片视频到不同的进程内
                        if g_info_dict["{}_src".format(pattern)] is None:
                            task_cnt += 1
                    if task_cnt == len(process_list):
                        break
                # 模型信息汇总
                msgs_dict = {}
                for pattern in models_dict.keys():# 加载切片视频到不同的进程内
                    msg_ = g_info_dict["{}_result".format(pattern)]
                    msgs_dict[pattern] = msg_
                    if msg_ is not None:
                        models_dict[pattern](frame,msg_)

                business_task(msgs_dict)# 业务处理模块

            et_ = time.time()

            cv2.putText(frame, 'fps: {:.2f}'.format(1./(et_-st_)), (5,40),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0),4)
            cv2.putText(frame, 'fps: {:.2f}'.format(1./(et_-st_)), (5,40),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))

            cv2.namedWindow("frame",0)
            cv2.imshow("frame",frame)
            if cv2.waitKey(1) == 27:
                break

    cap.release()
