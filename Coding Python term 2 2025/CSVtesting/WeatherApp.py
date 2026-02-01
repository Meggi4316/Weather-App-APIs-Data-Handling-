import PySimpleGUI as sg
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
import urllib.request
import os
import socket
from PIL import Image, ImageTk, ImageSequence


#Converting degrees to direction
def direction(degrees):
    if degrees > 315 or degrees <= 45:
        return "North"
    elif degrees > 45 and degrees <= 135:
        return "East"
    elif degrees > 135 and degrees <= 225:
        return "South"
    else:
        return "West"
    
#Checking internet connection
def internet_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

#Creating GIF
def select_weather_gif(description):
    description = description.lower()
    for keyword, filename in {
        "clear": "sun.gif",
        "cloud": "cloudy.gif",
        "rain": "drizzle.gif",
        "storm": "storm.gif",
        "snow": "snowman.gif",
    }.items():
        if keyword in description and os.path.exists(filename):
            return filename
    return None
    
def load_resized_gif_frames(filepath, target_size=(80, 80)):
    gif = Image.open(filepath)
    duration = gif.info.get("duration", 100)
    frames = [
        ImageTk.PhotoImage(
            frame.copy().convert("RGBA").resize(target_size, Image.LANCZOS)
        )
        for frame in ImageSequence.Iterator(gif)
    ]
    return frames, duration

#API Key
key = "db5620faef0a378e1f0a1ac502088363"
icon_folder = "weather_icons"
os.makedirs(icon_folder, exist_ok=True)

if not internet_connected():
    sg.popup_error("❌ This app requires an internet connection to work.", title="Connection Error")
    exit()

#Tab Layout
tab1_layout = [
    [sg.Text("🌍 Enter a city or country:", font=("Helvetica", 14, "bold")),
     sg.InputText(key="city_name", font=("Helvetica", 12)),
     sg.Button("Get Weather", font=("Helvetica", 12))],
    [sg.Image(key="icon", visible=False), sg.Image(key="-GIF-", size=(80, 80), visible=False)],
    [sg.Text("🔆 Weather Report:", font=("Helvetica", 14, "bold"))],
    [sg.Text("", size=(50, 4), key="weather", font=("Helvetica", 12))]
]
 
tab2_layout = [
    [sg.Text("Feels Like Advice: ", font=("Helvetica", 14, "bold"))],
    [sg.Text("", size=(50,2), font=("Helvetica", 12), key="advice")],
    [sg.Text("What to Wear:", font=("Helvetica", 12, "bold"))],
    [sg.Text("", size=(50,1), font=("Helvetica", 12), key="wear")]
]

tab3_layout = [
    [sg.Text("🗓️ Weekly Forecast Summary:", font=("Helvetica", 14, "bold"))],
    [sg.Multiline("", size=(50, 12), font=("Helvetica", 12), key="weekly", disabled=True)],
]

tab4_layout = [
    [sg.Button("Show Weekly Graph", font=("Helvetica", 12))]
]

layout = [
    [sg.TabGroup([
        [sg.Tab("Current Weather", tab1_layout),
         sg.Tab("Advice", tab2_layout),
         sg.Tab("Weekly Forecast",tab3_layout),
         sg.Tab("Graph", tab4_layout)]
    ], font=("Helvetica", 12))],
    [sg.Push(), sg.Button("Exit", font=("Helvetica", 12))]
]

#Creating Window
window = sg.Window("🌎 GLOBAL WEATHER APP 🌎", layout, finalize=True, font=("Helvetica", 12))

select_city = ""
weather_data = None
gif_frames = []
gif_duration = 100
frame_index = 0

