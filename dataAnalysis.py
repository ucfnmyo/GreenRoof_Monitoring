import json
import pandas as pd 
import ast
import seaborn as sns
from datetime import datetime, time
import matplotlib.pyplot as plt
import numpy as np


roofArea = 4 * 8 #Area of quadrat = area of green roof / 4 = (length * width) / 4
quadratArea = roofArea/4
quadratVolume = quadratArea * 0.1 #quadrat volume = quadrat area * substrate depth (10 cm)

data = pd.read_json('data.json')
data['data'] = data['data'].apply(lambda x: x.replace(" u", ""))
data['data'] = data['data'].apply(lambda x: x.replace("'", '"'))
data['data'] = data['data'].apply(lambda x: ast.literal_eval(x))

nodes = {"gr_duino1" : "node1", "gr_duino_2" : "node2", "gr_duino3" : "node3", "gr_duino4" : "node4"}
data['dev_id'] = data['dev_id'].apply(lambda x : nodes[x])

wData = list(data['data'])
wData = pd.DataFrame(wData)
wData['pressure']
timeFix = lambda x : datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %Z")
data['time'] = data['time'].apply(timeFix) 

data['volumeRetained'] = data['moisture'].apply(lambda x: (x/100) * quadratVolume) #multiply soil moisutre percentage by volume of quadrat
data['ambTemp'] = wData['temperature'].apply(lambda x: (x - 32) * 5/9) # Convert temperature from F to C
data['ambTemp(K)'] = data['ambTemp'].apply(lambda x: x + 273.15) # Convert temperature from C to K
data['temperature(K)'] = data['temperature'].apply(lambda x: x + 273.15) 
data['ambHumid'] = wData['humidity'].apply(lambda x: x * 100) 
data['rain'] = wData['precipIntensity'].apply(lambda x: (x  * 25.4))
data['rainVolume'] = wData['precipIntensity'].apply(lambda x: (x  * 25.4) * roofArea) #Convert inches to meters then multiply by quadrat Area to attain volume of rain in m3 
data['windSpeed'] = wData['windSpeed'].apply(lambda x: x * 1.609) #Convert mph to kmh
data['windSpeed(ms)'] = data['windSpeed'].apply(lambda x: x / 3.6) #convert kmh to ms
data['windGust'] = wData['windGust'].apply(lambda x: x * 1.609) #convert mph to kmh
data['cloudCover'] = wData['cloudCover']
data['tempDiff'] = data['temperature(K)'] - data['ambTemp(K)']
data['tempDiff%'] = (data['tempDiff'] / data['ambTemp(K)']) * 100
data['humidDiff'] = data['humidity'] - data['ambHumid']
data['humidDiff%'] = (data['humidDiff'] / data['ambHumid']) * 100
#grPD['time'] = grPD['time'].apply(lambda x: str(x.year) + "-" + str(x.month) + "-" + str(x.day) + " " + str(x.hour) + ":" + str(x.minute)) 

data = data.drop(['data', 'w.time'], axis = 1)

#Energy Balance Model caculations
Ca = 1.005 #Atmosperic Heat Capacity (W/m2)
Lv = 2.26 #Latent Heat of Vaporization (J kg-1)
k = 0.41 #Von Karman's Constant
z = 20  #Vertical Reference Height for wind speed and temperature measurements
results = {}

##Logarithmic wind profile method 

U = list(data['windSpeed(ms)'])   #Horizontal Wind Speed
T = list(data['tempDiff'])#Temperature
H = list(data['humidDiff']) #Humidity

Qsensible = []
Qlatent = []

for t,u in zip(T,U): #Calulate sensible heat flux
    Qs = Ca * (z**2) * (k**2) *((u/z) * (t/z))
    Qsensible.append(Qs)

for h,u in zip(H, U): #Calculate vaporization rate kg m^-2 s^-2
    Ql = Lv * (z**2) * (k**2) *((u/z) * (h/z))
    Qlatent.append(Ql)

