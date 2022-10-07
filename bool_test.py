
""" while True:
    search_tonight = input("search train until tonight? (y or n, default = y): ")
    if not search_tonight or search_tonight == 'n':
        search_tonight = False
    elif search_tonight == 'y':
        search_tonight = True
    else:
        search_tonight = False

    print(search_tonight) """

""" while True:
    # seat_type: '1' = 일반실, '2' = 특실
    seat_type = input("select seat type (1 = 일반실 or 2 = 특실, default = 일반실): ")
    if not seat_type:
        seat_type = '1'
    if seat_type == '1':
        seat_type = '1'
    elif seat_type == '2': 
        seat_type = '2'
    else:
        seat_type = '1'

    print(seat_type) """

""" while True:
    # seat_type: '1' = 일반실, '2' = 특실
    seat_type = input("select seat type (1 = 일반실 or 2 = 특실, default = 일반실): ")
    if not seat_type:
        seat_type = '1'
    if seat_type != '1' and seat_type != '2':
        seat_type = '1'
    else:
        seat_type = seat_type

    print(seat_type) """

while True:
    discount = input("select discount ('000' = 일반, '131' = 경로, default = 일반): ")
    if not discount:
        discount = '000'
    if discount != '000' and discount != '131':
        discount = '000'
    else:
        discount = discount

    print(discount)