import requests
from datetime import datetime


apiCall = (
    "https://api.openweathermap.org/data/3.0/onecall?"
    "lat=-35.282001"
    "&lon=149.128998"
    "&exclude=hourly,minutely,alerts"
    "&appid=db5620faef0a378e1f0a1ac502088363"
    "&units=metric"
)

r = requests.get(url=apiCall)

print(r.status_code)

data = r.json()

print("Current Temperature: " , str(data["current"]["temp"]) + "°" )
print("Wind speed: " , str(data["current"]["wind_speed"]) + "m/s" )
print("Wind Direction: " , str(data["current"]["wind_deg"]) + "°" )
if "rain" in data["daily"][0]:
    print("Possible Rainfall: ", str(data["daily"][0]["rain"]) + "mm")
else: 
    print("Rain data not avaliable")


sunrise = data["current"]["sunrise"]
sunrise = datetime.fromtimestamp(sunrise)
print("Sunrise: ", sunrise)
          
      




import PySimpleGUI as sg

sg.theme('DarkAmber')  

layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

window = sg.Window('Window Title', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': 
        break
    print('You entered ', values[0])

window.close()
