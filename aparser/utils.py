import operator
import datetime
import json

from django.core import serializers
from django.conf import settings

from .taximaster.api import get_order_state, change_order_state, send_sms, get_current_orders, get_addresses_like_street, get_addresses_like_house, analyze_route2, calc_order_cost2, create_order2, get_addresses_like_points, create_order_api

HOST = 'https://fishka.dyndns.org'
PORT = 8089
API_KEY = '4aaoI4Pp8m98XBjT55BYL57lj09XF9fa1b5E0SaA'

DEFAULT_CITY = 'Екатеринбург'

def leve_dist(a, b):
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n+1)
    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*n
        for j in range(1,n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]

def tokenize_address(address):
    street = ''
    house = ''
    city = ''
    i = 0
    try:
        while not address[i].isalpha():
            i += 1
        #while address[i].isalpha():
        #    street += address[i]
        #    i += 1
        while not address[i].isdigit():
            street += address[i]
            i += 1
        while address[i].isdigit():
            house += address[i]
            i += 1
        if (address[i] in ' /\\') or address[i].isalpha():
            house += address[i]
            i += 1
        while address[i].isdigit():
            house += address[i]
            i += 1
        city = address[i:]
    except IndexError:
        return normalize_street(street), house, city
    return normalize_street(street), house, city

def normalize_street(street):
    oldstreet = street
    street = ''
    for i in oldstreet:
        if i.isalpha() or i.isspace() or i.isdigit():
            street += i
        else:
            street += ' '
    while street.find('  ') != -1:
        street = street.replace('  ', ' ')
    return str.rstrip(street)

def get_top_streets(streets, street):
    dists = {}
    for t_street in streets:
        ct_street = t_street['street'].split(' /')[0]
        dists[t_street['street']] = leve_dist(ct_street.lower(), street.lower())
    return [x[0] for x in sorted(dists.items(), key=operator.itemgetter(1))[:5]]

def get_top_points(points, point):
    dists = {}
    for t_point in points:
        dists[t_point] = leve_dist(t_point.lower(), point.lower())
        if t_point.find('[') == -1:
            dists[t_point] *= 1000
    return [x[0] for x in sorted(dists.items(), key=operator.itemgetter(1))[:5]]

def get_top_houses(addresses, house):
    dists = {}
    for t_address in addresses:
        t_house = t_address['house']
        dists[t_house] = leve_dist(t_house.lower(), house.lower())
        if t_house[-1].isdigit():
            if t_house.find('/') == -1 and t_house.find('к.') == -1 and t_house.find('ко') == -1 and t_house.find('ст') == -1:
                dists[t_house] = dists[t_house] * 10000000 + int(t_house[-1])
            else:
                dists[t_house] = dists[t_house] * 10000
        else:
            dists[t_house] = dists[t_house] * 10 + ord(t_house[-1].lower())
        if t_house.lower() == house.lower():
            dists[t_house] = 0
    return [x[0] for x in sorted(dists.items(), key=operator.itemgetter(1))[:5]]

def filter_points(answer):
    correct_addresses = []
    for address in answer['data']['addresses']:
        if address['coords']['lon'] != 0 and address['street'].find('аэроп. К') == -1:
            correct_addresses.append(address)
    answer['data']['addresses'] = correct_addresses
    return answer

def get_streets_starts_with(answer, street):
    ret = []
    for address in answer['data']['addresses']:
        for st in address['street'].split(' /')[0].split(' '):
            if str.rstrip(st).lower().startswith(str.rstrip(street).lower()):
                ret.append(str.rstrip(address['street'].split(' /')[0]))
    return ret

def extract_streets(answer, street):
    ret = []
    for address in answer['data']['addresses']:
        ret.append(str.rstrip(address['street']))
    return ret

def extract_points(answer, street):
    ret = []
    sret = []
    for address in answer['data']['addresses']:
        estreet = str.rstrip(address['street'])
        if address.get('comment', ''):
            estreet += ' *' + address.get('comment', '')
            ret.append(estreet)
        else:
            sret.append(estreet)
    return ret + sret

def get_streets(street, selected_city):
    parts = street.split(' ')
    ret = set()
    for part in parts:
        if len(part) < 1:
            continue
        answer = get_addresses_like_street(HOST, PORT, API_KEY, part, city=selected_city)
        if answer['code'] != 0:
            return []
        if len(ret) == 0:
            ret = set(extract_streets(answer, part))
        else:
            ret = ret.intersection(set(extract_streets(answer, part)))
        if len(ret) == 0:
            return []
    return list(ret)

def get_points(street, selected_city):
    parts = street.split(' ')
    ret = set()
    for part in parts:
        if len(part) < 2:
            continue
        answer = get_addresses_like_points(HOST, PORT, API_KEY, part, city=selected_city)
        if answer['code'] != 0:
            return []
        else:
            answer = filter_points(answer)
        if len(ret) == 0:
            ret = set(extract_points(answer, part))
        else:
            ret = ret.intersection(set(extract_points(answer, part)))
        if len(ret) == 0:
            return []
    return list(ret)