data['Qlatent'] = Qlatent
data['Qsensible'] = Qsensible
data['BowenRatio'] = data['Qsensible']/ data['Qlatent']
data[['Qlatent', 'Qsensible']].describe()

#Subset to get indvividual node data and subset again to make them all the same length
grData = data.set_index('dev_id')

def nodeAgg(node):
    output = node.set_index('time').resample('15T').mean().reset_index()
    output['hour'] = output['time'].apply(lambda x : datetime.time(x))
    output = output.groupby('hour').mean().reset_index()
    return output

node1 = grData.loc['node1'].reset_index()
node2 = grData.loc['node2'].reset_index()
node3 = grData.loc['node3'].reset_index()
node4 = grData.loc['node4'].reset_index()

timeLen = [len(list(node1['time'])), len(list(node2['time'])), len(list(node3['time'])), len(list(node4['time']))]
minTime = min(timeLen)
node1 = node1.iloc[0:minTime]
node2 = node2.iloc[0:minTime]
node3 = node3.iloc[0:minTime]
node4 = node4.iloc[0:minTime]

node1Agg = nodeAgg(node1)
node2Agg = nodeAgg(node2)
node3Agg = nodeAgg(node3)
node4Agg = nodeAgg(node4)

#Aggregate data by hourly values
aggData = data.set_index('time').resample('15T').mean().reset_index()
aggData['hour'] = aggData['time'].apply(lambda x : datetime.time(x))
dailyAgg = aggData.groupby('hour').mean().reset_index()

#Discriptive Statistics
fullDesc = data.describe()
fullDesc.loc['median'] = data.median()
fullDesc.loc['range'] = data.iloc[:,1:len(data.columns)].max() - data.iloc[:,1:len(data.columns)].min()
fullDesc.to_csv('fullDesc.csv')
node1.describe().to_csv('node1Stats.csv')
node2.describe().to_csv('node2Stats.csv')
node3.describe().to_csv('node3Stats.csv')
node4.describe().to_csv('node4Stats.csv')


######Violin Plots#######
sns.set()
sns.set_style('whitegrid')
sns.set_palette(sns.color_palette('Set1'))
##Temperature 
tempDesc = data[['temperature', 'ambTemp']]
tempDesc.columns = ['Green Roof Temperature', 'Ambient Temperature']
tempDesc = tempDesc.melt()
tempVio = sns.violinplot(x="variable", y="value",data=tempDesc)
tempVio.set(xlabel = "", ylabel = "Temperature (°C)")
plt.tight_layout()
plt.savefig('figures/tempVio.pdf',  bbox_inches = "tight", transparent = True)
##Humidity 
humDesc = data[['humidity', 'ambHumid']]
humDesc.columns = ['Green Roof Humidity', 'Ambient Humidity']
humDesc = humDesc.melt()
humVio = sns.violinplot(x="variable", y="value",data=humDesc)
humVio.set(xlabel = "", ylabel = "Humidity (%)")
plt.savefig('figures/humidVio.pdf',  bbox_inches = "tight", transparent = True)

#Line graph Visualisations using Seaborn

###TOTAL DATA SET##########

##GR temperature vs ambient temperature
fig, tempLine = plt.subplots(figsize=(10,5))
tempLine = sns.lineplot(x="time", y="temperature", data=aggData, ax = tempLine)
tempLine = sns.lineplot(x = "time", y = "ambTemp", data = aggData, ax = tempLine)
tempLine.set(xlabel = "Time", ylabel = "Temperature (°C)")
tempLine.legend(labels = ['GR Temperature', 'Ambient Temperature'])
fig.savefig("figures/tempLine.pdf", bounding_box = "tight", transparent = True)
##GR Humidity vs ambient humidity
fig, humidLine = plt.subplots(figsize=(10,5))
humidLine = sns.lineplot(x="time", y="humidity", data=aggData, ax = humidLine)
humidLine = sns.lineplot(x = "time", y = "ambHumid", data = aggData, ax = humidLine)
humidLine.legend(labels = ['GR Humidity', 'Ambient Humidity'])
humidLine.set(xlabel = "Time", ylabel = "Humidity (%)")
fig.savefig("figures/humidLine.pdf", bounding_box = "tight", transparent = True)
##Percentage Difference - temperature and humidity
fig, diffLine = plt.subplots(figsize = (10, 5))
diffLine = sns.lineplot(x = "time", y = "tempDiff%", data = aggData, ax = diffLine)
diffLine = sns.lineplot(x = "time", y = "humidDiff%", data = aggData, ax = diffLine)
diffLine.legend(labels = ['Temperature Ratio', 'Humidity Ratio'])

