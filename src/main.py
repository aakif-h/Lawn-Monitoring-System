import RPi.GPIO as GPIO
from time import sleep, time
from cimis import process_CIMIS_data
from DHT11 import process_DHT_data
from SenseLED import process_PIR_data, setup_PIR
from lcd import setup_LCD, LCD_display
import threading

global mcp,lcd, ce, ct, ch, relayPin


def setup():
    global mcp, lcd, relayPin
    GPIO.setwarnings(False)
    # setup for the Motion Sensor
    setup_PIR()

    # setup for the LCD
    mcp, lcd = setup_LCD()

    # setup for the Relay Module
    relayPin = 40
    GPIO.setup(relayPin, GPIO.OUT)
    
    

def cimis_thread():
    global ce, ct, ch
    ce, ct, ch = process_CIMIS_data()

def calc_water(eto):
    pf = 1.0 # plant factor (lawn)
    sf = 1500 # square footage (30 x 50 area)
    ie = 0.75 # irrigation efficiency (compensates for water not absorbed by plant)
    # equation given in the final project pdf (Appendix B)
    hourly_gal = (eto*pf*sf*0.62)/ie # 0.62 is a constant factor for conversion
    return hourly_gal # return hourly water consumption



def run():
    global mcp, lcd, relayPin
    
    init_time = time()
    temp, humidity = 0, 0
    avgTemp, avgHumidity = 0, 0
    totalTemp, totalHumidity = 0,0
    
    motion_time_remaining, motion_time_duration = 0, 5
    water_time_remaining, water_time_duration = 0, 0
    polling_dht_time = 60
    polling_cimis_time = 90
    water_flag, motion_flag = False, False
    
    t = None
    global ce, ct, ch
    ce, ct, ch = -1, -1, -1
    bottom_message, top_message = None, None
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
                
                if water_time_remaining == 0:
                    water_flag = False
                    continue

                print("water time remaining: ", water_time_remaining)
                water_time_remaining -= 1
                # poll both the Relay and LCD modules
                GPIO.output(relayPin, GPIO.LOW)
                lcd.clear()
                lcd.setCursor(0,0)
                lcd.message(top_message)
                top_message = top_message[1:] + top_message[0]
                lcd.setCursor(0,1)
                lcd.message(bottom_message)
                bottom_message = bottom_message[1:] + bottom_message[0]
                sleep(1)                
                GPIO.output(relayPin, GPIO.HIGH)
        else:    
            lcd.clear()
            time_diff = int(time() - init_time)
            # poll the DHT sensor every minute
            # and display on the LCD
            if (time_diff) % polling_dht_time == 0:
                temp, humidity = process_DHT_data()
                totalTemp = avgTemp + temp
                totalHumidity = avgHumidity + humidity
                top_message = "t:{} h:{} at:{} ah:{} ".format(temp, humidity, avgTemp, avgHumidity)
                    

            if (time_diff) % polling_cimis_time == 0:
                print("inCIMIS")

                # do while loop to wait until cimis data has been
                # retrieved (if URLerror, etc. occurs, just restart
                # the thread)
                cimis_init_time = time()
                while True:
                    t = threading.Thread(target = cimis_thread)
                    t.start()
                    t.join()
                    if (ce > -1 and ct > -1 and ch > -1) or (time() - cimis_init_time > 10):
                        break

                eto = ce/ct*temp

                ce = float("{0:.2f}".format(ce))
                ct = float("{0:.2f}".format(ct))
                ch = float("{0:.2f}".format(ch))
                water_diff = float("{0:.2f}".format(calc_water(ce) - calc_water(eto)))
                avgTemp = float("{0:.2f}".format(totalTemp/60))
                avgHumidity = float("{0:.2f}".format(totalHumidity/60)) 
                
                bottom_message = "ce:{} ct:{} ch:{} sav:{} ".format(ce, ct, ch, water_diff)
                water_flag = True
                water_time_duration = calc_water(eto)/100
                water_time_duration = 1 if water_time_duration < 1 else water_time_duration
                water_time_remaining = int(water_time_duration)
                totalTemp, totalHumidity = 0, 0


            lcd.setCursor(0, 0)
            lcd.message(top_message)
            top_message = top_message[1:] + top_message[0]
            lcd.setCursor(0,1)
            lcd.message(bottom_message)
            bottom_message = bottom_message[1:] + bottom_message[0]
       
            if (time_diff) % 86400 == 86399:
                init_time = time()

            
            print("time diff",time_diff)
            sleep(0.2)  
        



def destroy():
    lcd.clear()
    GPIO.output(relayPin, GPIO.LOW)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        run()
    except KeyboardInterrupt:
        destroy()
