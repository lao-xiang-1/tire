import serial
import time

class STP23L:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)
        self.distance=0

    def reset(self):
        reset_cmd = bytearray([0xAA,0xAA,0xAA,0xAA,0,0x0D,0,0,0,0,0x0D])
        self.ser.write(reset_cmd)
        reset_data=self.ser.read(13)
        data=list(bytearray(reset_data))
        if data[11]:
            print("reset success")

    def decode_data(self,data):
        average_distance=0
        time=0
        if data[0]!=0xAA:
            self.distance=0
        for i in range(10,195,15):
            if i+15<len(data):
                distance=(data[i+1]<<8)+data[i]
                peak=data[i+4]+(data[i+5]<<8)+(data[i+6]<<16)+(data[i+7]<<24)
                if peak>350000:
                    average_distance+=distance
                    time+=1
        if time>0:
            self.distance=average_distance/time               
        else:
            self.distance=0
        pass

    def read_data(self):
        raw_data = self.ser.read(195)
        data=list(bytearray(raw_data))
        self.decode_data(data)
        return self.distance
    
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
            data = stp23l.read_data()
            print(f"Distance:{data:.2f}mm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        stp23l.stop()
        pass