#GR Soil Moisture vs Rain
fig, moistureLine = plt.subplots(figsize = (10,5))
moistureLine = sns.lineplot(x="time", y="moisture", data=aggData, ax = moistureLine)

#Water retention volume vs Rain volume
fig, retentionLine = plt.subplots(figsize= (10,5))
retentionLine = sns.lineplot(x = 'time', y = 'rain', data = aggData, ax= retentionLine)
retentionLine = sns.lineplot(x = 'time', y = 'volumeRetained', data = aggData, ax = retentionLine)

#Light Intensity
fig, lightLine = plt.subplots(figsize = (10,5))
lightLine = sns.lineplot(x = 'time', y = 'light', data = aggData, ax = lightLine)

#Sensible Heat Flux
fig, sensibleLine = plt.subplots(figsize = (10,5))
sensibleLine = sns.lineplot(x = 'hour', y = 'Qsensible', data = dailyAgg, ax = sensibleLine)
dailyAgg.Qsensible.describe()
#Latent Heat Flux
fig, latentLine = plt.subplots(figsize = (10,5))
latentLine = sns.lineplot(x = 'time', y = 'Qlatent', data = aggData, ax = latentLine)
aggData['Qlatent'].mean()
#Bowen Ratio
fig, bowenLine = plt.subplots(figsize = (10,5))
latentLine = sns.lineplot(x = 'time', y = 'BowenRatio', data = aggData, ax = bowenLine)

#####DAILY AVERAGE DATASET######
##GR temperature vs ambient temperature
fig, dailyTemp = plt.subplots(figsize=(10,5))
dailyTemp = sns.lineplot(x="hour", y="temperature", data=dailyAgg, ax = dailyTemp)
dailyTemp = sns.lineplot(x = "hour", y = "ambTemp", data = dailyAgg, ax = dailyTemp)
dailyTemp.legend(labels = ['GR Temperature', 'Ambient Temperature'])
dailyTemp.set(xlabel = "Time", ylabel = "Temperature (°C)")
plt.savefig("figures/dailyTemp.pdf", bounding_box = "tight", transparent = True)
##GR Humidity vs ambient humidity
fig, dailyHumid = plt.subplots(figsize=(10,5))
dailyHumid = sns.lineplot(x="hour", y="humidity", data=dailyAgg, ax = dailyHumid)
dailyHumid = sns.lineplot(x = "hour", y = "ambHumid", data = dailyAgg, ax = dailyHumid)
dailyHumid.set(xlabel  = "Hour", ylabel = "Humidity (%)")
dailyHumid.legend(labels = ["GR Humidity", "Ambient Humidity"])
plt.savefig("figures/dailyHumid.pdf", bounding_box = "tight", transparent = True)
##Thermal/humidity difference
fig, dailyDiff = plt.subplots(figsize = (10, 5))
dailyDiff = sns.lineplot(x = "hour", y =  "tempDiff%", data = dailyAgg, ax = dailyDiff)
dailyDiff = sns.lineplot(x = "hour", y = "humidDiff%", data = dailyAgg, ax = dailyDiff)

