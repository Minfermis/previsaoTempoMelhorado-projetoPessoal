import tkinter as tk
import requests
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import ttkbootstrap
from translate import Translator
import math
import pyttsx3
import threading
import os
import shutil
from win32com.client import Dispatch

def get_weather(city):
    API_key = "00bf3dcc830277391166d8ef7a6da84f"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric"
    res = requests.get(url)

    if res.status_code == 404:
        messagebox.showerror("Erro", "Cidade não encontrada")
        return None

    weather = res.json()
    icon_id = weather["weather"][0]["icon"]
    temperature = weather["main"]["temp"]
    description = weather["weather"][0]["description"]
    city = weather["name"]
    country = weather["sys"]["country"]

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
    return (icon_url, temperature, description, city, country)

def translate_description(description):
    translation_dict = {
        'clear sky': 'céu limpo',
        'few clouds': 'poucas nuvens',
        'scattered clouds': 'nuvens dispersas',
        'broken clouds': 'nuvens quebradas',
        'shower rain': 'chuva fraca',
        'rain': 'chuva',
        'thunderstorm': 'tempestade',
        'snow': 'neve',
        'mist': 'névoa',
        'overcast clouds': 'nublado'
    }
    return translation_dict.get(description, description)

def provide_reminders_async(city, temperature, description):
    # Inicializa o motor de síntese de voz do Google
    engine = pyttsx3.init()

    # Define a voz do Google
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Escolha a voz que você prefere

    # Fala a temperatura atual
    engine.say(f"A temperatura em {city} é {temperature:.1f} graus Celsius.")
    
    # Fala a descrição do clima
    engine.say({description})

    # Verifica as condições com base na temperatura
    if temperature <= 15:
        engine.say(f"Vai estar frio em {city}. Não se esqueça de levar um agasalho.")
    elif 16 <= temperature <= 24:
        engine.say(f"O clima em {city} está normal. Aproveite o seu dia!")
    else:
        engine.say(f"Vai estar quente em {city}. Lembre-se de usar protetor solar antes de sair.")

    # Verifica as condições de chuva
    if "rain" in description:
        engine.say(f"E também está prevista chuva em {city}. Não se esqueça de levar um guarda-chuva.")

    engine.runAndWait()

# Função para chamar provide_reminders em uma thread separada
def call_provide_reminders(city, temperature, description):
    threading.Thread(target=provide_reminders_async, args=(city, temperature, description)).start()


def search():
    city = cidadeEntrar.get()
    result = get_weather(city)
    if result is None:
        return
    icon_url, temperature, description, city, country = result
    location_label.configure(text=f"{city}, {country}")

    rounded_temperature = math.floor(temperature)
    temperature_label.configure(text=f"Temperatura: {rounded_temperature}°C")
    translated_description = translate_description(description)
    descripation_label.configure(text=f"Descrição: {translated_description}")

    # Chama provide_reminders em uma thread separada
    call_provide_reminders(city, rounded_temperature, translated_description)

    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon



# Criar Janela
root = ttkbootstrap.Window(themename="morph")
root.title("SunRain")
root.geometry("400x400")

# Para inserir o nome da cidade
cidadeEntrar = ttkbootstrap.Entry(root, font="Helvetica, 18")
cidadeEntrar.pack(pady=10)

# Para procurar previsão do tempo
search_button = ttkbootstrap.Button(root, text="Pesquisar", command=search, bootstyle="warning")
search_button.pack(pady=10)
location_label = tk.Label(root, font="Helvetica, 25")
location_label.pack(pady=20)
icon_label = tk.Label(root)
icon_label.pack()

# Área da temperatura 
temperature_label = tk.Label(root, font="Helvetica, 20")
temperature_label.pack()

# Área da descrição
descripation_label = tk.Label(root, font="Helvetica, 20")
descripation_label.pack()


root.mainloop()
