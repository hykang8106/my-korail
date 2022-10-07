# [ref] https://github.com/carpedm20/korail2
#
# "requests" module document:
# [ref] https://requests.readthedocs.io/en/latest/user/quickstart/
import requests
import sys
from datetime import datetime, timedelta

from os.path import exists
import json

from time import sleep
import pandas as pd
from tabulate import tabulate # to print dataframe nice


SCHEME = "https"
KORAIL_HOST = "smart.letskorail.com"
KORAIL_PORT = "443"

KORAIL_DOMAIN = "{}://{}:{}".format(SCHEME, KORAIL_HOST, KORAIL_PORT)
KORAIL_MOBILE = "{}/classes/com.korail.mobile".format(KORAIL_DOMAIN)

KORAIL_LOGIN = "{}.login.Login".format(KORAIL_MOBILE)
KORAIL_LOGOUT = "{}.common.logout".format(KORAIL_MOBILE)
KORAIL_SEARCH_SCHEDULE = "{}.seatMovie.ScheduleView".format(KORAIL_MOBILE)
KORAIL_TICKETRESERVATION = "{}.certification.TicketReservation".format(KORAIL_MOBILE)
KORAIL_MYRESERVATIONLIST = "{}.reservation.ReservationView".format(KORAIL_MOBILE)
KORAIL_MYTICKETLIST = "{}.myTicket.MyTicketList".format(KORAIL_MOBILE)
KORAIL_MYTICKET_SEAT = "{}.refunds.SelTicketInfo".format(KORAIL_MOBILE)
KORAIL_CANCEL = "{}.reservationCancel.ReservationCancelChk".format(KORAIL_MOBILE)
KORAIL_STATION_DB = "{}.common.stationdata".format(KORAIL_MOBILE)

DEFAULT_USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 5.1.1; Nexus 4 Build/LMY48T)"

_device = 'AD'
_version = '190617001'
_key = 'korail1234567890'

station_DB_file = "korail_station_DB.txt"
login_info_file = "korail_login_info.txt"

train_type_menu = \
"""
    k = KTX/KTX-산천, s = 새마을호, m = 무궁화호, t = 통근열차, 
    n = 누리로, p = 공항직통, ic = ITX-청춘, is = ITX-새마을, a = 전체
"""

train_type_dict = {
    'k' : '100', # "KTX, KTX-산천"
    's' : '101', # "새마을호"
    'm' : '102', # "무궁화호"
    't' : '103', # "통근열차"
    'n' : '102', # "누리로"
    'a' : '109', # "전체"
    'p' : '105', # "공항직통"
    'ic' : '104', # "ITX-청춘"
    'is' : '101', # "ITX-새마을"
}

top_menu = \
"""
    [top menu]
    "search train only(not seat check)" = 1
    "search and reserve train" = 2
    "show reservations" = 3
    "cancel reservations" = 4
    "get tickets" = 5
    "reserve specific train" = 6
    "end program" = x
"""

# [ref] https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
# "How to pretty print nested dictionaries?"
def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))

def response_is_success(r):

    '''
    check http response is success
    '''

    if r.status_code == 200:
        return True
    else:
        return False

def result_is_success(j):

    '''
    check http response result is success
    '''

    if j['strResult'] == 'SUCC':
        return True
    else:
        return False

def get_station_DB():

    '''
    get station DB

    return station DB, which is list of station dictionary

    station dictionary example:
    {
        "stn_cd": "0001", 
        "stn_nm": "서울", 
        "longitude": "126.9708191", 
        "latitude": "37.551856", 
        "group": "7", # 의미?
        "major": "1", # 없는 경우도 있음. 큰 역일 경우 있는듯
        "popupMessage": "", 
        "popupType": "0"
    }
    '''

    if not exists(station_DB_file):
        url = KORAIL_STATION_DB
        r = requests.get(url)
        if response_is_success(r):
            j = r.json()
            station_DB = j['stns']['stn']

            print("save station_DB into \"{}\" file".format(station_DB_file))
            json.dump(station_DB, open(station_DB_file, 'w'), ensure_ascii=False)

            return station_DB
        else:
            return []
    else:
        # print("load station_DB from \"{}\" file".format(station_DB_file))
        station_DB = json.load(open(station_DB_file)) 

        return station_DB

""" 
import json

# Serialize data into file:
json.dump( data, open("file_name.json", 'w'))

# Read data from file:
data = json.load(open("file_name.json")) 
"""


def init_session():

    """ 
    [ref] https://requests.readthedocs.io/en/latest/user/advanced/

    [Session Objects]
    The Session object allows you to persist certain parameters across requests. 
    It also persists cookies across all requests made from the Session instance, 
    and will use urllib3’s connection pooling. 
    So if you’re making several requests to the same host, 
    the underlying TCP connection will be reused, 
    which can result in a significant performance increase (see HTTP persistent connection).

    A Session object has all the methods of the main Requests API.

    s = requests.Session()

    s.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
    r = s.get('https://httpbin.org/cookies')

    print(r.text)
    # '{"cookies": {"sessioncookie": "123456789"}}'
    """
    s = requests.Session()

    """ 
    Sessions can also be used to provide default data to the request methods. 
    This is done by providing data to the properties on a Session object:

    s = requests.Session()
    s.auth = ('user', 'pass')
    s.headers.update({'x-test': 'true'})

    # both 'x-test' and 'x-test2' are sent
    s.get('https://httpbin.org/headers', headers={'x-test2': 'true'})
    """
    s.headers.update({'User-Agent': DEFAULT_USER_AGENT}) 

    return s

