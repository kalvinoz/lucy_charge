fully_charged = False

my_car.sync_wake_up()

if car_data['charge_state']['charging_state'] == 'Complete':
    fully_charged = True

new_current_value = 0

while True:

    sunny = is_daytime()

    if not sunny['check']:
        if sunny['wait_time'] > 2:
            print('Too long until sunrise')
            break

        else:
            print(sunny['wait_time'])
            sleep(sunny['wait_time'] * 3600)

    # sleep(60)

    car_is_awake = refresh_data_if_online()

    if not parked_at_home():
        print('Not home')
        break

    if fully_charged:
        my_car.command('FLASH_LIGHTS')
        print('Fully charged')
        break

    if car_data['charge_state']['charging_state'] == 'Complete':
        fully_charged = True
        my_car.command('FLASH_LIGHTS')
        break

    previous_current_value = car_A()
    new_current_value = max_available_A()

    print(new_current_value)

    if previous_current_value == new_current_value:
        sleep(15)
        continue

    print(new_current_value)

    if new_current_value > 0:
        if not car_is_awake: my_car.sync_wake_up()
        start_charge_safe()
        set_charge_amps(new_current_value)
        sleep(60)
        continue

    if new_current_value == 0 & car_is_awake:
        stop_charge_safe()
        continue