def top_addresses(address, selected_city):
    address = address.lower()
    street, house, city = tokenize_address(address)
    house = house.replace(' ', '')
    street = str.strip(street)
    if house == '' or house == '1905':
        #streets = get_streets(street, selected_city)[:5]
        points = get_top_points(get_points(street, selected_city), street)
        return [x for x in points]
    top_streets = get_streets(street, selected_city)[:5]
    if len(top_streets) == 0:
        points = get_top_points(get_points(street, selected_city), street)
        return [x for x in points]
    top = []
    cur_street_index = -1
    for cur_street in top_streets:
        cur_street_index += 1
        answer = get_addresses_like_house(HOST, PORT, API_KEY, cur_street, house, city=selected_city)
        if answer['code'] != 0:
            answer = get_addresses_like_house(HOST, PORT, API_KEY, cur_street, house.upper(), city=selected_city)
        if answer['code'] != 0:
            continue
        else:
            top_houses = get_top_houses(answer['data']['addresses'], house)
            top_exstension = [cur_street + ', ' + x for x in top_houses]
            if top_houses[0].lower() == str.strip(house).lower():
                try:
                    tmp = top[cur_street_index]
                    top[cur_street_index] = top_exstension[0]
                    top_exstension[0] = tmp
                except:
                    pass
            top.extend(top_exstension)
    return top[:5]

def get_info(address, selected_city):
    street, house, city = tokenize_address(address)
    if len(address.split(', ')) > 1:
        house = address.split(', ')[-1]
        street = ', '.join(address.split(', ')[:-1])
        answer = get_addresses_like_house(HOST, PORT, API_KEY, street, house, city=selected_city)
        if answer['code'] != 0:
            return None
    else:
        answer = get_addresses_like_points(HOST, PORT, API_KEY, address, city=selected_city)
        if answer['code'] != 0:
            return None
    ret = {}
    ret['address'] = address
    good_index = 0
    for i in range(len(answer['data']['addresses'])):
        if answer['data']['addresses'][i]['house'].replace(' ', '').lower() == house:
            good_index = i
    ret['lon'] = answer['data']['addresses'][good_index]['coords']['lon']
    ret['lat'] = answer['data']['addresses'][good_index]['coords']['lat']
    return ret

def address_correct(address, selected_city):
    if len(address.split(', ')) > 1:
        house = address.split(', ')[-1]
        street = ', '.join(address.split(', ')[:-1])
        answer = get_addresses_like_house(HOST, PORT, API_KEY, street, house, city=selected_city)
        if answer['code'] != 0:
            return False
        return True
    else:
        answer = get_addresses_like_points(HOST, PORT, API_KEY, address, city=selected_city)
        if answer['code'] != 0:
            return False
        if answer['data']['addresses'][0]['coords']['lon'] == 0:
            return False
        return True

def route_analysis(from_address, to_address, selected_city):
    city = get_city_util(selected_city)
    from_info = get_info(from_address, selected_city)
    to_info = get_info(to_address, selected_city)
    if not all([from_info, to_info]):
        return 0, []
    answer = analyze_route2(HOST, PORT, API_KEY, [from_info, to_info])
    if answer['code'] != 0:
        return 0, []
    route = answer['data']['full_route_coords']
    params = {}
    params['tariff_id'] = city.tarif
    params['source_zone_id'] = answer['data']['addresses'][0]['zone_id']
    params['dest_zone_id'] = answer['data']['addresses'][1]['zone_id']
    params['distance_city'] = answer['data']['city_dist']
    params['distance_country'] = answer['data']['country_dist']
    if answer['data']['country_dist'] > 0:
        params['is_country'] = True
    params['source_distance_country'] = answer['data']['source_country_dist']
    answer = calc_order_cost2(HOST,PORT, API_KEY, params)
    if answer['code'] != 0:
        return 0, []
    return answer['data']['sum'], route

def get_coords(address, selected_city):
    if address == '':
        return [{'lat':0,'lon':0}]
    street, house, city = tokenize_address(address)
    if len(address.split(', ')) > 1:
        house = address.split(', ')[-1]
        street = ', '.join(address.split(', ')[:-1])
        answer = get_addresses_like_house(HOST, PORT, API_KEY, street, house, city=selected_city)
        if answer['code'] != 0:
            return [{'lat':0,'lon':0}]
    else:
        answer = get_addresses_like_points(HOST, PORT, API_KEY, address, city=selected_city)
        if answer['code'] != 0:
            return [{'lat':0,'lon':0}]
    good_index = 0
    for i in range(len(answer['data']['addresses'])):
        if answer['data']['addresses'][i]['house'].replace(' ', '').lower() == house:
            good_index = i
    return [{'lon': answer['data']['addresses'][good_index]['coords']['lon'],
             'lat': answer['data']['addresses'][good_index]['coords']['lat']}]