def login_korail(s, korail_id, korail_pw):

    # 2: for membership number
    # 4: for phone number
    # 5: for email
    txt_input_flg = '2'

    url = KORAIL_LOGIN
    data = {
        'Device': _device,
        'Version': '150718001', # HACK
        #'Version': self._version,
        'txtInputFlg': txt_input_flg,
        'txtMemberNo': korail_id,
        'txtPwd': korail_pw
    }

    r = s.get(url, params=data)
    if not response_is_success(r):
        print("http response failed")
        sys.exit()

    """ 
    [JSON Response Content]
    There’s also a builtin JSON decoder, in case you’re dealing with JSON data:

    import requests

    r = requests.get('https://api.github.com/events')
    r.json()
    [{'repository': {'open_issues': 0, 'url': 'https://github.com/... 
    """

    j = r.json()
    # print(j)

    if result_is_success(j) and j['strMbCrdNo'] == korail_id:
        return True
    else:
        return False

def logout_korail(s):

    s.get(KORAIL_LOGOUT)


def search_train(s, dep, arr, date, time, train_type, check_seat, seat_type):

    """
    search train
    """

    adult_count = 1
    child_count = 0
    senior_count = 0

    url = KORAIL_SEARCH_SCHEDULE
    data = {
        'Device': _device,
        'radJobId': '1',
        'selGoTrain': train_type,
        'txtCardPsgCnt': '0',
        'txtGdNo': '',
        'txtGoAbrdDt': date,  # '20140803',
        'txtGoEnd': arr,
        'txtGoHour': time,  # '071500',
        'txtGoStart': dep,
        'txtJobDv': '',
        'txtMenuId': '11',
        'txtPsgFlg_1': adult_count,  # 어른
        'txtPsgFlg_2': child_count,  # 어린이
        'txtPsgFlg_3': senior_count,  # 경로
        'txtPsgFlg_4': '0',  # 장애인1
        'txtPsgFlg_5': '0',  # 장애인2
        'txtSeatAttCd_2': '000',
        'txtSeatAttCd_3': '000',
        'txtSeatAttCd_4': '015', # 015: 일반석, 018: 2층석 #### not tested(as of 221006)
        'txtTrnGpCd': train_type,

        'Version': _version,
    }

    r = s.get(url, params=data)
    if not response_is_success(r):
        print("[search_train] http response failed")
        sys.exit(1)

    j = r.json()
    # print(j)

    if not j['strResult'] == 'SUCC':
        # print('search train success')
        print("[search_train] http get result failed")
        sys.exit(1)

    train_infos = j['trn_infos']['trn_info']

    ##########################################
    # search result may include train whose arrival station is not user-given arrival station
    # [ktx 열차 예] 출발역: 오송, 도착역: 서울 인 경우, 도착역이 용산인 열차가 포함됨.
    # 스마트폰 코레일 앱에서도 동일한 결과를 보이는데, 해당 열차는 회색으로 포시되며,
    # 해당 열차 예매를 진행하면, 도착역이 용산 이라는 팝업 창이 나타남.
    # 이 열차는 결과에서 제외해야 함.
    ##########################################
    train_infos = list(filter(lambda x: x['h_arv_rs_stn_nm'] == arr, train_infos))

    if check_seat:
        trains = []

        for t in train_infos:
            
            """ print(
            t['h_trn_seq'], # 일련 번호
            t['h_dpt_dt'], # 출발 날짜
            t['h_dpt_tm_qb'], # 출발 시각
            t['h_rsv_psb_flg'], # 예약 가능 여부 ('Y' or 'N')
            t['h_rsv_psb_nm'].replace("\n", ""), # 가격, 할인, 적립
            t['h_spe_rsv_cd'], # 특실 예약 가능 여부: 00 = 없음, 11 = 예약 가능, 13: 매진
            t['h_gen_rsv_cd'] # 일반실 예약 가능 여부: 00 = 없음, 11 = 예약 가능, 13: 매진
            ) """

            if seat_type == '2' and t['h_spe_rsv_cd'] == '11':
                trains.append(t)

            if seat_type == '1' and t['h_gen_rsv_cd'] == '11':
                trains.append(t)

            """ if t['h_spe_rsv_cd'] == '11' or t['h_gen_rsv_cd'] == '11':
                trains.append(t) """
    else:
        trains = train_infos

    return trains

def search_train_until_tonight(s, dep, arr, date, time, train_type, check_seat, seat_type):

    one_minute = timedelta(minutes=1)
    all_trains = []
    last_time = time
    for i in range(15):  # 최대 15번 호출

        # print(i)
        trains = search_train(s, dep, arr, date, last_time, train_type, check_seat, seat_type)
        if not trains:
            print("search no. = {}, no train result".format(i))
            break
        # print_trains(trains)
        all_trains.extend(trains)

        # 마지막 열차시간에 1분 더해서 계속 검색.
        t = datetime.strptime(all_trains[-1]['h_dpt_tm'], "%H%M%S") + one_minute
        last_time = t.strftime("%H%M%S")

    return all_trains

def search_and_reserve_train(s, dep, arr, date, time, train_type, search_tonight, seat_type, discount):

    check_seat = True

    while True:
        notfound = True
        while notfound:
            if search_tonight:
                trains = search_train_until_tonight(s, dep, arr, date, time, train_type, check_seat, seat_type)
            else:
                trains = search_train(s, dep, arr, date, time, train_type, check_seat, seat_type)
            if not trains:
                continue
            else:
                notfound = False
                break

        seat = reserve_train(s, trains[0], seat_type, discount)
        if not seat:
            continue
        else:
            break

        time.sleep(2)

    return seat

