import pandas as pd
import string
import random
import datetime
import time
import numpy as np


# function to generate an ID
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# function to generate a normal distribution within a range
from scipy.stats import truncnorm


def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


# use get_truncated_normal(...).rvs(number)

# function to generate a random time string within a range
def randomtimes(stime="2019-05-10 10:00:00", etime="2019-05-10 22:00:00", format='%Y-%m-%d %H:%M:%S', n=5):
    """
    :param stime: start time
    :param etime: end time
    :param n: number of timestamps
    :return: a list of timestamps
    """
    start = datetime.datetime.strptime(stime, format)
    end = datetime.datetime.strptime(etime, format)
    td = end - start
    return [(get_truncated_normal(mean=0.4, sd=0.5, low=0, upp=1).rvs() * td + start).strftime(format) for _ in
            range(n)]


# simulate 1-day data
random.seed(233)

# table "face_camera"

# number of rows
nrow = 2000

# timestamp in readable format
timestamp1 = randomtimes(n=nrow)
# convert string to datetime object
timestamp1 = [datetime.datetime.strptime(timestamp1[d], '%Y-%m-%d %H:%M:%S') for d in range(len(timestamp1))]
# convert datetime to nanosecond
# timestamp1 = [int(time.mktime(timestamp1[d].timetuple()) * 1000000000) for d in range(len(timestamp1))]
# order timestamp
timestamp1.sort()

# other variables
cameraID = [1] * nrow
faceID = [id_generator(6) for _ in range(nrow)]
age = [int(get_truncated_normal(mean=40, sd=10, low=10, upp=70).rvs()) for _ in range(nrow)]
gender = random.choices(['Female', 'Male', 'Unknown'], [0.4, 0.4, 0.2], k=nrow)
customerType = random.choices(['新客', '老客'], [0.8, 0.2], k=nrow)
mood = random.choices(['开心', '中性'], [0.3, 0.7], k=nrow)
accompany = [random.choice(['有伴', '无伴']) for _ in range(nrow)]
zoneID = random.choices(['outdoor', 'in'], [0.8, 0.2], k=nrow)

# create a data frame
face_camera = pd.DataFrame({
    'timestamp': timestamp1,
    'cameraID': cameraID,
    'faceID': faceID,
    'gender': gender,
    'age': age,
    'customerType': customerType,
    'mood': mood,
    'accompany': accompany,
    'zoneID': zoneID
})

# save the data frame using influx line protocol
face_camera_lines = ["faceCamera2"  # measurement/table name
                     + ","  # comma between measurement and tags
                     # tags are for filtering/group-by features
                     # and do not need double quotes tag name and tag value
                     + "cameraID=" + str(face_camera["cameraID"][d])
                     + " "  # white space between tags and fields
                     # fields are dynamic
                     # string has to be surrounded by double quotes,
                     # integer needs to add "i" after the number
                     + "faceID=" + '"' + str(face_camera["faceID"][d]) + '"' + ","
                     + "age=" + str(face_camera["age"][d]) + "i" + ","
                     + "gender=" + '"' + str(face_camera["gender"][d]) + '"' + ","
                     + "customerType=" + '"' + str(face_camera["customerType"][d]) + '"' + ","
                     + "mood=" + '"' + str(face_camera["mood"][d]) + '"' + ","
                     + "accompany=" + '"' + str(face_camera["accompany"][d]) + '"'
                     + " "  # white space between fields and timestamp
                     + str(face_camera["timestamp"][d]) for d in range(len(face_camera))]

# export the lines to a txt
thefile = open('faceCamera.txt', 'w')
for item in face_camera_lines:
    thefile.write("%s\n" % item)

face_camera.to_csv('face_camera.csv', index=False)

# table "IEQ" from sensors
random.seed(233)
nrow = 240 * 4

