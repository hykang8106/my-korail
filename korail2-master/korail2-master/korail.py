# -*- coding: utf-8 -*-

# sudo pip install --upgrade git+https://github.com/carpedm20/korail2.git@sng2c

from korail2 import *
import time
import sys

RESERVE_TRAIN = False

KORAIL_ID = '0473157658'
KORAIL_PW = 'uresj35805!'

PUSHOVER_APP_TOKEN = 'APP_TOKEN'
PUSHOVER_USER_TOKEN = 'USER_TOKEN'

DEP = '부강'
ARV = '조치원'
# DEP = '오송'
# ARV = '서울'
DEP_DATE = '20220930'
DEP_TIME = '190000'
PSGRS = [AdultPassenger(1)]
TRAIN_TYPE = TrainType.MUGUNGHWA
# TRAIN_TYPE = TrainType.KTX
# TRAIN_TYPE = TrainType.ITX_CHEONGCHUN


def sendnoti(msg):
    pass
    
k = Korail(KORAIL_ID, KORAIL_PW, auto_login=False)
if not k.login():
    print("login fail")
    exit(-1)
while True:
    notFound = True
    while notFound:
        try:
            # sys.stdout.write( "Finding Seat %s ➜ %s              \r" %(DEP, ARV) )
            # sys.stdout.flush()
            trains = k.search_train_allday(DEP, ARV, DEP_DATE, DEP_TIME, passengers=PSGRS, train_type=TRAIN_TYPE)
            print("##### Found!!")
            for t in trains:
                print(t)
            
            notFound = False
        except NoResultsError:
            sys.stdout.write("No Seats                               \r")
            sys.stdout.flush()
            time.sleep(2)
        except Exception as e:
            print(e)
            time.sleep(2)

    k.login()
    seat = None
    ok = False

    if RESERVE_TRAIN:
        try:
            seat = k.reserve(trains[0], passengers=PSGRS)
            ok = True
        except KorailError as e:
            print(e)
            sendnoti(e)
            break
    

    if ok:
        print(seat)
        sendnoti(repr(seat))
        break

    time.sleep(3)