def reserve_train(s, train, seat_type, discount):

    # reserve count 
    # only 1 adult implemented, not child, not senior(as of 220930)
    cnt = 1

    """ # general class first
    if train['h_gen_rsv_cd'] == '11':
        seat_type = '1'
    else:
        seat_type = '2' """

    ######################################################
    # in case of 'ic(itx-청춘)', which have no 1st class
    ######################################################
    """ if train['h_spe_rsv_cd'] == '00':
        seat_type = '1' """

    url = KORAIL_TICKETRESERVATION
    data = {
        'Device': _device,
        'Version': _version,
        'Key': _key,
        'txtGdNo': '',
        'txtJobId': '1101',
        'txtTotPsgCnt': cnt,
        'txtSeatAttCd1': '000',
        'txtSeatAttCd2': '000',
        'txtSeatAttCd3': '000',
        'txtSeatAttCd4': '015', # 015: 일반석, 018: 2층석 #### not tested(as of 221006)
        'txtSeatAttCd5': '000',
        'hidFreeFlg': 'N',
        'txtStndFlg': 'N',
        'txtMenuId': '11',
        'txtSrcarCnt': '0',
        'txtJrnyCnt': '1',

        # 이하 여정정보1
        'txtJrnySqno1': '001',
        'txtJrnyTpCd1': '11',
        'txtDptDt1': train['h_dpt_dt'], # train.dep_date,
        'txtDptRsStnCd1': train['h_dpt_rs_stn_cd'], # train.dep_code,
        'txtDptTm1': train['h_dpt_tm'], # train.dep_time,
        'txtArvRsStnCd1': train['h_arv_rs_stn_cd'], # train.arr_code,
        'txtTrnNo1': train['h_trn_no'], # train.train_no,
        'txtRunDt1': train['h_run_dt'], # train.run_date,
        'txtTrnClsfCd1': train['h_trn_clsf_cd'], # train.train_type,
        'txtPsrmClCd1': seat_type,
        'txtTrnGpCd1': train['h_trn_gp_cd'], # train.train_group,
        'txtChgFlg1': '',

        # 이하 여정정보2
        'txtJrnySqno2': '',
        'txtJrnyTpCd2': '',
        'txtDptDt2': '',
        'txtDptRsStnCd2': '',
        'txtDptTm2': '',
        'txtArvRsStnCd2': '',
        'txtTrnNo2': '',
        'txtRunDt2': '',
        'txtTrnClsfCd2': '',
        'txtPsrmClCd2': '',
        'txtChgFlg2': '',

        # 이하 txtTotPsgCnt 만큼 반복
        'txtPsgTpCd1'    : '1',   #손님 종류 (어른 = 1, 어린이 = 3)
        'txtDiscKndCd1'  : discount, #할인 타입 (경로 = 131, 동반유아, 군장병 등..)
        # 'txtDiscKndCd1'  : '000', #할인 타입 (경로 = 131, 동반유아, 군장병 등..)
        'txtCompaCnt1'   : '1',   #인원수
        'txtCardCode_1'  : '',
        'txtCardNo_1'    : '',
        'txtCardPw_1'    : '',
    }

    r = s.get(url, params=data)
    if not response_is_success(r):
        print("[reserve_train] http response failed")
        sys.exit(1)
    j = r.json()
    # print(j)
    if not result_is_success(j):
        print("[reserve_train] http get result failed")
        sys.exit(1)

    # print(j)
    # print(j['strResult'])
    # print(j['h_pnr_no'])

    rsv_id = j['h_pnr_no']
    rsvlist = list(filter(lambda x: x['h_pnr_no'] == rsv_id, show_reservations(s)))
    if len(rsvlist) == 1:
        return rsvlist[0]

    """ 
    filter, lambda example
    >>> a = [8, 3, 2, 10, 15, 7, 1, 9, 0, 11]
    >>> list(filter(lambda x: x > 5 and x < 10, a))
    [8, 7, 9] 
    """

def show_reservations(s):

    '''
    show my reservation

    return list of dictionary(train info)
    '''

    url = KORAIL_MYRESERVATIONLIST
    data = {
        'Device': _device,
        'Version': _version,
        'Key': _key,
    }
    r = s.get(url, params=data)
    if not response_is_success(r):
        print("[show_reservations] http response failed")
        sys.exit(1)

    j = r.json()
    if not result_is_success(j):
        print("[show_reservations] http get result failed")
        sys.exit(1)

    # print(j)

    rsv_infos = j['jrny_infos']['jrny_info']

    reserves = []
    for info in rsv_infos:
        for tinfo in info['train_infos']['train_info']:
            print(
                tinfo['h_pnr_no'], # 예약 번호
                tinfo['h_run_dt'], # 운행 일짜
                tinfo['h_trn_clsf_nm'], # 열차 종류
                tinfo['h_trn_no'], # 열차 번호
                tinfo['h_dpt_rs_stn_nm'], # 출발역
                tinfo['h_dpt_tm'], # 출발 시간
                tinfo['h_arv_rs_stn_nm'], # 도착역
                tinfo['h_arv_tm'], # 도착 시간
                tinfo['h_tot_seat_cnt'], # 예약 좌석 수
                tinfo['h_rsv_amt'], # 예약 가격
                tinfo['h_ntisu_lmt_dt'], # 결제 기한 날짜
                tinfo['h_ntisu_lmt_tm'], # 결제 기한 시간     
            )

            reserves.append(tinfo)

    return reserves

