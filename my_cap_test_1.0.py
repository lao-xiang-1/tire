#只检测炸弹快，若前方有则发送0
import cv2
import threading
import pupil_apriltags as apriltag
import time
#from find_serial import SerialPortSelector
import serial
import struct
import torch
import my_STP23L as stp
import time

cap_x=640
cap_y=480

class match:
    def __init__(self):
        #tag码检测参数
        self.tag_detector=apriltag.Detector(families='tag36h11')
        #激光雷达
        self.port1 = '/dev/ttyUSB0'  # 串口名称
        self.baudrate1 = 230400  # 波特率
        self.port2 = '/dev/ttyUSB1'  # 串口名称
        self.baudrate2 = 230400  # 波特率
        self.stp1=stp.STP23L(self.port1,self.baudrate1)
        self.stp2=stp.STP23L(self.port2,self.baudrate2)
        self.distance1=0
        self.distance2=0
        #串口参数
        self.ser=serial.Serial(port='/dev/ttyUSB2',baudrate=115200,timeout=0.5)
        #获取帧
        self.cap=cv2.VideoCapture('2.mp4')
        ret,frame=self.cap.read()
        self.last_frame=frame
        self.frame=frame
        self.wheather_frame=0
        #是否tag
        self.if_get_tag=0

    def get_frame(self):
        print('self.cap.isOpened():',self.cap.isOpened())
        while self.cap.isOpened():
            ret,frame=self.cap.read()
            if ret:
                self.last_frame=self.frame#帧缓存（处理的是上一帧）
                self.frame=frame
                self.wheather_frame=1
                # cv2.imshow('Raw Video',frame)
                # cv2.waitKey(30)

    #开启线程
    def main(self):
        threading.Thread(target=self.get_frame).start()
        threading.Thread(target=self.apriltag_detect).start()
        threading.Thread(target=self.distance_detect).start()

    def distance_detect(self):
        self.stp1.reset()
        self.stp2.reset()
        while True:
            self.distance1=self.stp1.read_data()
            self.distance2=self.stp2.read_data()
            print(self.distance1,self.distance2)
            self.send_data()#发送数据

    def apriltag_detect(self):
        while self.wheather_frame==0:
            time.sleep(0.01)
        while True:
            frame=self.last_frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            try:
                tags = self.tag_detector.detect(gray)
                if len(tags)== 0:
                    print("no tag")
                    self.if_get_tag=0
                    continue
                print("-"*50)
                for tag in tags:
                    self.if_get_bomb=0
                    self.center_x_for_tag=tag.center[0]
                    tag_id=tag.tag_id
                    if cap_x-32 <= self.center_x_for_tag <= cap_x+32 and tag_id==2:
                        self.if_get_bomb=1
                        self.send_data()#发送数据
                        print("find the bomb")
                print("-"*50)
            except:
                print("worng")    
            time.sleep(0.1)#检测间隔

    #只发送x坐标
    def send_data(self):
        data=[]
        if_get_bomb=self.if_get_bomb.to_bytes(1)#转换为字节
        pack1=struct.pack(">H", int(self.distance1))
        pack2=struct.pack(">H", int(self.distance2))
        data=b'\xff'+pack1+pack2+if_get_bomb+b'\xfe'#最终格式
        print('发送的数据：',data)
        self.ser.write(data)
        pass

    def stop(self):
        cv2.destroyAllWindows()
        self.cap.release()
        print('stop')

if  __name__=='__main__' :
    match = match()
    try:
        match.main()
    except BaseException as e:
        if isinstance(e, KeyboardInterrupt):
            match.stop()
            print("手动终止，释放成功！")
        else:
            print(e)
    match.stop()
    print("运行完成，释放成功！")
