from .core import request

def ping(address, port, api_key):
    return request(address, port, api_key, address, port, api_key, 'ping', {})
    
def get_crew_groups_list(address, port, api_key):
    return request(address, port, api_key, 'get_crew_groups_list', {})
    
def get_crew_info(address, port, api_key, crew_id):
    return request(address, port, api_key, 'get_crew_info', {'crew_id': crew_id})

def get_crews_info(address, port, api_key):
    return request(address, port, api_key, 'get_crews_info', {})
    
def get_drivers_info(address, port, api_key):
    return request(address, port, api_key, 'get_drivers_info', {'locked_drivers': 'true',
    'dismissed_drivers': 'true'})

def get_driver_info(address, port, api_key, driver_id):
    return request(address, port, api_key, 'get_driver_info', {'driver_id': driver_id})

def get_car_info(address, port, api_key, car_id):
    return request(address, port, api_key, 'get_car_info', {'car_id': car_id})
    
def get_cars_info(address, port, api_key):
    return request(address, port, api_key, 'get_cars_info', {'locked_cars': 'true'})
    
def create_car(address, port, api_key, code, mark, color, gos_number):
    return request(address, port, api_key, 'create_car', {'code': code, 'mark': mark, 
    'color': color, 'gos_number': gos_number}, post=True, json=True)
    
def update_car_info(address, port, api_key, car_id, others):
    params = {'car_id': str(car_id)}
    params.update(others)
    return request(address, port, api_key, 'update_car_info', params, post=True, json=True)
    
def create_driver(address, port, api_key, name, car_id, password):
    return request(address, port, api_key, 'create_driver', {'car_id': car_id, 'name': name,
    'password': password}, post=True, json=True)
    
def update_driver_info(address, port, api_key, driver_id, others):
    params = {'driver_id': driver_id}
    params.update(others)
    return request(address, port, api_key, 'update_driver_info', params, post=True, json=True)
    
def create_crew(address, port, api_key, driver_id, car_id, crew_group_id):
    return request(address, port, api_key, 'create_crew', {'crew_group_id': crew_group_id,
    'driver_id': driver_id, 'car_id': car_id}, post=True, json=True)
    
def update_crew_info(address, port, api_key, crew_id, others):
    params = {'crew_id': crew_id}
    params.update(others)
    return request(address, port, api_key, 'update_crew_info', params, post=True, json=True)

def get_addresses_like_street(address, port, api_key, street, city=None):
    #if len(street) < 3:
    #    return {'code': 999}
    params = {'street': street, 'get_streets': 'true', 'get_points': 'false', 
    'get_houses': 'false'}#, 'search_in_tm': 'false', 'search_in_yandex': 'true'}
    if city:
        params['city'] = city
    return request(address, port, api_key, 'get_addresses_like', params, post=False, json=False)

def get_addresses_like_house(address, port, api_key, street, house, city=None):
    #if len(street) < 3:
    #    return {'code': 999}
    params = {'street': street, 'get_streets': 'false', 'get_points': 'false', 
    'get_houses': 'true', 'house': house}#, 'search_in_tm': 'false', 'search_in_yandex': 'true'}
    if city:
        params['city'] = city
    return request(address, port, api_key, 'get_addresses_like', params, post=False, json=False)

def get_addresses_like_points(address, port, api_key, street, city=None):
    #if len(street) < 3:
    #    return {'code': 999}
    params = {'street': street, 'get_streets': 'false', 'get_points': 'true', 
    'get_houses': 'false'}
    if city:
        params['city'] = city
    return request(address, port, api_key, 'get_addresses_like', params, post=False, json=False)

def analyze_route2(address, port, api_key, addresses):
    params = {'get_full_route_coords': True, 'addresses': addresses}
    return request(address, port, api_key, 'analyze_route2', params, post=True, json=True)

def calc_order_cost2(address, port, api_key, params):
    return request(address, port, api_key, 'calc_order_cost2', params, post=True, json=True)

def create_order_api(address, port, api_key, params):
    return request(address, port, api_key, 'create_order', params, post=True, json=False)

def create_order2(address, port, api_key, params):
    return request(address, port, api_key, 'create_order2', params, post=True, json=True)

def get_current_orders(address, port, api_key, phone):
    params = {'phone': phone}
    return request(address, port, api_key, 'get_current_orders', params, post=False, json=False)

def send_sms(address, port, api_key, phone, message):
    params = {'phone': phone, 'message': message}
    return request(address, port, api_key, 'send_sms', params, post=True, json=False)

def change_order_state(address, port, api_key, order_id, order_state):
    params = {'order_id': order_id, 'new_state': order_state}
    return request(address, port, api_key, 'change_order_state', params, post=True, json=False)

def get_order_state(address, port, api_key, order_id):
    params = {'order_id': order_id}
    return request(address, port, api_key, 'get_order_state', params, post=False, json=False)