def get_tickets(s):

    '''
    get my tickets
    '''

    url = KORAIL_MYTICKETLIST
    data = {
        'Device': _device,
        'Version': _version,
        'Key': _key,
        'txtIndex': '1',
        'h_page_no': '1',
        'txtDeviceId': '',
        'h_abrd_dt_from': '',
        'h_abrd_dt_to': '',
    }

    r = s.get(url, params=data)
    if not response_is_success(r):
        print("[get_tickets] http response failed")
        sys.exit(1)

    j = r.json()
    if not result_is_success(j):
        print("[get_tickets] http get result failed")
        sys.exit(1)

    ticket_infos = j['reservation_list']

    tickets = []

    for info in ticket_infos:

        ticket = info['ticket_list'][0]['train_info'][0]

        print(
        ticket['h_srcar_no'], # 객실 번호
        ticket['h_seat_cnt'], # 좌석 수
        ticket['h_seat_no'], # 좌석 번호(serial 번호)
        ticket['h_seat_no_end'], # 좌석 끝 번호(serial 번호), 좌석 수 1이면, 좌석 번호와 동일
        ticket['h_buy_ps_nm'], # 구매자 이름
        ticket['h_orgtk_sale_dt'], # 구매 일자
        ticket['h_orgtk_wct_no'], # 구매 정보 1
        ticket['h_orgtk_ret_sale_dt'], # 구매 정보 2
        ticket['h_orgtk_sale_sqno'], # 구매 정보 3
        ticket['h_orgtk_ret_pwd'], # 구매 정보 4
        ticket['h_rcvd_amt'], # 구매 가격
        ) 
        
        url = KORAIL_MYTICKET_SEAT
        data = {
            'Device': _device,
            'Version': _version,
            'Key': _key,
            'h_orgtk_wct_no': ticket['h_orgtk_wct_no'],
            'h_orgtk_ret_sale_dt': ticket['h_orgtk_ret_sale_dt'],
            'h_orgtk_sale_sqno': ticket['h_orgtk_sale_sqno'],
            'h_orgtk_ret_pwd': ticket['h_orgtk_ret_pwd'],
        }

        r = s.get(url, params=data)
        if not response_is_success(r):
            print("[get_tickets(seat)] http response failed")
            sys.exit(1)

        j = r.json()
        if not result_is_success(j):
            print("[get_tickets(seat)] http get result failed")
            sys.exit(1)

        seat = j['ticket_infos']['ticket_info'][0]['tk_seat_info'][0]
        print(seat)

        # add 'seat_no' key
        ticket['seat_no'] = seat['h_seat_no']
        ticket['seat_no_end'] = None

        tickets.append(ticket)

        """ 
        ticket = Ticket(info)

        url = KORAIL_MYTICKET_SEAT
        data = {
            'Device': _device,
            'Version': _version,
            'Key': _key,
            'h_orgtk_wct_no': ticket.sale_info1,
            'h_orgtk_ret_sale_dt': ticket.sale_info2,
            'h_orgtk_sale_sqno': ticket.sale_info3,
            'h_orgtk_ret_pwd': ticket.sale_info4,
        }
        r = self._session.get(url, params=data)
        j = json.loads(r.text)

        if self._result_check(j):
            seat = j['ticket_infos']['ticket_info'][0]['tk_seat_info'][0]
            ticket.seat_no = _get_utf8(seat, 'h_seat_no')
            ticket.seat_no_end = None

        tickets.append(ticket) 
        """

    return tickets

def cancel_reservation(s, reserve):

    '''
    cancel my reservations
    '''

    url = KORAIL_CANCEL
    data = {
        'Device': _device,
        'Version': _version,
        'Key': _key,
        'txtPnrNo': reserve['h_pnr_no'],
        # 'txtPnrNo': rsv.rsv_id,
        'txtJrnySqno': "001",
        # 'txtJrnySqno': rsv.journey_no,
        'txtJrnyCnt': "01",
        # 'txtJrnyCnt': rsv.journey_cnt,
        'hidRsvChgNo': "00000",
        # 'hidRsvChgNo': rsv.rsv_chg_no,
    }

    r = s.get(url, params=data)
    j = r.json()

    if result_is_success(j):
        print("reservation cancelled")

def show_and_cancel_reservations(s):

    my_reserves = show_reservations(s)

    print_reserves(my_reserves)

    user_input = int(input("select reservation no. to be cancelled: "))

    cancel_reservation(s, my_reserves[user_input])


