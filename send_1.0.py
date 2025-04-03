import my_STP23L_1 as stp
import serial
import struct
import time

def send_data(data1,data2):
    pack1=struct.pack(">H", int(data1))
    pack2=struct.pack(">H", int(data2))
    #print(pack1,pack2)
    data=b'\xFF'+pack1+pack2+b'\x00'+b'\xFE'#+b'\x00'
    print('发送00：',data)
    ser.write(data)

def receive():
    # 等待至少1字节可用，超时500ms
    back_data = b''
    if ser.in_waiting > 0:
        back_data = ser.read(ser.in_waiting)
    print('接收0000：',back_data)

if __name__=='__main__':
    port1 = '/dev/ttyUSB0'  # 串口名称
    baudrate1 = 230400  # 波特率
    port2 = '/dev/ttyUSB1'  # 串口名称
    baudrate2 = 230400  # 波特率
    ser=serial.Serial(port='/dev/ttyUSB2',baudrate=115200,timeout=5)
    stp1=stp.STP23L(port1,baudrate1)
    stp1.reset()
    stp2=stp.STP23L(port2,baudrate2)
    stp2.reset()
    try:
        while True:

            if stp1.get_distance()==0 or stp2.get_distance()==0 :
                continue

            for i in range(0,12):
                data1=stp1.distance[i]
                data2=stp2.distance[i]

                print('原始：',data1,data2)
                # print(f"Distance:{data1:.2f}mm")
                send_data(data1,data2)
                #time.sleep(0.05)
                receive()
                time.sleep(0.1)#发送之间的时间间隔

    except KeyboardInterrupt:
        stp1.stop()
        stp2.stop()
        pass
    