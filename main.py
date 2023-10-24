from config import *
import requests
import json
from datetime import datetime
import time

dt = datetime.fromtimestamp(1696680000)
#print(dt)

month_to_num={
    "January":1,
    "February":2,
    "March":3,
    "April":4,
    "May":5,
    "June":6,
    "July":7,
    "August":8,
    "September":9,
    "October":10,
    "November":11,
    "December":12
}


class PumpPair:
    def __init__(self, pair):
        self.pair       = pair
        self.buy_zone   = 0
        self.target_1   = 0
        self.target_2   = 0
        self.target_3   = 0
        self.target_4   = 0
        self.target_5   = 0
        self.time       = 0
        self.date       = 0

    def get_pair(self):
        print(self.pair)

    def get_targets(self):
        #print(self.target_1, self.target_2, self.target_3, self.target_4, self.target_5)
        return [self.target_1, self.target_2, self.target_3, self.target_4, self.target_5]

    def get_info(self):
        print(self.target_1, self.target_2, self.target_3, "date: ", self.date, "time", self.time)


    def set_text(self, text):
        self.text = text

    def set_buy(self, buy_zone):
        self.buy_zone = buy_zone

    def set_target_1(self, target_1):
        self.target_1 = target_1

    def set_target_2(self, target_2):
        self.target_2 = target_2

    def set_target_3(self, target_3):
        self.target_3 = target_3

    def set_target(self, target, number):
        if number == 1:
            self.target_1 = target
        elif number == 2:
            self.target_2 = target
        elif number == 3:
            self.target_3 = target
        elif number == 4:
            self.target_4 = target
        elif number == 5:
            self.target_5 = target


    def set_time(self, time):
        self.time = time

    def set_date(self, date):
        self.date = date


def date_time_translate(date_time):
    print("date_time: ", date_time)
    if len(date_time[0])>1:
        return datetime(2023, int(month_to_num[date_time[0]]), int(date_time[1]), int(date_time[2]), int(date_time[3]))
    else:
        return datetime(2023, int(date_time[5:6]), int(date_time[8:9]), int(date_time[11:12]), int(date_time[14:15]))


def get_targets(pump_pair):
    for i in range(1,6):
        try:
            target = re.search((r'@ Target {}: \d*[.]*\d*'.format(i)), pump_pair.text)
            if target == None:
                target = re.search((r'@ Target{}: \d*[.]*\d*'.format(i)), pump_pair.text)
            print('found: ', target, i)
            pump_pair.set_target(str(target.group()).split(":")[1], i)
        except:
            print("no target {} info".format(i))


def parse_img(img, message_time):
    text = pytesseract.image_to_string(img)

    pair = re.search(r"[A-Za-z]+\/+[A-Za-z]+ ", text)

    if pair == None:
        return 0
    else:
        pair = str(pair.group())[0:-1]
        #print(pair)
        pump_pair = PumpPair(pair)
        pump_pair.set_text(text)
        get_targets(pump_pair)
        a = pump_pair.get_targets()
        print("THE TARGETS: ", a)
        try:
            time_t = re.search(r'([0-1]?[0-9]|2[0-3]):[0-5][0-9]', text)
            pump_pair.set_time(str(time_t.group()))
            print(str(time_t.group()))
            pump_pair.set_date(text.split("\n")[0])
            print(text.split("\n")[0])
        except Exception as e:
            print("no time info")
            print(e)
        #print('THE IMAGE TEXT: \n', pump_pair.text)


        if pump_pair.get_targets()[0] == pump_pair.get_targets()[1]:
            print('Not pump')
            return 0
        pump_pair.get_info()
        print("time: ",pump_pair.time)
        print("date: ",pump_pair.date)
        date=pump_pair.date.split(' ')+pump_pair.time.split(':')

        date = date_time_translate(date)
        message_time = date_time_translate(message_time)

        date=time.mktime(date.timetuple())
        message_time = time.mktime(message_time.timetuple())
        #print("".join(pump_pair.pair.split('/')), int(date)*1000)
        result = float(request_data("".join(pump_pair.pair.split('/')), int(date)*1000, message_time*1000))
        print("Current price of {}: {}".format(pump_pair.pair, result))
        targets = pump_pair.get_targets()
        print("teoritical profit from targets:")
        for i in range(1,6):
            try:
                target = float(targets[i-1])
                if target != 0:
                    print("target {}: ".format(target), (result * 100 / target) - 100)
            except:
                print("no target ")
                continue

def request_data(symbol, start_time, end_time):
    print(symbol, start_time, end_time)
    x = requests.get(r'https://api.binance.com/api/v3/klines?symbol={}&interval=1h&startTime={}'.format(symbol, start_time))
    #print(x.status_code)
    y="'bars':{"
    y+=x.text
    y+="}"
    #print(y)
    max_price = 0
    aList = json.loads(x.text)
    print(aList)
    for i in aList:
        print("date: ", datetime.fromtimestamp(i[0]/1000), "price: ", i[2])
    for i in aList:
        if float(i[2]) > float(max_price):
            max_price = i[2]
    #print(x.headers)
    return max_price




client=TelegramClient('test', api_id, api_hash)


user_input_channel = 't.me/Bitcoin_Pump_Signal_usdt', 'me'  # Within the client:
subjectFilter = ['physics', 'mathematics', 'maths', 'math']
levelFilter = ['sec', 'secondary', 'junior college', 'jc']
#request_data()


@client.on(events.NewMessage(chats=user_input_channel))
async def newMessageListener(event):
    newMessage = event.message.message
    print("The message: ", str(event.message))
    message_time = str(event.message.date)[:-9]
    print(message_time)
    path = await client.download_media(event.message, thumb=-1)
    print("path is ", path)
    img1 = np.array(Image.open(path))
    parse_img(img1, message_time)

with client:
    client.run_until_disconnected()