def get_train_info_from_user(station_DB):

    while True:
        dpt_stn = input("\ndeparture station: ")
        if not dpt_stn:
            continue
        if not list(filter(lambda x: x['stn_nm'] == dpt_stn, station_DB)):
            print("\"{}\" not in station DB".format(dpt_stn))
        else:
            break

    while True:
        arv_stn = input("arrival station: ")
        if not arv_stn:
            continue
        if not list(filter(lambda x: x['stn_nm'] == arv_stn, station_DB)):
            print("\"{}\" not in station DB".format(arv_stn))
        else:
            break   
    
    while True:
        dpt_date = input("departure date(yyyymmdd): ")
        if not dpt_date:
            continue
        else:
            # check date string valid
            datetime.strptime(dpt_date, '%Y%m%d')
            break

    while True:
        dpt_time = input("departure time(hhmm): ")
        if not dpt_time:
            continue
        else:
            # check time string valid
            datetime.strptime(dpt_time, '%H%M') 
            # must add second string
            # without this, you have incorrect result
            dpt_time = dpt_time + '00'
            break

    while True:
        print(train_type_menu)
        train_type = input("select train type: ")
        if not train_type:
            continue
        if not train_type in list(train_type_dict.keys()):
            print("\"{}\" not in train type".format(train_type))
        else:
            train_type = train_type_dict[train_type]
            break
    
    search_tonight = input("search train until tonight? ('y' or 'n', default = 'n'): ")
    if not search_tonight or search_tonight == 'n':
        search_tonight = False
    elif search_tonight == 'y':
        search_tonight = True
    else:
        search_tonight = False

    # seat_type: '1' = 일반실, '2' = 특실
    seat_type = input("select seat type ('1' = 일반실, '2' = 특실, default = 일반실): ")
    if not seat_type:
        seat_type = '1'
    if seat_type != '1' and seat_type != '2':
        seat_type = '1'
    else:
        seat_type = seat_type

    # discount: '000' = 일반, '131' = 경로
    discount = input("select discount ('000' = 일반, '131' = 경로, default = 일반): ")
    if not discount:
        discount = '000'
    if discount != '000' and discount != '131':
        discount = '000'
    else:
        discount = discount
        

    return dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount

def print_trains(trains):

    """ 
    trains: list of train dictionary
    """
    """ 
    # print all key, value in train dict

    for seq, train in enumerate(trains):
        print("##### train [{}]".format(seq))
        for k, v in train.items():
            print("{} : {}".format(k, v)) 
    """

    """ 
    for seq, train in enumerate(trains):
        print("[{}] {}, {}, {}, {}, {}, rsv = {}, 1st rsv code = {}, 2nd rsv code = {}, {}, {}, {}, {}".\
            format(seq, train['h_trn_no'], train['h_dpt_tm_qb'], \
                train['h_arv_tm_qb'], train['h_rsv_psb_nm'].replace("\n", ""), \
                train['h_spe_rsv_psb_nm'].replace("\n", ""), train['h_rsv_psb_flg'], \
                train['h_spe_rsv_cd'], train['h_gen_rsv_cd'], \
                train['h_spe_rsv_cd2'], train['h_gen_rsv_cd2'], train['h_spe_rsv_nm'], train['h_gen_rsv_nm'])) 
    """

    """ 
    t['h_rsv_psb_flg'], # 예약 가능 여부 ('Y' or 'N')
    t['h_rsv_psb_nm'], # 일반실 가격, 할인, 적립
    t['h_spe_rsv_psb_nm'], # 특실 가격, 할인, 적립
    t['h_spe_rsv_cd'], # 특실 예약 가능 여부: 00 = 해당없음, 11 = 예약 가능, 13: 매진
    t['h_gen_rsv_cd'] # 일반실 예약 가능 여부: 00 = 해당없음, 11 = 예약 가능, 13: 매진 
    t['h_spe_rsv_cd2'], # 특실 예약 가능 추가 정보: None(매진인 경우), 19 = 매진임박, 39: 좌석많음
    t['h_gen_rsv_cd2'] # 일반실 예약 가능 추가 정보: None(매진인 경우), 19 = 매진임박, 39: 좌석많음
    t['h_spe_rsv_nm'], # 특실 예약 가능 정보: '-'(특실 없는 경우), 좌석많음, 매진임박, 매진
    t['h_gen_rsv_nm'], # 일반실 예약 가능 정보: 좌석많음, 매진임박, 매진
    """
    
    trains_df = pd.DataFrame(trains)
    # remove newline in "일반실 가격", "특실 가격" column
    trains_df = trains_df.replace('\n','', regex=True)
    selected_columns = trains_df[["h_trn_no", "h_dpt_tm_qb", "h_arv_tm_qb", \
        "h_gen_rsv_nm", "h_rsv_psb_nm", "h_spe_rsv_nm", "h_spe_rsv_psb_nm"]]
    trains_df = selected_columns.copy()
    trains_df = trains_df.rename(columns={"h_trn_no" : "열차 번호", "h_dpt_tm_qb": "출발 시간", \
        "h_arv_tm_qb" : "도착 시간", "h_rsv_psb_nm" : "일반실 가격", \
        "h_spe_rsv_psb_nm" : "특실 가격", "h_gen_rsv_nm" : "일반실 좌석 상태", \
        "h_spe_rsv_nm" : "특실 좌석 상태"})
    print(tabulate(trains_df, headers="keys"))

    """ print(trains.to_string(columns=['train_no', 'dpt_time', 'arv_time', \
        '2nd_seat_status', '2nd_class_price', '1st_seat_status', '1st_class_price'])) """

