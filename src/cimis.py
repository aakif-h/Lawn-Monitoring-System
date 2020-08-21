# Author: Aakif Hussaini
# Date: June 11, 2019
# Desc: To read from CIMIS database and find an Eto value to be used in determining
#       duration of sprinkling the lawn


from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError
from datetime import datetime, date, timedelta
import json


# processing of CIMIS data
def process_CIMIS_data():
    url = "http://et.water.ca.gov/api/data"

    # unique key from registering on CIMIS website
    appKey = '5b7615cd-a019-4dda-9875-34edff9f0a00'

    # Number corresponding to Irvine station
    stationNum = '75'

    # should be parsing data from the current time
    # (using yesterday's information to resolve cases like when data has not been updated at the start of a new day)
    startDate = (date.today() - timedelta(days=1)).isoformat()
    endDate = date.today().isoformat()

    #
    dataItems = [
        'hly-air-tmp',
        #      'hly-dew-pnt',
        'hly-eto',
        #      'hly-net-rad',
        #      'hly-asce-eto',
        #      'hly-asce-etr',
        #      'hly-precip',
        'hly-rel-hum',
        #      'hly-res-wind',
        #      'hly-soil-tmp',
        #      'hly-sol-rad',
        #      'hly-vap-pres',
        #      'hly-wind-dir',
        #      'hly-wind-spd'
    ]
    dataItems = ','.join(dataItems)

    params = {
        'appKey': appKey,
        'targets': stationNum,
        'startDate': startDate,
        'endDate': endDate,
        'dataItems': dataItems,
        'unitOfMeasure': 'M'  # metric units
    }

    query = urlencode(params)

    full_url = url + '?' + query
    try:
        response = urlopen(full_url)
        decoded_string = response.read().decode('utf-8')

        json_obj = json.loads(decoded_string)
        return get_ETo(json_obj)
    except (URLError, ConnectionResetError, ConnectionRefusedError, json.decoder.JSONDecodeError) as e:
        print("The following exception occured: ", e)
        return -1, -1, -1



# get the ETo
def get_ETo(json_obj):
    print(datetime.now().hour)
    
    this_hour = int(datetime.now().hour - 5) * 100
    this_day = date.today().isoformat()



    if this_hour <= 0:
        this_hour = this_hour + 2400
        this_day = (date.today() - timedelta(days=1)).isoformat()


    data_list = []
    append_flag = 0
    count = 0
    for i in json_obj['Data']['Providers']:
        for j in i['Records']:
            if this_hour == int(j['Hour']) and this_day == j['Date']:
                append_flag = 1
            if append_flag:
                print(j['Hour'], j['HlyEto']['Value'], j['HlyAirTmp']['Value'], j['HlyRelHum']['Value'])

                eto = float(j['HlyEto']['Value']) if j['HlyEto']['Value'] != None else -1
                temp = float(j['HlyAirTmp']['Value']) if j['HlyAirTmp']['Value'] != None else -1
                hum = float(j['HlyRelHum']['Value']) if j['HlyRelHum']['Value'] != None else -1
                data_list.append([ eto, temp, hum ])

                count = count + 1
            if count >= 6:
                break
    return calc_data(data_list)

# calculation of ETo
def calc_data(data_list):
    if data_list[-1][0] != -1:
        CIMIS_ETo = data_list[-1][0]
    else:
        CIMIS_ETo = getAverage(data_list[:5], 0)

    if data_list[-1][1] != -1:
        CIMIS_temp = data_list[-1][1]
    else:
        CIMIS_temp = getAverage(data_list[:5], 1)

    if data_list[-1][2] != -1:
        CIMIS_humidity = data_list[-1][2]
    else:
        CIMIS_humidity = getAverage(data_list[:5], 2)
    
   

    # for later handling of discrepancies in data
    if CIMIS_temp <= 0:
        print("something happened to temp")
        CIMIS_temp = -1
    if CIMIS_humidity == 0:
        print("something happened to humidity")
        CIMIS_humidity = -1
    
    return CIMIS_ETo, CIMIS_temp, CIMIS_humidity

def getAverage(float_list, index):

    temp_list = []
    for i in range(len(float_list)):
        temp_list.append(float_list[i][index])

    count = 0
    sum = 0
    for i in temp_list:
        sum = sum + i
        count = count + 1

    count = 1 if count == 0 else count
    return sum / count

# main thread
"""
if __name__ == "__main__":
    eto, temp, hum = process_CIMIS_data()
    print('e: ', eto, '\tt: ', temp, '\th: ', hum)
"""

