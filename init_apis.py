# Wattwatchers API

api_key =  WATTWATCHERS_KEY # insert your actual key here
headers = {
  'Authorization': 'Bearer %s' % api_key
}
device_id = WATTWATCHERS_DEVICE_ID
WW_base_url = 'https://api-v3.wattwatchers.com.au/short-energy/' + device_id

# Tesla API
tesla = teslapy.Tesla(TESLA_EMAIL)
if not tesla.authorized:
    print('Use browser to login. Page Not Found will be shown at success.')
    print('Open this URL: ' + tesla.authorization_url())
    tesla.fetch_token(authorization_response=input('Enter URL after authentication: '))

vehicles = tesla.vehicle_list()

my_car = vehicles[0]