def print_reserves(reserves):

    for seq, tinfo in enumerate(reserves):

        print("[{}] {}, {}, {}, {}, {}, {}, {}, {}, {}, {}원, {}, {}".\
            format(seq, 
            tinfo['h_pnr_no'], # 예약 번호
            datetime.strptime(tinfo['h_run_dt'], '%Y%m%d').strftime('%Y/%m/%d'), # 운행 일짜
            tinfo['h_trn_clsf_nm'], # 열차 종류
            tinfo['h_trn_no'], # 열차 번호
            tinfo['h_dpt_rs_stn_nm'], # 출발역
            datetime.strptime(tinfo['h_dpt_tm'], '%H%M%S').strftime('%H:%M'), # 출발 시간
            tinfo['h_arv_rs_stn_nm'], # 도착역
            datetime.strptime(tinfo['h_arv_tm'], '%H%M%S').strftime('%H:%M'), # 도착 시간
            int(tinfo['h_tot_seat_cnt']), # 예약 좌석 수
            int(tinfo['h_rsv_amt']), # 예약 가격
            datetime.strptime(tinfo['h_ntisu_lmt_dt'], '%Y%m%d').strftime('%Y/%m/%d'), # 결제 기한 날짜
            datetime.strptime(tinfo['h_ntisu_lmt_tm'], '%H%M%S').strftime('%H:%M'), # 결제 기한 시간     
        ))

    reserves_df = pd.DataFrame(reserves)
    selected_columns = reserves_df[['h_pnr_no', 'h_run_dt', 'h_trn_clsf_nm', 'h_trn_no', \
        'h_dpt_rs_stn_nm', 'h_dpt_tm', 'h_arv_rs_stn_nm', 'h_arv_tm', 'h_tot_seat_cnt', \
        'h_rsv_amt', 'h_ntisu_lmt_dt', 'h_ntisu_lmt_tm']]
    reserves_df = selected_columns.copy()
    reserves_df = reserves_df.rename(columns={'h_pnr_no' : '예약번호', 'h_run_dt' : '운행일자', \
        'h_trn_clsf_nm' : '열차종류', 'h_trn_no' : '열차번호', 'h_dpt_rs_stn_nm' : '출발역', \
        'h_dpt_tm' : '출발시간', 'h_arv_rs_stn_nm' : '도착역', 'h_arv_tm' : '도착시간', \
        'h_tot_seat_cnt' : '좌석수', 'h_rsv_amt' : '가격', \
        'h_ntisu_lmt_dt' : '결제일자', 'h_ntisu_lmt_tm' : '결제시간'})
    reserves_df = reserves_df.astype({'좌석수': int, '가격' : int})
    # reserves_df['운행일자'] = reserves_df['운행일자'].apply(lambda x: )
    """ reserves_df['운행일자'] = pd.to_datetime(reserves_df['운행일자'])
    # reserves_df['운행일자'] = pd.to_datetime(reserves_df['운행일자'], format='%Y/%m/%d')
    reserves_df['결제일자'] = pd.to_datetime(reserves_df['결제일자'], format='%Y/%m/%d') """
    print(tabulate(reserves_df, headers="keys"))
    
    """ print(reserves.to_string(columns=['rsv_no', 'train_run_date', 'train_type', 'train_no', \
        'dpt_stn', 'dpt_time', 'arv_stn', 'arv_time', 'seat_cnt', 'rsv_price', \
        'pay_due_date', 'pay_due_time'])) """

def print_tickets(tickets):

    for seq, t in enumerate(tickets):

        print("[{}] {}, {}, {}, {}, {}, {}, {}, {}, {}, {}원, {}".\
            format(seq, 
            datetime.strptime(t['h_dpt_dt'], '%Y%m%d').strftime('%Y/%m/%d'), # 출발 일자
            t['h_dpt_rs_stn_nm'], # 출발 역
            datetime.strptime(t['h_dpt_tm'], '%H%M%S').strftime('%H:%M'), # 출발 시간
            t['h_arv_rs_stn_nm'], # 도착 역
            datetime.strptime(t['h_arv_tm'], '%H%M%S').strftime('%H:%M'), # 도착 시간
            t['h_trn_clsf_nm'], # 열차 종류
            t['h_trn_no'], # 열차 번호
            t['h_srcar_no'], # 객실 번호
            t['seat_no'], # 좌석 번호
            int(t['h_rcvd_amt']), # 구매 가격
            datetime.strptime(t['h_orgtk_sale_dt'], '%Y%m%d').strftime('%Y/%m/%d'), # 구매 일자
            # t['h_orgtk_wct_no'], # 구매 정보 1(승차권 번호 1)
            # t['h_orgtk_ret_sale_dt'], # 구매 정보 2(승차권 번호 2)
            # t['h_orgtk_sale_sqno'], # 구매 정보 3(승차권 번호 3)
            # t['h_orgtk_ret_pwd'], # 구매 정보 4(승차권 번호 4)
            # t['h_buy_ps_nm'], # 구매자 이름
            ))


    """ print(
        ticket['h_srcar_no'], # 객실 번호
        ticket['h_seat_cnt'], # 좌석 수
        ticket['h_seat_no'], # 좌석 번호(serial 형태)
        ticket['h_seat_no_end'], # 좌석 끝 번호(serial 형태), 좌석 수 1이면, 좌석 번호와 동일
        ticket['h_buy_ps_nm'], # 구매자 이름
        ticket['h_orgtk_sale_dt'], # 구매 일자
        ticket['h_orgtk_wct_no'], # 구매 정보 1(승차권 번호 1)
        ticket['h_orgtk_ret_sale_dt'], # 구매 정보 2(승차권 번호 2)
        ticket['h_orgtk_sale_sqno'], # 구매 정보 3(승차권 번호 3)
        ticket['h_orgtk_ret_pwd'], # 구매 정보 4(승차권 번호 4)
        ticket['h_rcvd_amt'], # 구매 가격
        ) 
    """     

    # print(tickets)

def get_login_info(login_info_file):

    if not exists(login_info_file):
        print("{} file not found".format(login_info_file))
        sys.exit(1)

    login_info = json.load(open(login_info_file)) 
    korail_id = login_info["korail_id"]
    korail_pw = login_info["korail_pw"]

    return korail_id, korail_pw