#####NODE VISUALISATIONS#####
##node temperature comparison
fig, nodeTemp = plt.subplots(figsize=(10,5))
nodeTemp = sns.lineplot(x="hour", y="temperature", data=node1Agg, ax = nodeTemp)
nodeTemp = sns.lineplot(x="hour", y="temperature", data=node2Agg, ax = nodeTemp)
nodeTemp = sns.lineplot(x="hour", y="temperature", data=node3Agg, ax = nodeTemp)
nodeTemp = sns.lineplot(x="hour", y="temperature", data=node4Agg, ax = nodeTemp)
nodeTemp = sns.lineplot(x="hour", y="ambTemp", data=aggData, ax = nodeTemp)
nodeTemp.legend(labels = ['node1', 'node2', 'node3', 'node4', 'Ambient Temperature'])
nodeTemp.set(xlabel = "Time", ylabel = "Temperature (°C)")
fig.savefig("figures/nodeTemp.pdf", bounding_box = "tight", transparent = True)
##Node temperatture amplitude bar char
sns.barplot(x = 'dev_id', y = 'temperature', data = data)

##node humidity comparison
fig, nodeHumid = plt.subplots(figsize=(10,5))
nodeHumid = sns.lineplot(x="hour", y="humidity", data=node1Agg, ax = nodeHumid)
nodeHumid = sns.lineplot(x="hour", y="humidity", data=node2Agg, ax = nodeHumid)
nodeHumid = sns.lineplot(x="hour", y="humidity", data=node3Agg, ax = nodeHumid)
nodeHumid = sns.lineplot(x="hour", y="humidity", data=node4Agg, ax = nodeHumid)
#nodeHumid = sns.lineplot(x="hour", y="humidity", data=aggData, ax = nodeHumid)
nodeHumid.legend(labels = ['node1', 'node2', 'node3', 'node4'])
nodeHumid.set(xlabel = "Time", ylabel = "Humidity(%)")
plt.savefig("figures/nodeHumid.pdf", bounding_box = "tight", transparent = True)
##Qsensible nodes
fig, nodeQs = plt.subplots(figsize=(10,5))
nodeQs = sns.lineplot(x="hour", y="Qsensible", data=node1Agg, ax = nodeQs)
nodeQs = sns.lineplot(x="hour", y="Qsensible", data=node2Agg, ax = nodeQs)
nodeQs = sns.lineplot(x="hour", y="Qsensible", data=node3Agg, ax = nodeQs)
nodeQs = sns.lineplot(x="hour", y="Qsensible", data=node4Agg, ax = nodeQs)
nodeQs.legend(labels = ['node1', 'node2', 'node3', 'node4'])
nodeQs.set(xlabel = "Time", ylabel = "Heat Flux (W/m$^2$)")
plt.savefig("figures/nodeQs.pdf", bounding_box = "tight", transparent = True)
##Qlatent nodes
fig, nodeQl = plt.subplots(figsize=(10,5))
nodeQl = sns.lineplot(x="time", y="Qlatent", data=node1, ax = nodeQl)
nodeQl = sns.lineplot(x="time", y="Qlatent", data=node1, ax = nodeQl)
nodeQl = sns.lineplot(x="time", y="Qlatent", data=node1, ax = nodeQl)
nodeQl = sns.lineplot(x="time", y="Qlatent", data=node1, ax = nodeQl)
nodeQl.legend(labels = ['node1', 'node2', 'node3', 'node4'])
nodeQl.set(xlabel = "Time", ylabel = "Heat Flux (W/m$^2$)")
plt.savefig("figures/nodeQl.pdf", bounding_box = "tight", transparent = True)


##Obtain daily average Qs and Ql to calculate bowen ratio for each node per day
def nodeBowen(nodes):
    output = pd.DataFrame()
    n = 1
    for node in nodes:
        node = node.set_index('time').resample('D').mean()
        node = node.Qsensible/node.Qlatent
        node = pd.DataFrame(node).reset_index()
        node['node'] = 'node' + str(n)
        node.columns =['day', 'BowenRatio', 'node']
        output = pd.concat([output, node])
        n = n + 1

    mean = output.groupby('day').mean().reset_index()
    mean['node'] = 'mean'
    output = pd.concat([output, mean])
    return output
