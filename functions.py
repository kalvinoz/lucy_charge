# Functions which change something

def set_soc_limit(new_limit):
    refresh_data_if_online()
    current_limit = my_car.get_vehicle_data()['charge_state']['charge_limit_soc']
    if current_limit != new_limit:
        my_car.command('CHANGE_CHARGE_LIMIT', percent=new_limit)


def set_charge_amps(charging_amps):
    refresh_data_if_online()
    new_charging_amps = int(min(charging_amps, max_charging_amps))
    if car_data['charge_state']['charge_amps'] != new_charging_amps:
        my_car.command('CHARGING_AMPS', charging_amps=new_charging_amps)
        # need to send command twice when below 5A
        if new_charging_amps < 5:
            my_car.command('CHARGING_AMPS', charging_amps=new_charging_amps)


def start_charge_safe():
    refresh_data_if_online()
    no_action_status = ['Charging', 'Complete']
    if car_data['charge_state']['charging_state'] not in no_action_status:
        my_car.command('START_CHARGE')


def stop_charge_safe():
    refresh_data_if_online()

    if car_data['charge_state']['charging_state'] == 'Charging':
        my_car.command('STOP_CHARGE')

# Functions which just get data

def refresh_data_if_online():
    car_is_awake = (my_car.get_vehicle_summary()['state'] == 'online')
    if car_is_awake:
        car_data = my_car.get_vehicle_data()
    return car_is_awake


def parked_at_home():
    drive_state = car_data['drive_state']
    movement_keys = ['shift_state', 'speed']
    car_movement = [drive_state.get(key) for key in movement_keys]
    car_stopped = (car_movement == [None, None])
    location_keys = ['latitude', 'longitude']
    car_coords = [drive_state.get(key) for key in ('latitude', 'longitude')]
    home_dist = geodistance.distance(HOME_COORDINATES, car_coords).m
    car_at_home = (home_dist < 25)
    return car_stopped & car_at_home


def car_A():
    if car_data['charge_state']['charging_state'] == 'Charging':
        return car_data['charge_state']['charge_amps']
    else:
        return 0


def max_available_A():
    refresh_data_if_online()

    WW_instant = WW_base_url + '/latest?convert[energy]=kW'

    data_raw = requests.get(WW_instant, headers=headers).content
    power_data = literal_eval(data_raw.decode('utf-8'))

    total_used_kW = sum(power_data['pRealKw'][:4])
    solar_kW = power_data['pRealKw'][3]
    car_V = sum(power_data['vRMS'][:3])
    car_kW = car_V * car_A() / 1000
    house_hold_kW = total_used_kW - car_kW
    available_for_car_kW = max(solar_kW - house_hold_kW, 0)
    available_for_car_A = 1000 * available_for_car_kW / car_V

    return int(available_for_car_A)


def is_daytime(buffer_hours=1.5):
    sun = Sun(HOME_COORDINATES[0], HOME_COORDINATES[1])

    local_tz = pytz.timezone(LOCAL_TIMEZONE)

    sun_rise = sun.get_sunrise_time(datetime.now()).astimezone(local_tz).time()
    sun_set = sun.get_sunset_time(datetime.now()).astimezone(local_tz).time()

    sun_rise_dt = datetime.combine(datetime.now(local_tz), sun_rise)
    sun_set_dt = datetime.combine(datetime.now(local_tz), sun_set)

    now_dt = datetime.combine(datetime.now(local_tz), datetime.now(local_tz).time())

    hours_after_sunrise = (now_dt - sun_rise_dt).total_seconds() / 3600
    hours_before_sunset = (sun_set_dt - now_dt).total_seconds() / 3600

    after_sunrise = (hours_after_sunrise > buffer_hours)
    before_sunset = (hours_before_sunset > buffer_hours)

    hours_until_sunrise = 24 - hours_after_sunrise + buffer_hours

    return {'check': after_sunrise & before_sunset, \
            'wait_time': hours_until_sunrise}