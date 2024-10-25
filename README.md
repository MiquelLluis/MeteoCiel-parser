# Meteociel Weather Scraper

This is a personal Python script that fetches and parses hourly weather forecast data from [Meteociel](https://www.meteociel.fr/) for specified locations through their URL. It scrapes table data from Meteociel forecast pages and returns a structured DataFrame for analysis.


## Usage

```python
from meteociel import fetch_weather

# Example: Fetch Paris weather data from the AROME model
url = 'https://www.meteociel.fr/previsions-arome-1h/27817/paris.htm'
weather = fetch_weather(url)
print(weather)
```


### Dependencies

- `pandas`: Data manipulation and analysis.
- `requests`: HTTP requests for fetching web pages.
- `beautifulsoup4`: HTML parsing and data extraction.