nodeBowen = nodeBowen([node1, node2, node3, node4])
xlabels = (nodeBowen['day'].apply(lambda x: "0"+str(x.month) + "-0" + str(x.day))).unique()
bowenBar = sns.barplot(x = "day", y = "BowenRatio", hue = 'node', data = nodeBowen, linewidth = 0, edgecolor = ".2")
bowenBar.set_xticklabels(xlabels)
plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
plt.savefig('figures/BownBar.pdf', bounding_box = 'tight', transparent = True)
nodeBowen
set(list(nodeBowen.day))

##Output Qsensible and Qlatent stats as csv
def Qdesc(nodes):
    output = pd.DataFrame()
    for node in nodes:
        nodestats =  node[['Qlatent', 'Qsensible']].describe()
        output = pd.concat([output, nodestats], axis = 1)
    output.to_csv("nodeQStats.csv")
     
Qdesc([node1Agg, node2Agg, node3Agg, node4Agg])
data['Qsensible'].describe()

#nodeTemp = sns.lineplot(x="hour", y="ambTemp", data=aggData, ax = nodeTemp)
nodeTemp.legend(labels = ['node1', 'node2', 'node3', 'node4', 'A mbient Temperature'])
nodeTemp.set(xlabel = "Time", ylabel = "Temperature (°C)")
#Node soil moisture comparison
fig, nodeMoisture = plt.subplots(figsize=(10,5))
nodeMoisture = sns.lineplot(x="hour", y="moisture", data=node1Agg, ax = nodeMoisture)
nodeMoisture = sns.lineplot(x="hour", y="moisture", data=node2Agg, ax = nodeMoisture)
nodeMoisture = sns.lineplot(x="hour", y="moisture", data=node3Agg, ax = nodeMoisture)
nodeMoisture = sns.lineplot(x="hour", y="moisture", data=node4Agg, ax = nodeMoisture)
nodeMoisture.legend(labels = ['node1', 'node2', 'node3', 'node4'])
nodeMoisture.set(xlabel = "Time", ylabel = "Soil Moisture (%)")
#Node Violin Plots
#Temperature
data = data.sort_values('dev_id')
nodeTempVio = sns.violinplot(x="dev_id", y="temperature",data=data)
nodeTempVio.set(xlabel = "", ylabel = "Temperature (°C)")
plt.savefig("figures/nodeTempVio.pdf", bounding_box = "tight", transparent = True)
#Humidity
nodeHumidVio = sns.violinplot(x="dev_id", y="humidity",data=data)
nodeHumidVio.set(xlabel = "", ylabel = "Humidity (%)")
plt.savefig("figures/nodeHumidVio.pdf", bounding_box = "tight", transparent = True)
sns.violinplot(x="dev_id", y="moisture",data=data)
sns.violinplot(x="dev_id", y="light",data=data)

##Temperature, Windspeed and UV exposure
#WindChart
fig, windLine = plt.subplots(figsize = (10,5))
windLine = sns.lineplot(x="time", y="windGust", data=aggData, ax = windLine)
windLine = sns.lineplot(x="time", y="windSpeed", data=aggData, ax = windLine)
windLine.legend(labels = ['Wind Gust', 'Wind Speed'], loc = "upper center")
windLine.set(xlabel = "Time", ylabel = "Wind Speed (km/hr)")
plt.savefig('figures/windSpeed.pdf',  bbox_inches = "tight", transparent = True)
#RainChart
fig, rainLine = plt.subplots(figsize = (10,5))
rainLine = sns.lineplot(x="time", y="rain", data=aggData, ax = rainLine)
rainLine.set(xlabel = "Time", ylabel = "Precipitation Intensity (mm/hr)")
rainLine.legend(labels = 'Rain Intensity', loc = "upper center")
plt.savefig('figures/Rain.pdf',  bbox_inches = "tight", transparent = True)

aggData['humidDiff%'].min()


aggData[['Qsensible', 'Qlatent']].describe()
aggData['BowenRatio'].describe()




