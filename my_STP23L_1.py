import serial
import time

class STP23L:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)
        self.distance=[]

    def reset(self):
        reset_cmd = bytearray([0xAA,0xAA,0xAA,0xAA,0,0x0D,0,0,0,0,0x0D])
        self.ser.write(reset_cmd)
        reset_data=self.ser.read(13)
        data=list(bytearray(reset_data))
        if data[11]:
            print("reset success")

    def get_distance(self):
        while True:
            if self.ser.in_waiting > 0:
                raw_data = b''
                while len(raw_data) < 195:
                    # 读取串口中所有可用的数据
                    raw_data += self.ser.read(self.ser.in_waiting)
                    time.sleep(0.01)  # 可以加一些延时，避免CPU占用过高
                
                # 确保读取到完整的195字节
                if len(raw_data) >= 195:
                    data = list(bytearray(raw_data[:195]))  # 取前195字节，防止溢出

                    count=0
                    if data[0]!=0xAA:
                        return 0
                    for i in range(10,195,15):
                        self.distance[count]=(data[i+1]<<8)+data[i]
                        count+=1
                    return 1
    
    def stop(self):
        stop_cmd = bytearray([0xAA,0xAA,0xAA,0xAA,0,0x0F,0,0,0,0,0xF])
        self.ser.write(stop_cmd)
        self.ser.close() 

if __name__ == "__main__":
    port = '/dev/ttyUSB0'  # 串口名称
    baudrate = 230400  # 波特率
    stp23l = STP23L(port, baudrate)
    stp23l.reset()
    try:
        while True:
            if stp23l.get_distance()==0:
                continue
            for i in range(0,12):
                data=stp23l.distance[i]
                print(f"Distance:{data}mm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        stp23l.stop()
        pass