# variables
# generate time series with incremental = 6 minutes
one_series = pd.date_range('2019-05-10', periods=240, freq='0.1H').strftime("%Y-%m-%d %H:%M:%S").tolist()
timestamp2 = one_series * 4
# convert string to datetime object
timestamp2 = [datetime.datetime.strptime(timestamp2[d], '%Y-%m-%d %H:%M:%S') for d in range(len(timestamp2))]
# convert datetime to nanosecond
# timestamp2 = [int(time.mktime(timestamp2[d].timetuple()) * 1000000000) for d in range(len(timestamp2))]


# 4 zones
zoneID = sorted(['进门区', '中区1', '中区2', '里间'] * 240)

# temperature sin function
fs = 240  # sample number
f = 1  # the frequency of the signal
x = np.arange(fs)  # the points on the x axis for plotting
# compute the value (amplitude) of the sin wave at the for each sample
# highest temp = 28 at 2pm, lowest temp = 22 at 2am
temp3 = 3 * np.sin(2 * np.pi * f * ((x - 80) / fs)) + 25 + random.uniform(-0.5, 0.5)
# each zone temp is a bit different
temp2 = (temp3 + 2).round(2).tolist()
temp2 = [x + random.uniform(-0.5, 0.5) for x in temp2]
temp1 = (temp3 + 2.5).round(2).tolist()
temp1 = [x + random.uniform(-0.5, 0.5) for x in temp1]
temp4 = (temp3 + 3).round(2).tolist()
temp4 = [x + random.uniform(-0.5, 0.5) for x in temp4]
temp3 = temp3.round(2).tolist()
temp3 = [x + random.uniform(-0.5, 0.5) for x in temp3]
# combine the 4 zones
temp = temp1 + temp2 + temp3 + temp4


# CO2, constant 400 ppm, start to increase at 8 am, and then decrease
def f(time):
    T = time
    Ts1 = 80
    ind = 0
    t_axis = np.arange(T)
    ft = np.arange(T)

    for t in t_axis:
        if 80 <= t:
            ft[ind] = 600 * np.sin(2 * np.pi * (t - Ts1) / Ts1 / 4) + 400 + random.uniform(-30, 30)
            ind += 1
        else:
            ft[ind] = 400 + random.uniform(-20, 20)
            ind += 1
    return ft


CO2 = f(240).tolist() + f(240).tolist() + f(240).tolist() + f(240).tolist()

# PM2.5, mean 200, sd 50, 0~400, PM2.5 ug/m3
PM = get_truncated_normal(mean=200, sd=50, low=0, upp=400)
PMvalue = [int(x) for x in PM.rvs(nrow)]
# RH mean 55, sd 5, 0~100%
RH = get_truncated_normal(mean=55, sd=5, low=0, upp=100)
RHvalue = [int(x) for x in RH.rvs(nrow)]
# mean 0.05, sd 0.05, 0.01~1, m/s
air_speed = get_truncated_normal(mean=5, sd=2, low=1, upp=100)  # note this function cannot take float inputs
airSpeedValue = [round(x, 2) for x in air_speed.rvs(nrow) / 100]
# mean 0.6, sd 1.0, 0~4 mg/m3
TVOC = get_truncated_normal(mean=6, sd=2, low=0, upp=40)
TVOCvalue = [round(x, 2) for x in TVOC.rvs(nrow) / 10]
# mean 0.004, sd 0.07, 0~1 mg/m3
formaldehyde = get_truncated_normal(mean=4, sd=4, low=0, upp=1000)
formaldehydeValue = [round(x, 3) for x in formaldehyde.rvs(nrow) / 1000]

# create the dataframe
sensor = pd.DataFrame({
    'timestamp': timestamp2,
    'zoneID': zoneID,
    'temp': temp,
    'RH': RHvalue,
    'air_speed': airSpeedValue,
    'CO2': CO2,
    'PM': PMvalue,
    'TVOC': TVOCvalue,
    'formaldehyde': formaldehydeValue
})

