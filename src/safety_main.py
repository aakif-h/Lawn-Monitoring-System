from time import sleep, time
from cimis import process_CIMIS_data
from DHT11 import process_DHT_data
from SenseLED import process_PIR_data, setup_PIR
from lcd import setup_LCD, LCD_display
import threading

global mcp,lcd, ce, ct, ch


def setup():
    global mcp, lcd
    setup_PIR()
    mcp, lcd = setup_LCD()
    

def cimis_thread():
    global ce, ct, ch
    ce, ct, ch = process_CIMIS_data()
    #print(ce, ct, ch)


def run():
    global mcp, lcd
    
    init_time = time()
    temp, humidity = 0, 0
    avgTemp, avgHumidity = 0, 0
    motion_time_remaining, motion_time_duration = 0, 5
    water_flag, motion_flag = False, False
    
    t = None
    global ce, ct, ch
    ce, ct, ch = -1, -1, -1
    message = None
    while True:
        if water_flag == True:
            if motion_flag == True:
                lcd.clear()
                lcd.setCursor(0,0)
                lcd.message("Motion detected")
                lcd.setCursor(0,1)
                lcd.message("Time Left: {}".format(motion_time_remaining))
                if motion_time_remaining == 0:
                    motion_flag = False
                    continue
                motion_time_remaining -= 1
                sleep(1)
                    
            else:
                # poll motion sensor  
                motion_flag = process_PIR_data()
                if (motion_flag) == True:
                    motion_time_remaining = motion_time_duration
                    continue
                lcd.clear()
                lcd.setCursor(0,0)
                lcd.message("Water Irr On")
                lcd.setCursor(0,1)
                lcd.message(message)
                message = message[1:] + message[0]
                sleep(1)
            
        else:
            time_diff = int(time() - init_time)
            # poll the DHT sensor every minute
            # and display on the LCD
            if (time_diff) % 60 == 0:
                temp, humidity = process_DHT_data()
                avgTemp = avgTemp + temp
                avgHumidity = avgHumidity + humidity
                    

            if (time_diff) % 3600 == 0:
                print("inCIMIS")
                while True:
                    t = threading.Thread(target = cimis_thread)
                    t.start()
                    t.join()
                    if ce > -1 and ct > -1 and ch > -1:
                        break
                message = "c_eto: {} c_tmp: {} c_hum: {}".format(ce, ct, ch)
                water_flag = True


            lcd.setCursor(0, 0)
            lcd.message("tmp:{} hum:{}".format(temp, humidity))
            lcd.setCursor(0,1)
            print(ce, ct, ch)
            lcd.message(message)
            message = message[1:] + message[0]
       
            if (time_diff) % 86400 == 86399:
                init_time = time()

            
            print("time diff",time_diff)
            sleep(0.0625)  
        



def destroy():
    pass

if __name__ == '__main__':
    setup()
    try:
        run()
    except KeyboardInterrupt:
        destroy()
