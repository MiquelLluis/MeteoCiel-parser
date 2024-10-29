from datetime import datetime

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


def _initialise_figure(width=60, height=10, xmin=None, xmax=None, ymin=None, ymax=None,
                       xlabel=None, ylabel=None, color_mode='names'):
    """
    Initialises a Plotille Figure object with default settings for plotting weather data.

    Parameters
    ----------
    width : int, optional
        The width of the plot in characters.
    height : int, optional
        The height of the plot in characters.
    xmin : int, optional
        The minimum value for the x-axis.
    xmax : int, optional
        The maximum value for the x-axis.
    ymin : int, optional
        The minimum value for the y-axis.
    ymax : int, optional
        The maximum value for the y-axis.
    xlabel : str, optional
        The label for the x-axis.
    ylabel : str, optional
        The label for the y-axis.
    color_mode : str, optional
        The used color mode. See `plotille.color()`.

    Returns
    -------
    plotille.Figure
        A Plotille Figure object with the specified settings.
    """
    fig = plotille.Figure()
    fig.color_mode = color_mode
    fig.width = width
    fig.height = height

    # maybe this can be done more elegantly
    if xmin is not None and xmax is not None:
        fig.set_x_limits(min_=xmin, max_=xmax)
    elif xmin is not None:
        fig.set_x_limits(min_=xmin)
    elif xmax is not None:
        fig.set_x_limits(max_=xmax)
    if ymin is not None and ymax is not None:
        fig.set_y_limits(min_=ymin, max_=ymax)
    elif ymin is not None:
        fig.set_y_limits(min_=ymin)
    elif ymax is not None:
        fig.set_y_limits(max_=ymax)

    fig.x_label = xlabel
    fig.y_label = ylabel
    return fig


def _annotate_days(fig):
    """
    Annotates days with vertical lines in the plotille figure.

    Parameters
    ----------
    fig : plotille.Figure
        The figure to annotate.

    Returns
    -------
    fig : plotille.Figure
        The annotated figure.
    """
    # Get limits of the plot 
    x_min, x_max = fig.x_limits()
    y_min, y_max = fig.y_limits()

    # Be consistent with the color mode
    if fig.color_mode == 'names':
        line_color = 'bright_black'
    elif fig.color_mode == 'rgb':
        line_color = (39, 43, 52)
    else:
        raise NotImplementedError

    # Annotate days with vertical lines
    x_ini = (x_min // 24 + 1) * 24
    while x_ini < x_max:
        fig.plot([x_ini, x_ini], [y_min, y_max], lc=line_color, label=str(x_ini))
        x_ini += 24

    return fig


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

    # Keep the range of data within now + 3 days if available
    x_now = datetime.now().hour
    if x_now > x_min:
        x_min = x_now
    if x_now+72 < x_max:
        x_max = x_min + 72

    temperature = df["Temperature"].str.replace(" °C", "").astype(int)
    wind_speed = df["Wind Speed"].astype(int)
    precipitation = df["Precipitation"].replace("--", "0.0").str.replace(" mm", "").astype(float)
    
    # Filter out zero precipitation points
    non_zero_precipitation = precipitation > 0
    precipitation_non_zero = precipitation[non_zero_precipitation]
    hours_non_zero = unrolled_hours[non_zero_precipitation]
    hours_zero = unrolled_hours[~non_zero_precipitation]

    # Plot Temperature
    fig = _initialise_figure(
        width=60, height=10,
        xmin=x_min, xmax=x_max,
        ymin=float(temperature.min() - 2), ymax=float(temperature.max() + 2),
        xlabel="Time (h)",
        ylabel="Temperature (°C)"
    )
    fig.plot(unrolled_hours, temperature, lc='red', interp='linear')
    fig = _annotate_days(fig)
    print(fig.show())

    # Plot Wind Speed
    print('\n')
    fig = _initialise_figure(
        width=60, height=10,
        xmin=x_min, xmax=x_max,
        ymin=0, 
        xlabel="Time (h)",
        ylabel="Wind Speed (km/h)"
    )
    fig.plot(unrolled_hours, wind_speed, lc='magenta', interp='linear')
    fig = _annotate_days(fig)
    print(fig.show())

    # Plot Precipitation as a bar-like plot, ignoring zero values
    print('\n')
    fig = _initialise_figure(
        width=60, height=10,
        xmin=x_min, xmax=x_max,
        ymin=0, 
        xlabel="Time (h)",
        ylabel="Precipitation (mm)"
    )
    # Draw day separation lines first
    fig = _annotate_days(fig)
    # Line joining everything first, for better visualization
    fig.plot(
        unrolled_hours, precipitation,
        lc='blue',
        interp='linear',
        marker=None
    )
    # Markers for non-zero precipitation
    fig.plot(
        hours_non_zero, precipitation_non_zero,
        marker='🌢', # Emulates bar-like appearance
        lc='blue',
        interp=None
    )
    print(fig.show())



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
