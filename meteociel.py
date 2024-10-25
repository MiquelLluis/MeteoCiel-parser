from bs4 import BeautifulSoup
import pandas as pd
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