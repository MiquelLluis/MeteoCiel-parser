from meteociel import fetch_weather


def paris_arome():
    url = 'https://www.meteociel.fr/previsions-arome-1h/27817/paris.htm'
    weather = fetch_weather(url)
    print(weather[['Date', 'Time', 'Temperature', 'Wind Speed', 'Wind Gust', 'Precipitation', 'Humidity']])

def paris_wrf():
    url = 'https://www.meteociel.fr/previsions-wrf-1h/27817/paris.htm'
    weather = fetch_weather(url)
    print(weather[['Date', 'Time', 'Temperature', 'Wind Speed', 'Wind Gust', 'Precipitation', 'Humidity']])


if __name__ == '__main__':
    paris_arome()
    # paris_wrf()