# save the data frame using influx line protocol
IEQ_lines = ["IEQ"  # measurement/table name
             + ","  # comma between measurement and tags
             # tags are for filtering/group-by features
             # and do not need double quotes tag name and tag value
             + "zoneID=" + str(sensor["zoneID"][d])
             + " "  # white space between tags and fields
             # fields are dynamic
             # string has to be surrounded by double quotes,
             # integer needs to add "i" after the number
             + "temp=" + str(sensor["temp"][d]) + ","
             + "RH=" + str(sensor["RH"][d]) + "i,"
             + "airSpeed=" + str(sensor["air_speed"][d]) + ","
             + "CO2=" + str(sensor["CO2"][d]) + "i,"
             + "PM=" + str(sensor["PM"][d]) + "i,"
             + "TVOC=" + str(sensor["TVOC"][d]) + ","
             + "formaldehyde=" + str(sensor["formaldehyde"][d])
             + " "  # white space between fields and timestamp
             + str(sensor["timestamp"][d]) for d in range(len(sensor))]

# export the lines to a txt
thefile = open('IEQ.txt', 'w')
for item in IEQ_lines:
    thefile.write("%s\n" % item)

sensor.to_csv('IEQ.csv', index=False)

# table "track camera"
random.seed(233)

# timestamp the subject enters the "from_zone" in readable format
# assume from 10 to 11, 30 movements
# from 11 to 14, 260 movements
# from 14 to 18, 200 movements
# from 18 to 22, 600 movements
timestamp3 = randomtimes(stime="2019-05-10 10:00:00", etime="2019-05-10 11:00:00", n=50) + randomtimes(
    stime="2019-05-10 11:00:00", etime="2019-05-10 14:00:00", n=300) + randomtimes(stime="2019-05-10 14:00:00",
                                                                                   etime="2019-05-10 18:00:00",
                                                                                   n=251) + randomtimes(
    stime="2019-05-10 18:00:00", etime="2019-05-10 22:00:00", n=600)
# convert string to datetime object
timestamp3 = [datetime.datetime.strptime(timestamp3[d], '%Y-%m-%d %H:%M:%S') for d in range(len(timestamp3))]
random.shuffle(timestamp3)

# cameraID, assume only one track camera covers four zones
nrow = 1201
cameraID = [2] * nrow

# zoneID the subject came from
from_zone = ['进门区'] * 545 + ['中区1'] * 302 + ['中区2'] * 243 + ['里间'] * 111
to_zone = ['中区1'] * 302 + ['中区2'] * 243 + ['进门区'] * 153 + ['中区2'] * 119 + ['里间'] * 30 + ['中区1'] * 138 + [
    '里间'] * 81 + ['进门区'] * 24 + ['中区1'] * 51 + ['中区2'] * 60

# time the subject stayed in the from_zone, unit in second
stay1 = get_truncated_normal(mean=90, sd=30, low=5, upp=1800).rvs(545).tolist()
stay2 = get_truncated_normal(mean=500, sd=100, low=5, upp=1800).rvs(302).tolist()
stay3 = get_truncated_normal(mean=300, sd=100, low=5, upp=1800).rvs(243).tolist()
stay4 = get_truncated_normal(mean=300, sd=200, low=5, upp=1800).rvs(111).tolist()
stay = stay1 + stay2 + stay3 + stay4
stay = [int(x) for x in stay]

# create the dataframe
track = pd.DataFrame({
    'timestamp': timestamp3,
    'cameraID': cameraID,
    'from': from_zone,
    'to': to_zone,
    'stay': stay
})

track.sort_values(by=['timestamp'], inplace=True)

track.to_csv('track_camera.csv', index=False)

# convert datetime to nanosecond
track['timestamp'] = [int(time.mktime(track['timestamp'][d].timetuple()) * 1000000000) for d in
                      range(len(track['timestamp']))]

# save the data frame using influx line protocol
track_lines = ["track"  # measurement/table name
               + ","  # comma between measurement and tags
               # tags are for filtering/group-by features
               # and do not need double quotes tag name and tag value
               + "cameraID=" + str(track["cameraID"][d])
               + " "  # white space between tags and fields
               # fields are dynamic
               # string has to be surrounded by double quotes,
               # integer needs to add "i" after the number
               + "from=" + '"' + str(track["from"][d]) + '"' + ","
               + "to=" + '"' + str(track["to"][d]) + '"' + ","
               + "stay=" + str(track["stay"][d]) + 'i'
               + " "  # white space between fields and timestamp
               + str(track["timestamp"][d]) for d in range(len(track))]

