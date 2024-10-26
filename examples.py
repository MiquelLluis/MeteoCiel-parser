import subprocess

from meteociel import fetch_weather


def paris_arome():
    subprocess.run(['python', 'meteociel.py', 'https://www.meteociel.fr/previsions-arome-1h/27817/paris.htm'])

def paris_arome_plot():
    subprocess.run(['python', 'meteociel.py', '-p', 'https://www.meteociel.fr/previsions-arome-1h/27817/paris.htm'])


if __name__ == '__main__':
    paris_arome()
    paris_arome_plot()