def get_train_info_from_file(train_info_file, station_DB):

    if not exists(train_info_file):
        print("{} file not found".format(train_info_file))
        sys.exit(1)

    train = json.load(open(train_info_file, encoding='utf-8'))

    dpt_stn = train['dep']
    if not list(filter(lambda x: x['stn_nm'] == dpt_stn, station_DB)):
        print("\"{}\" not in station DB".format(dpt_stn))
        sys.exit(1)

    arv_stn = train['arr']
    if not list(filter(lambda x: x['stn_nm'] == arv_stn, station_DB)):
        print("\"{}\" not in station DB".format(arv_stn))
        sys.exit(1)

    dpt_date = train['date']
    # check date string valid
    datetime.strptime(dpt_date, '%Y%m%d')

    dpt_time = train['time']
    # check time string valid
    datetime.strptime(dpt_time, '%H%M') 
    # must add second string
    # without this, you have incorrect result
    dpt_time = dpt_time + '00'

    train_type = train['train_type']
    if not train_type in list(train_type_dict.keys()):
        print("\"{}\" not in train type".format(train_type))
        sys.exit(1)
    train_type = train_type_dict[train_type]

    search_tonight = train['search_tonight']
    if search_tonight == 'y':
        search_tonight = True
    else:
        search_tonight = False

    seat_type = train['seat_type']
    discount = train['discount']

    return dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount

def reserve_specific_train(s, dpt_stn, arv_stn, dpt_date, dpt_time, train_type, seat_type, discount):

    """
    "dpt_time" must be same as departure time of train which you want to reserve 
    """

    # dont care seat available because we try to reserve sold-out train
    check_seat = False

    trains = search_train(s, dpt_stn, arv_stn, dpt_date, dpt_time, train_type, check_seat, seat_type)
    # this is train which you want to reserve
    specific_train = trains[0]

    # seat = reserve_train(s, trains[0])

    while True:
        j = force_reserve_train(s, specific_train, seat_type, discount)

        if j['strResult'] == 'FAIL' and j['h_msg_txt'] == '잔여석없음':
            print(".", end='')
            sleep(10)
            continue

        ############### try below #################
        # if j['strResult'] == 'SUCC' and j['h_msg_txt] == '예약완료 되었습니다.':
        ####################################
        if j['strResult'] == 'SUCC':
            print("###### got it!!")
            break 

    rsv_id = j['h_pnr_no']
    rsvlist = list(filter(lambda x: x['h_pnr_no'] == rsv_id, show_reservations(s)))
    if len(rsvlist) == 1:
        return rsvlist[0]


def force_reserve_train(s, train, seat_type, discount):

    # reserve count 
    # only 1 adult implemented, not child, not senior(as of 220930)
    cnt = 1

    url = KORAIL_TICKETRESERVATION
    data = {
        'Device': _device,
        'Version': _version,
        'Key': _key,
        'txtGdNo': '',
        'txtJobId': '1101',
        'txtTotPsgCnt': cnt,
        'txtSeatAttCd1': '000',
        'txtSeatAttCd2': '000',
        'txtSeatAttCd3': '000',
        'txtSeatAttCd4': '015', # 015: 일반석, 018: 2층석 #### not tested(as of 221006)
        'txtSeatAttCd5': '000',
        'hidFreeFlg': 'N',
        'txtStndFlg': 'N',
        'txtMenuId': '11',
        'txtSrcarCnt': '0',
        'txtJrnyCnt': '1',

        # 이하 여정정보1
        'txtJrnySqno1': '001',
        'txtJrnyTpCd1': '11',
        'txtDptDt1': train['h_dpt_dt'], # train.dep_date,
        'txtDptRsStnCd1': train['h_dpt_rs_stn_cd'], # train.dep_code,
        'txtDptTm1': train['h_dpt_tm'], # train.dep_time,
        'txtArvRsStnCd1': train['h_arv_rs_stn_cd'], # train.arr_code,
        'txtTrnNo1': train['h_trn_no'], # train.train_no,
        'txtRunDt1': train['h_run_dt'], # train.run_date,
        'txtTrnClsfCd1': train['h_trn_clsf_cd'], # train.train_type,
        'txtPsrmClCd1': seat_type,
        'txtTrnGpCd1': train['h_trn_gp_cd'], # train.train_group,
        'txtChgFlg1': '',

        # 이하 여정정보2
        'txtJrnySqno2': '',
        'txtJrnyTpCd2': '',
        'txtDptDt2': '',
        'txtDptRsStnCd2': '',
        'txtDptTm2': '',
        'txtArvRsStnCd2': '',
        'txtTrnNo2': '',
        'txtRunDt2': '',
        'txtTrnClsfCd2': '',
        'txtPsrmClCd2': '',
        'txtChgFlg2': '',

        # 이하 txtTotPsgCnt 만큼 반복
        'txtPsgTpCd1'    : '1',   # 손님 종류 (어른 = 1, 어린이 = 3)
        'txtDiscKndCd1'  : discount, # 할인 타입 (경로 = 131, 동반유아, 군장병 등..)
        'txtCompaCnt1'   : '1',   # 인원수
        'txtCardCode_1'  : '',
        'txtCardNo_1'    : '',
        'txtCardPw_1'    : '',
    }

    r = s.get(url, params=data)
    if not response_is_success(r):
        print("[reserve_train] http response failed")
        sys.exit(1)
    j = r.json()
    # print(j)

    return j

    """ 
    rsv_id = j['h_pnr_no']
    rsvlist = list(filter(lambda x: x['h_pnr_no'] == rsv_id, show_reservations(s)))
    if len(rsvlist) == 1:
        return rsvlist[0] 
    """

