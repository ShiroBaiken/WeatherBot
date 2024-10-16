import httpx
from aiogram import Bot


class Weather(Bot):

    def __init__(self, bot_key, weather_api_key, *args, **kwargs):
        self.api_link = 'https://www.meteosource.com/api/v1/free'
        self.weather_api_key = weather_api_key
        super(Weather, self).__init__(token=bot_key)

    def get_locations(self, params):
        edited_params = {x: y for x, y in params.items() if x != 'place_id' and x != 'units'}
        edited_params.update({'text': params['place_id']})
        locations = httpx.get(url=self.api_link + '/find_places', params=edited_params)
        if locations.status_code == 200:
            return locations.json()
        else:
            return locations.text

    def get_weather_for_city(self, location):
        params = {
            'key': self.weather_api_key,
            'place_id': location,
            'units': 'metric',

        }
        response = httpx.get(url=self.api_link + '/point', params=params)
        if response.status_code == 200:
            return response.json(), 'weather'
        else:
            return self.get_locations(params), 'locations'

