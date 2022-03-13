"""
# @Time     : 2022/3/13 11:06 下午
# @Author   : ssw
# @File     : upload_big_video.py
# @Desc      : 使用fastapi 上传大视频
"""
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import os
import datetime

app = FastAPI(title="视频处理接口")


@app.post("/uploadVideo", summary="上传视频", tags=["视频处理"])
async def getVideo(file: UploadFile = File(...)):
    print(f"接收视频")
    time_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # 当前时间字符串
    temp_file_name = f"tempVideoFile_{time_now}.mp4"  # 临时文件的文件名
    batch_size = 10 * 2 ** 20  # 每次写入文件的数据大小，这里代表 10 MiB
    with open(temp_file_name, 'wb') as f:  # 分批写入数据
        for i in iter(lambda: file.file.read(batch_size), b''):  # 从网络文件流分批读取数据到 b'',再写入文件
            f.write(i)

    file_size = os.path.getsize(temp_file_name)  # 统计文件大小
    cap = cv2.VideoCapture(temp_file_name)  # 读取视频数据
    fps = cap.get(cv2.CAP_PROP_FPS)  # 统计视频的帧率
    total_s = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 统计视频的帧数
    total_time = total_s / fps  # 计算视频的时长

    # 逐帧处理图像
    # if cap.isOpened():          # 展示视频（没有音频）
    #     while True:
    #         ok,frame = cap.read()       # 逐帧读取图像
    #         if ok:
    #             cv2.imshow('1',frame)       # 显示单帧图像
    #             cv2.waitKey(int(1000 * total_s / fps) - 1)    # 根据帧率，延时显示下一张
    #         else:
    #             cv2.destroyAllWindows()
    #             break       # 关闭图像窗口，退出循环
    result = {'文件名': file.filename,
              '文件大小': file_size,
              '帧数': total_s,
              '时长': total_time, }  # 返回视频的基本信息

    if os.path.exists(temp_file_name):  # 删除临时视频文件
        os.remove(temp_file_name)

    return JSONResponse(content=result)


if __name__ == "__main__":
    name_app = os.path.basename(__file__)[0:-3]  # 获取当前文件名
    uvicorn.run(f'{name_app}:app', host="0.0.0.0", port=8004, reload=True)  # 开启服务