def get_train_info(train_info_file):

    while True:
        method = input("select how get train info('f' = from file or 'u' = user input): ")
        if method == 'f':
            dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount = \
                        get_train_info_from_file(train_info_file, station_DB)
            break
        elif method == 'u':
            dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount = \
                        get_train_info_from_user(station_DB)
            break
        else:
            continue

    return dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount

top_menu_dict = {
    '1' : search_train,
    '2' : search_and_reserve_train,
    '3' : show_reservations,
    '4' : show_and_cancel_reservations,
    '5' : get_tickets,
    '6' : reserve_specific_train,
    'x' : sys.exit
}

"""
[train_info_file example, "train_info.txt"]

{"dep" : "평내호평", "arr" : "청량리", "date" : "20221004", "time" : "0851", "train_type" : "ic", 
"search_tonight" : "n", "seat_type" : "1", "discount" : "000"}

"dep" = departure station
"arr" = arrival station
"date" = departure date
"time" = departure time
"train_type" = 
    'k' = "KTX, KTX-산천"
    's' = "새마을호"
    'm' = "무궁화호"
    't' = "통근열차"
    'n' = "누리로"
    'a' = "전체"
    'p' = "공항직통"
    'ic' = "ITX-청춘"
    'is' = "ITX-새마을"
"search_tonight" = search train until tonight, 'y' or 'n'
"seat_type" = 
    '1' = 일반실, '2' = 특실
"discount" = 
    '000' = 일반, '131' = 경로

"""

if __name__ == "__main__":

    if not len(sys.argv) == 2:
        print("need \"train info file\"")
        sys.exit(1)

    train_info_file = sys.argv[1]
    print("train info file: \"{}\"".format(train_info_file))
        
    korail_id, korail_pw = get_login_info(login_info_file)

    station_DB = get_station_DB()
    if not station_DB:
        print("station DB not ready")
        sys.exit(1)

    s = init_session()

    if not login_korail(s, korail_id, korail_pw):
        print("login failed")
        sys.exit(1)

    while True:

        print(top_menu)
        menu = input("select menu: ")
        if not menu:
            continue
        if menu in list(top_menu_dict.keys()):

            if menu == '1':

                dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount = \
                    get_train_info(train_info_file)

                check_seat = False

                if search_tonight:
                    trains = \
                        search_train_until_tonight(s, dpt_stn, arv_stn, dpt_date, dpt_time, \
                            train_type, check_seat, seat_type)
                else:
                    trains = \
                        search_train(s, dpt_stn, arv_stn, dpt_date, dpt_time, \
                            train_type, check_seat, seat_type)

                print_trains(trains)

            if menu == '2':
                
                dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount = \
                    get_train_info(train_info_file)

                search_and_reserve_train(s, dpt_stn, arv_stn, dpt_date, dpt_time, train_type, \
                    search_tonight, seat_type, discount)

            if menu == '3':

                my_reserves = show_reservations(s)
                print_reserves(my_reserves)

            if menu == '4':

                show_and_cancel_reservations(s)

            if menu == '5':

                my_tickets = get_tickets(s)
                print_tickets(my_tickets)

            if menu == '6':

                dpt_stn, arv_stn, dpt_date, dpt_time, train_type, search_tonight, seat_type, discount = \
                    get_train_info(train_info_file)

                reserve_specific_train(s, dpt_stn, arv_stn, dpt_date, dpt_time, \
                    train_type, seat_type, discount)

            if menu == 'x':
                # do not use: i suspect logout may remove reservation
                # logout_korail(s)
                print("end program")
                sys.exit(0)

        else:
            print("### error: {} not in menu".format(menu))
        

    sys.exit(0)


    # trains = search_train_until_tonight(s, dep_station, arr_station, date, time, train_type)

    # trains = search_train(s, dep_station, arr_station, date, time, train_type)

    # reserve_train(s, trains[0])

    # my_reserves = show_reservations(s)

    # cancel_reservation(s, my_reserves[0])

    # my_tickets = show_tickets(s)
    # print(my_tickets)


""" 
class Train(Schedule):
    # : 지연 시간 (hhmm)
    delay_time = None  # h_expct_dlay_hr

    # : 예약 가능 여부
    reserve_possible = False  # h_rsv_psb_flg ('Y' or 'N')

    #: 예약 가능 여부
    reserve_possible_name = None  # h_rsv_psb_nm

    #: 특실 예약가능 여부
    #: 00: 특실 없음
    #: 11: 예약 가능
    #: 13: 매진
    special_seat = None  # h_spe_rsv_cd

    #: 일반실 예약가능 여부
    #: 00: 일반실 없음
    #: 11: 예약 가능
    #: 13: 매진
    general_seat = None  # h_gen_rsv_cd

    def __init__(self, data):
        super(Train, self).__init__(data)
        self.reserve_possible = _get_utf8(data, 'h_rsv_psb_flg')
        self.reserve_possible_name = _get_utf8(data, 'h_rsv_psb_nm')

        self.special_seat = _get_utf8(data, 'h_spe_rsv_cd')
        self.general_seat = _get_utf8(data, 'h_gen_rsv_cd')

    def __repr__(self):
        repr_str = super(Train, self).__repr__()

        if self.reserve_possible_name is not None:
            seats = []
            if self.has_special_seat():
                seats.append("특실")

            if self.has_general_seat():
                seats.append("일반실")

            repr_str += " " + (",".join(seats)) + " " + self.reserve_possible_name.replace('\n', ' ')

        return repr_str

    def has_special_seat(self):
        return self.special_seat == '11'

    def has_general_seat(self):
        return self.general_seat == '11'

    def has_seat(self):
        return self.has_general_seat() or self.has_special_seat() 
"""

