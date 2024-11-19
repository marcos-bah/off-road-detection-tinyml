from imu import MPU6050
from time import sleep, localtime
from machine import Pin, I2C

LED = machine.Pin("LED", machine.Pin.OUT)
LED.off()

def setup():
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    imu = MPU6050(i2c)
    return imu

def read_data(imu):
    ax = round(imu.accel.x, 2)
    ay = round(imu.accel.y, 2)
    az = round(imu.accel.z, 2)
    gx = round(imu.gyro.x)
    gy = round(imu.gyro.y)
    gz = round(imu.gyro.z)
    tem = round(imu.temperature, 2)
    return ax, ay, az, gx, gy, gz, tem

imu = setup()

btn_normal_slow = Pin(2, Pin.IN, Pin.PULL_DOWN)
btn_normal_fast = Pin(3, Pin.IN, Pin.PULL_DOWN)
btn_fall = Pin(4, Pin.IN, Pin.PULL_DOWN)
btn_idle = Pin(5, Pin.IN, Pin.PULL_DOWN)

def read_data_btn():
    normal_slow = btn_normal_slow.value()
    normal_fast = btn_normal_fast.value()
    fall = btn_fall.value()
    idle = btn_idle.value()
    
    return normal_slow, normal_fast, fall, idle

def get_label():
    slow, fast, fall, idle = read_data_btn()
    label = None
    
    if(slow):
        label = "slow"
    elif(fast):
        label = "fast"
    elif(fall):
        label = "fall"
    elif(idle):
        label = "idle"
        
    return label

def getDatetime():
    current_time = localtime()
    return "{:04d}{:02d}{:02d}_{:02d}-{:02d}-{:02d}".format(
        current_time[0], current_time[1], current_time[2] % 100, 
        current_time[3], current_time[4], current_time[5]
    )

def create_filename():
    datetime = getDatetime()
    return f"data_{datetime}.csv"

def save_csv(ax, ay, az, gx, gy, gz, label, isLast):
    global filename
    try:
        with open(filename, "r") as f:
            pass 
    except OSError:
        with open(filename, "w") as f:
            f.write("ax,ay,az,gx,gy,gz,label\n")
    
    with open(filename, "a") as f:
        f.write(f"{ax},{ay},{az},{gx},{gy},{gz},{label}\n")
        if isLast:
            f.write("\n")

def save_data(label, n):
    for i in range(n):
        isLast = False
        if i == n-1:
            isLast = True
        ax, ay, az, gx, gy, gz, tem = read_data(imu)
        datetime = getDatetime()
        save_csv(ax, ay, az, gx, gy, gz, label, isLast)
        print(f"ax: {ax}\tay: {ay}\taz: {az}\tgx: {gx}\tgy: {gy}\tgz: {gz}\tTemp: {tem}\tDatetime: {datetime}\tLabel: {label}\t", end="\r\n")
        sleep(0.02)

filename = create_filename()

while True:
    print("System Ready...", end="\r")
    label = get_label()
    if(label != None):
        LED.on()
        print("Starting recording");
        save_data(label, 50)
        print("Stop record");
        LED.off()
        
    sleep(0.1)



