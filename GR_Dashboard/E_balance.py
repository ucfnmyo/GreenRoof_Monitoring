
from flask import flask
import json
import numpy as np


#initialising variables employed in the json object
temperature = []
humidity = []
moisture = []
light = []
timeRaw = []
time = []
jsonData = {"temperature" : temperature, "humidity" : humidity, "soilMoisture" : moisture,"light" : light, "time" : time, "timeRaw" : timeRaw}
nDays = []
with open('/Users/MedoYounes/Documents/GR_Dashboard/data.json', 'r') as f:
    data = json.load(f)

for i in data:
    temperature.append(i['temperature'])
    humidity.append(i['humidity'])
    moisture.append(i['soilMoisture'])
    light.append(i['light'])
    timeRaw.append(i['time'])

data
jsonData

##Calculate Sensible Heat Flux (Qsensible)

ca = 5.95 * 10**21
k = 0.4
z = 20
u = np.random.randint(1, 10, 717)
t = jsonData['temperature']
q_sensible = []

for i in range(0, len(t)):
    qs = -ca* (k**2) * (z**2) * (u[i]/z * t[i]/z)
    q_sensible.append(qs)


## Calculate Latent Heat of Vaporization

lv = 2260 * 10**3
rh = jsonData['humidity']
q_latent = []

for i in range(0, len(rh)):
    qL = -lv ** (k**2) * (z**2) * (u[i]/z * rh[i]/z)
    q_latent.append(qL)

q_latent