# export the lines to a txt
thefile = open('trackCamera.txt', 'w')
for item in track_lines:
    thefile.write("%s\n" % item)

# intermediate table "SKU"

random.seed(233)
# in 2018
date = pd.date_range(start='2018-1-1', end='2018-12-31', freq='D').strftime("%Y-%m-%d").tolist()
day_num = len(date)
date = sorted(date * 12)
SKU = ['4D磁悬浮', '月光宝盒', '乳胶', '椰棕', '软硬两面', '云朗', '蒂斯', '舒缦', '畅眠', '小喜', '诺蓝', '尊亲'] * day_num
zoneID = ['进门区', '进门区', '中区1', '中区1', '中区1', '中区2', '中区2', '里间', '里间', '里间', '里间', '里间'] * day_num
try_num = [210, 200, 60, 40, 120, 90, 80, 30, 40, 50, 60, 55] * 90 + [180, 170, 30, 30, 80, 70, 30, 20, 10, 20, 20,
                                                                      15] * 91 + [200, 190, 50, 30, 100, 80, 40, 20, 20,
                                                                                  30, 35, 25] * 92 + [210, 200, 60, 40,
                                                                                                      120, 90, 80, 30,
                                                                                                      40, 50, 60,
                                                                                                      55] * 92
try_num = [int(x + random.uniform(-10, 10)) for x in try_num]  # add some randomness
transaction_num = [50, 20, 5, 5, 8, 20, 5, 5, 5, 5, 10, 5] * 90 + [40, 30, 5, 5, 10, 15, 5, 5, 5, 5, 10, 5] * 91 + [40,
                                                                                                                    20,
                                                                                                                    10,
                                                                                                                    10,
                                                                                                                    8,
                                                                                                                    20,
                                                                                                                    5,
                                                                                                                    5,
                                                                                                                    10,
                                                                                                                    5,
                                                                                                                    10,
                                                                                                                    5] * 92 + [
                      55, 30, 5, 5, 8, 15, 5, 5, 5, 5, 10, 5] * 92
transaction_num = [int(x + random.uniform(-5, 5)) for x in transaction_num]
unit_profit = [1800, 1600, 1500, 1400, 1200, 1800, 2000, 2500, 1500, 1300, 1200, 1600] * day_num
unit_profit = [int(x + random.uniform(-100, 100)) for x in unit_profit]
profit_day_sum = list(x * y for x, y in list(zip(unit_profit, transaction_num)))

# create the dataframe
SKU = pd.DataFrame({
    'date': date,
    'zoneID': zoneID,
    'SKU': SKU,
    'try_num': try_num,
    'transaction_num': transaction_num,
    'unit_profit': unit_profit,
    'profit_day_sum': profit_day_sum
})

SKU.to_csv('SKU_year.csv', index=False)

# table "store_comparison_year"
random.seed(233)
city = ['Beijing'] * 5 + ['Shanghai'] * 5 + ['Shenzhen'] * 3 + ['Changsha'] * 3 + ['Hangzhou'] * 3
storeID = ['西单', '王府井', '中关村', '望京', '双安', '南京西路', '淮海中路', '五角场', '徐家汇', '虹桥', '华侨城', '罗湖', '东门', '火车站', '五一路', '东塘',
           '万象城', '武林银泰', '西湖']

ppl_day = []
in_rate = []
conv_rate = []
avg_day_profit = []
zone_diff = []