while True:
    event, values = window.read(timeout=gif_duration if gif_frames else None)

    if gif_frames:
        try:
            if window.was_closed():
                break
            window["-GIF-"].update(data=gif_frames[frame_index])
            frame_index = (frame_index + 1) % len(gif_frames)
        except:
            break

    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

    if event == "Get Weather":
        city_input = values["city_name"]
        selected_city = city_input.title()

        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_input}&limit=1&appid={key}"
        geo_response = requests.get(geo_url).json()

        if not geo_response:
            window["weather"].update("City not found. Try again.")
            continue

        lat = geo_response[0]["lat"]
        lon = geo_response[0]["lon"]

        url = f"https://api.openweathermap.org/data/3.0/onecall?units=metric&lat={lat}&lon={lon}&exclude=minutely,alerts&appid={key}"
        response = requests.get(url)
        parsed_data = json.loads(response.text)

        current = parsed_data["current"]
        temp = current["temp"]
        feels_like = current["feels_like"]
        wind_speed = int(current["wind_speed"] * 3.6)
        wind_dir = direction(current["wind_deg"])
        humidity = current["humidity"]
        description = current["weather"][0]["description"]

        gif_file = select_weather_gif(description)
        if gif_file:
            gif_frames, gif_duration = load_resized_gif_frames(gif_file, target_size=(80, 80))
            frame_index = 0
            window["-GIF-"].update(visible=True)
            window["icon"].update(visible=False)
        else:
            gif_frames = []
            icon_code = current["weather"][0]["icon"]
            icon_path = os.path.join(icon_folder, f"{icon_code}.png")
            if not os.path.exists(icon_path):
                urllib.request.urlretrieve(f"http://openweathermap.org/img/wn/{icon_code}@2x.png", icon_path)
            window["icon"].update(filename=icon_path, visible=True)
            window["-GIF-"].update(visible=False)

        weather_text = (
            f"🔆 {selected_city} Weather:\n"
            f"{description.title()} | {temp}°C (Feels like {feels_like}°C)\n"
            f"Wind: {wind_speed} km/h from {wind_dir} | Humidity: {humidity}%"
        )
        window["weather"].update(weather_text)

        #Advice box
        if feels_like < 10:
            advice = "🥶 It's chilly! Wear layers and stay warm. ❄️"
            clothing = "Thick coat, scarf, gloves, boots."
        elif feels_like > 30:
            advice = "🥵 It's hot! Avoid being outside too long. ☀️"
            clothing = "Shorts, t-shirt, sunglasses, hat."
        elif 10 <= feels_like <= 20:
            advice = "🌤️ Cool but nice. Light layers recommended."
            clothing = "Light jacket or jumper with jeans."  
        else:
            advice = "🙂 Comfortable weather . Perfect for a walk! 🌈"
            clothing = "T-shirt, pants, maybe a hoodie."

        if "rain" in description.lower():
            advice += "\n🌧️ It might rain. Take an umbrella!"
        elif "clear" in description.lower() and feels_like > 25:
            advice += "\n🕶️ UV might be high. Wear sunscreen!"

        window["advice"].update(advice) 
        window["wear"].update(clothing)

        #weekly forecast
        daily = parsed_data["daily"]
        daily.pop(0)

        max_temps = []
        min_temps = []
        summaries = []

        for day in daily:
            desc = day.get("summary") or day ["weather"][0]["description"].capitalize()
            summaries.append(desc)
            max_temps.append(day["temp"]["max"])
            min_temps.append(day["temp"]["min"])

        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        today_index = datetime.today().weekday()
        tomorrow_index = (today_index +1) % 7
        rotated_days = weekdays[tomorrow_index:] + weekdays[:tomorrow_index]

        weekly_text = "🌤️ Weekly Forecast\n\n"
        for i, desc in enumerate(summaries):
            day = rotated_days[i % 7]
            min_temp = f"{min_temps[i]:.1f}°C"
            max_temp = f"{max_temps[i]:.1f}°C"

            if "rain" in desc.lower():
                emoji = "🌧️"
            elif "cloud" in desc.lower():
                emoji = "☁️"
            elif "storm" in desc.lower():
                emoji = "⛈️"
            elif "snow"in desc.lower():
                emoji = "❄️"
            elif "clear" in desc.lower():
                emoji = "🌞"
            else:
                emoji = "🌈"
            
            weekly_text += f"{emoji} {day}: {desc}\n"
            weekly_text += f"   Min: {min_temp} | Max: {max_temp}\n\n"

        window["weekly"].update(weekly_text)
        weather_data = (max_temps, min_temps)

    if event == "Show Weekly Graph" and selected_city and weather_data:
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        today = datetime.today().weekday()
        rotated_days = weekdays[today+1:] + weekdays[:today+1]

        plt.figure(figsize=(10, 5))
        plt.plot(rotated_days, weather_data[0], label="Max Temp", color="red", marker='o')
        plt.plot(rotated_days, weather_data[1], label="Min Temp", color="blue", marker='o')
        plt.fill_between(rotated_days, weather_data[0], weather_data[1], color='lightgray', alpha=0.3)

        for i in range(len(rotated_days)):
            plt.text(rotated_days[i], weather_data[0][i] + 0.5, f"{weather_data[0][i]}°", ha='center', fontsize=10)
            plt.text(rotated_days[i], weather_data[1][i] - 1.5, f"{weather_data[1][i]}°", ha='center', fontsize=10)

        plt.title(f"Weekly Forecast for {selected_city}", fontsize=14)
        plt.xlabel("Day")
        plt.ylabel("Temperature (°C)")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

window.close()