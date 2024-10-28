from bs4 import BeautifulSoup
import pandas as pd
try:
    import plotille
    _PLOTILLE = True
except ImportError:
    print("WARNING: ASCII plotting library 'plotille' not found.")
    _PLOTILLE = False
import requests


def fetch_weather(url):
    table_html = _fetch_weather_table(url)
    table = _parse_weather_table(table_html)

    return table


def _fetch_weather_table(url):
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the specific table by unique identifier
    table = soup.find("table", {"style": "border-collapse: collapse;"})
    
    # Return the HTML for this table as a string
    return str(table)


def _parse_weather_table(html):
    # Parse HTML content
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("table", {"style": "border-collapse: collapse;"})

    data = []
    current_date = None
    rows = table.find_all("tr")[2:]  # Skips header rows

    for row in rows:
        cols = row.find_all("td")
        
        # Update current_date if the cell has a rowspan (first row of the day)
        if len(cols[0].attrs) and 'rowspan' in cols[0].attrs:
            current_date = cols[0].text.strip()
            row_data = [current_date] + [col.text.strip() for col in cols[1:]]
        else:
            row_data = [current_date] + [col.text.strip() for col in cols]
        
        # Ensure we have exactly 10 elements in row_data
        if len(row_data) > 10:
            row_data = row_data[:10]
        elif len(row_data) < 10:
            row_data += [""] * (10 - len(row_data))

        # Handle image-based cells for wind direction (col index 4)
        if len(cols) > 4 and cols[4].img:
            row_data[4] = cols[4].img['alt']
        
        data.append(row_data)

    # Define column names and create DataFrame
    df = pd.DataFrame(data, columns=["Date", "Time", "Temperature", "Feels Like", "Wind Direction",
                                     "Wind Speed", "Wind Gust", "Precipitation", "Humidity", "Pressure"])
    return df


def _plot_weather_data(df):
    """
    Plots columns of a DataFrame representing Time, Temperature, Wind speed, and Precipitation
    as individual subplots in ASCII using the Plotille package.

    Parameters
    ----------
    matrix : np.ndarray
        A 2D array where each column represents Time, Temperature, Wind speed, and Precipitation.
    """
    hours = df["Time"].apply(lambda x: int(x.split(":")[0]))
        # Detect day changes by finding where the hour value goes backwards
    day_offsets = (hours.diff() < 0).cumsum()  # Increment day count when hour goes back
    unrolled_hours = hours + day_offsets * 24  # Accumulate hours, adding 24h for each new day

    x_min, x_max = int(unrolled_hours.min()), int(unrolled_hours.max())
    x_max = x_min + 48

    temperature = df["Temperature"].str.replace(" °C", "").astype(int)
    wind_speed = df["Wind Speed"].astype(int)
    precipitation = df["Precipitation"].replace("--", "0.0").str.replace(" mm", "").astype(float)    # Set up titles and labels for each subplot

    # Plot Temperature
    print(plotille.plot(
        unrolled_hours, temperature,
        width=60,
        height=10,
        X_label="Time (h)",
        Y_label="Temp (°C)",
        x_min=x_min,
        x_max=x_max,
        lc='red'
    ))

    # Plot Wind Speed
    print('\n')
    print(plotille.plot(
        unrolled_hours, wind_speed,
        width=60,
        height=10,
        X_label="Time (h)",
        Y_label="Wind Speed (km/h)",
        x_min=x_min,
        x_max=x_max,
        y_min=0,
        lc='magenta'
    ))

    # Plot Precipitation as a bar-like plot
    print('\n')
    print(plotille.plot(
        unrolled_hours, precipitation,
        width=60,
        height=10,
        X_label="Time (h)",
        Y_label="Precipitation (mm)",
        x_min=x_min,
        x_max=x_max,
        y_min=0,
        marker='▮',  # Emulates bar-like appearance
        lc='blue'
    ))


if __name__ == '__main__':
    import sys

    try:
        *args, url = sys.argv[1:]
    except ValueError:
        raise ValueError("not enough arguments provided; at least the URL of MeteoCiel is needed.")

    if len(args) > 2:
        raise ValueError("too many arguments provided; the script only accepts '-p' as extra argument")
    if len(args) == 1:
        if args[0] != '-p':
            raise ValueError("argument not recognized; only '-p' is available")
        elif not _PLOTILLE:
            raise ImportError("The 'plotille' library is required for plotting. "
                              "Install it with 'pip install plotille' or run the "
                              "script without the '-p' flag.")
        plot = True
    else:
        plot = False

    data = fetch_weather(url)
    
    if plot:
        _plot_weather_data(data[['Time', 'Temperature', 'Wind Speed', 'Precipitation']])
    
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(data[['Date', 'Time', 'Temperature', 'Wind Speed', 'Wind Gust', 'Precipitation', 'Humidity']])