for x in range(len(storeID)):
    if x < 5:  # Beijing
        ppl_day.append(int(random.uniform(1500, 3000)))
        in_rate.append(round(random.uniform(0.1, 0.6), 2))
        conv_rate.append(round(random.uniform(0.05, 0.5), 2))
        avg_day_profit.append(int(random.uniform(15e4, 40e4)))
        zone_diff.append(round(random.uniform(1, 4), 2))
    elif x < 10:  # Shanghai
        ppl_day.append(int(random.uniform(2000, 4000)))
        in_rate.append(round(random.uniform(0.15, 0.5), 2))
        conv_rate.append(round(random.uniform(0.1, 0.4), 2))
        avg_day_profit.append(int(random.uniform(15e4, 60e4)))
        zone_diff.append(round(random.uniform(1, 3), 2))
    elif x < 13:  # Shenzhen
        ppl_day.append(int(random.uniform(1800, 3500)))
        in_rate.append(round(random.uniform(0.1, 0.3), 2))
        conv_rate.append(round(random.uniform(0.1, 0.25), 2))
        avg_day_profit.append(int(random.uniform(15e4, 35e4)))
        zone_diff.append(round(random.uniform(1, 3.5), 2))
    elif x < 16:  # Changsha
        ppl_day.append(int(random.uniform(1600, 3000)))
        in_rate.append(round(random.uniform(0.1, 0.5), 2))
        conv_rate.append(round(random.uniform(0.15, 0.4), 2))
        avg_day_profit.append(int(random.uniform(10e4, 40e4)))
        zone_diff.append(round(random.uniform(1, 4), 2))
    elif x < 19:  # Hangzhou
        ppl_day.append(int(random.uniform(2000, 3800)))
        in_rate.append(round(random.uniform(0.1, 0.4), 2))
        conv_rate.append(round(random.uniform(0.1, 0.5), 2))
        avg_day_profit.append(int(random.uniform(15e4, 40e4)))
        zone_diff.append(round(random.uniform(1, 3.5), 2))

store_comp = pd.DataFrame({
    'city': city,
    'storeID': storeID,
    'ppl_day': ppl_day,
    'in_rate': in_rate,
    'conv_rate': conv_rate,
    'avg_day_profit': avg_day_profit,
    'zone_diff': zone_diff
})

store_comp.to_csv('store_comp_year.csv', index=False)


# table 'face_year'
random.seed(233)
Date = pd.date_range('2018-01-01', '2018-12-31', freq='D').strftime("%Y-%m-%d").tolist()
weekday = pd.date_range('2018-01-01', '2018-12-31', freq='D').strftime("%A").tolist()
in_rate = []
conv_rate = []
female_pc = []
return_customer_pc = []
happy_pc = []
accompany_pc = []
is_weekend = []

for i in range(len(weekday)):
    if weekday[i] == 'Saturday' or weekday[i] == 'Sunday':
        is_weekend.append(1)
        in_rate.append(round(random.uniform(0.3, 0.5), 2))
        conv_rate.append(round(random.uniform(0.2, 0.4), 2))
        female_pc.append(round(random.uniform(0.5, 0.65), 2))
        return_customer_pc.append(round(random.uniform(0.1, 0.25), 2))
        happy_pc.append(round(random.uniform(0.3, 0.6), 2))
        accompany_pc.append(round(random.uniform(0.4, 0.7), 2))
    else:
        is_weekend.append(0)
        in_rate.append(round(random.uniform(0.1, 0.35), 2))
        conv_rate.append(round(random.uniform(0.15, 0.35), 2))
        female_pc.append(round(random.uniform(0.4, 0.6), 2))
        return_customer_pc.append(round(random.uniform(0.1, 0.25), 2))
        happy_pc.append(round(random.uniform(0.25, 0.4), 2))
        accompany_pc.append(round(random.uniform(0.4, 0.5), 2))


face_year = pd.DataFrame({
    'Date': Date,
    'weekday': weekday,
    'is_weekend': is_weekend,
    'in_rate': in_rate,
    'conv_rate': conv_rate,
    'female_pc': female_pc,
    'return_customer': return_customer_pc,
    'happy': happy_pc,
    'accompany': accompany_pc
})


face_year.to_csv('face_year.csv', index=False)