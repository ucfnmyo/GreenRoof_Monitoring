from flask import Flask, render_template
from flask import request,jsonify
import requests
import json
import pandas as pd
from datetime import datetime
from pandas.io.json import json_normalize
import ast
import numpy as np
import pymysql

app = Flask(__name__)

class Database:
    def __init__(self):
        host = "localhost"
        user = "ttn"
        password = "ttn2019"
        db = "scGreenRoof"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()
        
    def fullData(self):
        self.cur.execute("SELECT * FROM GR_DATA d INNER JOIN weatherData w ON d.time = w.time;")
        result = self.cur.fetchall()
        
        PD = pd.DataFrame(result).set_index('dev_id')
        node1 = PD.loc['gr_duino1'].reset_index()
        node2 = PD.loc['gr_duino_2'].reset_index()
        node3 = PD.loc['gr_duino3'].reset_index()
        node4 = PD.loc['gr_duino4'].reset_index()
        
        timeLen = [len(list(node1['time'])), len(list(node2['time'])), len(list(node3['time'])), len(list(node4['time']))]
        
        minTime = min(timeLen)
        node1 = node1.iloc[0:minTime]
        node2 = node2.iloc[0:minTime]
        node3 = node3.iloc[0:minTime]
        node4 = node4.iloc[0:minTime]
        
        return [node1, node2, node3, node4]
        
    def nodeData(self, node):
        if node == 2:
            self.cur.execute("SELECT * FROM GR_DATA d INNER JOIN weatherData w ON d.time = w.time WHERE d.dev_id = 'gr_duino_" + str(node) + "';")
            result = self.cur.fetchall()
            return result
        self.cur.execute("SELECT * FROM GR_DATA d INNER JOIN weatherData w ON d.time = w.time WHERE d.dev_id = 'gr_duino" + str(node) + "';")
        
        result = self.cur.fetchall()
        
    def jsonOutput(self):
        self.cur.execute("SELECT * FROM GR_DATA d INNER JOIN weatherData w ON d.time = w.time;")
        result = self.cur.fetchall()
      
        
        return result
        
        return result
    


@app.route('/')
def dashboard():

    def nodes():
        db = Database()
        db.fullData()
        gr_duino1 = db.nodeData(1) #pull data for nodes
        gr_duino2 = db.nodeData(2)
        gr_duino3 = db.nodeData(3)
        gr_duino4 = db.nodeData(4)
        
        gr1PD = pd.DataFrame(gr_duino1) #Convert to PD
        gr2PD = pd.DataFrame(gr_duino2)
        gr3PD = pd.DataFrame(gr_duino3)
        gr4PD = pd.DataFrame(gr_duino4)
        
        wData = []
        wTime = []
        
        roofArea = 4 * 8 #Area of quadrat = area of green roof / 4 = (length * width) / 4
        quadratArea = roofArea/4
        quadratVolume = quadratArea * 0.1 #quadrat volume = quadrat area * substrate depth (10 cm)
        
        def wFormat(gr_duino, grPD): #Transform weather data to PD and take desired columns : temperature, humidity, precipIntensity and windSpeed
            
            for i in range(0, len(gr_duino)):
                data = gr_duino[i]['data'].replace("'", '"')
                data = data.replace(" u", "")
                data = ast.literal_eval(data)
                wData.append(data)
            wPD = pd.DataFrame(wData)
            wPD['temperature'] = wPD['temperature'].apply(lambda x: (x - 32) * 5/9) # Convert temperature from F to C
            wPD['humidity'] = wPD['humidity'].apply(lambda x: x * 100) 
            grPD['waterRetention(m3)']= grPD['moisture'].apply(lambda x: (x/100) * quadratVolume) #multiply soil moisutre percentage by volume of quadrat
            grPD['ambTemp'] = wPD['temperature']
            grPD['ambHumid'] = wPD['humidity']
            grPD['rain'] = wPD['precipIntensity'].apply(lambda x: (x * quadratArea) / 61023.744) #Divide by 61023.744 to convert cubic inches to cubic metres 
            grPD['windspeed'] = wPD['windSpeed']
            #grPD['time'] = grPD['time'].apply(lambda x: datetime.datetime(x))
            grPD['time'] = grPD['time'].apply(lambda x: str(x.year) + "-" + str(x.month) + "-" + str(x.day) + " " + str(x.hour) + ":" + str(x.minute)) 
            grPD = grPD.drop(['data', 'w.time'], axis = 1)
            
            return grPD
        
        gr1PD = wFormat(gr_duino1, gr1PD)
        gr2PD = wFormat(gr_duino1, gr2PD)
        gr3PD = wFormat(gr_duino1, gr3PD)
        gr4PD = wFormat(gr_duino1, gr4PD)
     
        grList = [gr1PD, gr2PD, gr3PD, gr4PD]
        
        def aggData(grPDs): # Calculate mean temperature, humidity, soil moisture etc
            lens = [len(grPDs[0]),len(grPDs[1]),len(grPDs[2]),len(grPDs[3])]
            
            if lens[0] != lens[1] and lens[0] != lens[2] and lens[0] != lens[3]: #Checking if node data of same length, if not, take length of shortest dataset
                t = - min(lens)
            else:
                t = -lens[0]
            temps = []
            humd = []
            soils = []
            retention = []
            lights = []
            wTemps = []
            wHumd = []
            wRain = []
            dates = []
            
                
            for grPD in grPDs:
                dates.append(grPD['time'].iloc[t:-1])
                temps.append(grPD['temperature'].iloc[t:-1])
                humd.append(grPD['humidity'].iloc[t:-1])
                soils.append(grPD['moisture'].iloc[t:-1])
                retention.append(grPD['waterRetention(m3)'].iloc[t:-1])
                lights.append(grPD['light'].iloc[t:-1])
                wTemps.append(grPD['ambTemp'].iloc[t:-1])
                wHumd.append(grPD['ambHumid'].iloc[t:-1])
                wRain.append(grPD['rain'].iloc[t:-1])
            
            def listMean(data): #simple function to obtain mean of multiple lists
                mean = list(np.mean(data,axis = 0))
                return mean
            
            
            tempMean = listMean(temps)
            humMean = listMean(humd)
            soilMean = listMean(soils)
            lightMean = listMean(lights)
            wTempMean = listMean(wTemps)
            wHumidMean = listMean(wHumd)
            
            
            def basicPerformance(grData, wData): #Performance function for thermal and humidity
                diff = list(np.array(grData) - np.array(wData))
                percentDiff = list((np.array(diff)/np.array(wData)) * 100)
                results = {"difference" : diff, "percentDiff" : percentDiff}
                return results
                
            def hydroPerformance(retentionList, rainList):
                npArr = lambda x: np.array(x)
                totalRain = list(sum(npArr(rainList)))
                totalRetention = list(sum(npArr(retentionList)))
                totalRetention = [0 if np.isnan(x) else x for x in totalRetention]
                rainRatio = list(np.array(totalRetention)/np.array(totalRain))
                rainRatio = [0 if np.isnan(x) else x for x in rainRatio]
                results = {"rainRatio" : rainRatio, "totalRetention" : totalRetention}
                return results
                
            tempPerf = basicPerformance(tempMean, wTempMean)
            humdPerf = basicPerformance(humMean, wHumidMean)
            hydroPerf = hydroPerformance(retention, wRain)
            
            results = {"thermal" : tempPerf, "humidity" : humdPerf, "hydro" : hydroPerf, "tempMean" : tempMean, "humMean" : humMean, "moistMean" : soilMean, "lightMean" : lightMean, "time": list(dates[0]), "wTemp" : wTempMean, "wHumidity" : wHumidMean }
           
            return results
         
        aggData = aggData(grList)
   
        def liveData(data):
            l = len(data['tempMean']) -1
            temp = data['tempMean'][l]
            hum = data['humMean'][l]
            moist = data['moistMean'][l]
            light = data['lightMean'][l]
            time = data['time'][l]
            results = {"temperature" : temp, "humidity": hum, "moisture" : moist, "light" : light, "time" : time}
            return results
            
        liveData = liveData(aggData)
        
        def pdJson(grPD):
            json = grPD.to_json(orient = 'columns')
            return(json)
            
        gr_duino1 = pdJson(gr1PD)
        gr_duino2 = pdJson(gr2PD)
        gr_duino3 = pdJson(gr3PD)
        gr_duino4 = pdJson(gr4PD)
        
        finalData = {"gr_duino1" : gr_duino1 , 
        "gr_duino2" : gr_duino2, 
        "gr_duino3" : gr_duino3, 
        "gr_duino4" : gr_duino4,
        "liveData" : liveData,
        "aggregate" : {"temperature" : aggData['tempMean'], "humidity" : aggData['humMean'], "moisture" : aggData['moistMean'], "light" : aggData['lightMean'], "time" : aggData['time'], "wTemp" : aggData["wTemp"], "wHumidity" : aggData["wHumidity"]},   
        "thermalPerformance" : aggData['thermal'], 
        "humidPerformance" : aggData['humidity'], 
        "hydroPerformance" : aggData['hydro']}
        
        return finalData
    
    grDuinos = nodes()
   
    
    return render_template('index.html', data = grDuinos, content_type = 'application/json')
    
    
@app.route('/overview')
def overview():
    def nodes():
        db = Database()
        gr_duino1 = db.nodeData(1) #pull data for nodes
        gr_duino2 = db.nodeData(2)
        gr_duino3 = db.nodeData(3)
        gr_duino4 = db.nodeData(4)
        
        gr1PD = pd.DataFrame(gr_duino1) #Convert to PD
        gr2PD = pd.DataFrame(gr_duino2)
        gr3PD = pd.DataFrame(gr_duino3)
        gr4PD = pd.DataFrame(gr_duino4)
        
        def liveData(data):
            l = len(data) -1
            temp = data['temperature'][l]
            hum = data['humidity'][l]
            moist = data['moisture'][l]
            light = data['light'][l]
            time = data['time'][l]
            time = str(time.year) + "-" + str(time.month) + "-" + str(time.day) + " " + str(time.hour) + ":" + str(time.minute)
            results = {"temperature" : temp, "humidity": hum, "moisture" : moist, "light" : light, "time" : time}
            return results
            
        gr1Live = liveData(gr1PD)
        gr2Live = liveData(gr2PD)
        gr3Live = liveData(gr3PD)
        gr4Live = liveData(gr4PD)
        
 
        
        def grJSON(grPDs, liveNodes):
            
            lens = [len(grPDs[0]),len(grPDs[1]),len(grPDs[2]),len(grPDs[3])]
                
            if lens[0] != lens[1] and lens[0] != lens[2] and lens[0] != lens[3]: #Checking if node data of same length, if not, take length of shortest dataset
                t = - min(lens)
            else:
                t = -lens[0]
                
            output = {}
            n = 1
            
            for node, live in zip(grPDs, liveNodes):
                
                applyInt = lambda x: int(x)
                temperature = list(map(applyInt, list(node['temperature'].iloc[t:-1])))
                humidity = list(map(applyInt, list(node['humidity'].iloc[t:-1])))
                moisture = list(map(applyInt, list(node['moisture'].iloc[t:-1])))
                light = list(map(applyInt, list(node['light'].iloc[t:-1])))
                timeFix = lambda x : str(x.year) + "-" + str(x.month) + "-" + str(x.day) + " " + str(x.hour) + ":" + str(x.minute)
                time = list(map(timeFix, list(node['time'].iloc[t:-1])))
                grName = "gr_duino" + str(n)
                nodeJson = {"temperature":temperature, "humidity" : humidity, "moisture" : moisture, "light" : light, "time" : time, "liveData": live}
                output[grName] = nodeJson
                n = n + 1
            
            
            return  output
            
        
        nodes = [gr1PD, gr2PD, gr3PD, gr4PD]    
        nodeLive =[gr1Live,gr2Live, gr3Live, gr4Live]
        
        nodeData = grJSON(nodes, nodeLive)
        
        return nodeData
        
    data = nodes()
    return render_template('grOverView.html', data = data, content_type = 'application/json')
  
  
@app.route('/performance')
def performance():
    def nodes():
        db = Database()
        
        grList = db.fullData()
    
        
        wTime = []
        
        roofArea = 4 * 8 #Area of quadrat = area of green roof / 4 = (length * width) / 4
        quadratArea = roofArea/4
        quadratVolume = quadratArea * 0.1 #quadrat volume = quadrat area * substrate depth (10 cm)
        
        def wFormat(grPDs): #Transform weather data to PD and take desired columns : temperature, humidity, precipIntensity and windSpeed
            
            for node in grPDs:
                wData = []
                timeFix = lambda x : str(x.year) + "-" + str(x.month) + "-" + str(x.day) + " " + str(x.hour) + ":" + str(x.minute)
                node['time'] = node['time'].apply(timeFix) 
                node['data'] = node['data'].apply(lambda x: x.replace("'", '"'))
                node['data'] = node['data'].apply(lambda x: x.replace(" u", ""))
                node['data'] = node['data'].apply(lambda x: ast.literal_eval(x))
                wData = list(node['data'])
                wPD = pd.DataFrame(wData)
                wPD['temperature'] = wPD['temperature'].apply(lambda x: (x - 32) * 5/9) # Convert temperature from F to C
                wPD['humidity'] = wPD['humidity'].apply(lambda x: x * 100) 
                node['volumeRetained'] = node['moisture'].apply(lambda x: (x/100) * quadratVolume) #multiply soil moisutre percentage by volume of quadrat
                node['ambTemp'] = wPD['temperature']
                node['ambHumid'] = wPD['humidity']
                node['rain'] = wPD['precipIntensity'].apply(lambda x: (x * quadratArea) / 61023.744) #Divide by 61023.744 to convert cubic inches to cubic metres 
                node['windSpeed'] = wPD['windSpeed']
                node['cloudCover'] = wPD['cloudCover']
                #grPD['time'] = grPD['time'].apply(lambda x: datetime.datetime(x))
                #grPD['time'] = grPD['time'].apply(lambda x: str(x.year) + "-" + str(x.month) + "-" + str(x.day) + " " + str(x.hour) + ":" + str(x.minute)) 
                node = node.drop(['data', 'w.time'], axis = 1)
            
            return grPDs
        
        
        grList = wFormat(grList)    
        
        def listMean(data): #simple function to obtain mean of multiple lists
                mean = list(np.mean(data,axis = 0))
                return mean
            
        def nodePerformance(nodes):
            
            applyInt = lambda x: int(x)
            def basicPerformance(node): #Performance function for thermal and humidity
             
                temperature = list(map(applyInt, list(node['temperature'])))
                humidity = list(map(applyInt, list(node['humidity'])))
                ambTemp = list(map(applyInt, list(node['ambTemp'])))
                ambHumid = list(map(applyInt, list(node['ambHumid'])))
                print(ambTemp)
              
                node['tempDiff'] = list(np.array(temperature) - np.array(ambTemp))
                node['tempDiff%'] = list((np.array(node['tempDiff'])/np.array(ambTemp)) * 100)
                node['humDiff'] = list(np.array(temperature) - np.array(ambTemp))
                node['humDiff%'] = list((np.array(node['humDiff'])/np.array(ambHumid)) * 100)
                
                return node
                
            def hydroPerformance(retentionList, rainList):
                npArr = lambda x: np.array(x)
                totalRain = list(sum(npArr(rainList)))
                totalRetention = list(sum(npArr(retentionList)))
                totalRetention = [0 if np.isnan(x) else x for x in totalRetention]
                rainRatio = list(np.array(totalRetention)/np.array(totalRain))
                rainRatio = [0 if np.isnan(x) else x for x in rainRatio]
                results = {"rainRatio" : rainRatio, "totalRetention" : totalRetention}
                return results
                
            def liveData(data):
                live = {}
                thermalDiff = data['tempDiff'].iloc[-1]
                thermalPerc  = data['tempDiff'].iloc[-1]
                humidDiff  = data['humDiff'].iloc[-1]
                humidPerc = data['humDiff%'].iloc[-1] 
                time = data['time'].iloc[-1]
           
                live["tempDiff"] = thermalDiff
                live["tempPerc"] = thermalPerc
                live["humidDiff"] = humidDiff 
                live["humidPerc"] = humidPerc
                live["time"] = time
              
                return live
                    
                
            output = {}
            n = 1
            thermalList = []
            humidList = []
            thermPercList =[]
            humPercList = []
            
            for node in nodes:
                node = basicPerformance(node)
                thermalDiff = list(map(applyInt, list(node['tempDiff'])))
                thermalPerc = list(map(applyInt, list(node['tempDiff%'])))
                humidDiff = list(map(applyInt, list(node['humDiff'])))
                humidPerc = list(map(applyInt, list(node['humDiff%'])))
                time = list(node['time'])
            
                live = liveData(node)
                nodeName = "gr_duino" + str(n)
                output[nodeName] = {"tempDiff" : thermalDiff, "tempDiff%": thermalPerc , "humidDiff" : humidDiff, "humdDiff%" : humidPerc, "time" : time, "liveData" : live}
                
                thermalList.append(np.array(thermalDiff))
                humidList.append(np.array(humidDiff))
                thermPercList.append(np.array(thermalPerc))
                humPercList.append(np.array(humidPerc))
                n = n + 1
            
            thermAgg = listMean(thermalList)
            humidAgg = listMean(humidList)
            tPercAgg = listMean(thermPercList)
            hPercAgg = listMean(humPercList)
            
            
            
            output['aggPerformance'] = {"thermal" : thermAgg, "humidity" : humidAgg, "thermalPerc": tPercAgg, "humidPerc" : hPercAgg}
                
        
    
            def thermalPerformance(grList): #Calculation of energy balance model components, radiation data oobtained from NASA POWER API
                node1 = grList[0]
                node2 = grList[1]
                node3 = grList[2]
                node4 = grList[3]
                time = list(node1['time'])
                d1 = time[0]
                d2 = time[-1]
                #Check if if month or date doesn't have a preceeding zero
                def timeFormat(d):
                    if len(str(d.month)) == 1 or len(str(d.day))== 1:
                        if len(str(d.month)) == 1:
                            m = str(0) + str(d.month)
                        else: m = str(d.month) 
                        
                        if len(str(d.day)) == 1:
                            dy = str(0) + str(d.day)
                        else: dy = str(d.day)
                    date = str(d.year) + m + dy
                    return date
                    
                    
                    
                #date1 = timeFormat(d1)
                #date2 = timeFormat(d2)
                #print("dates: ", date1, ", ", date2)
                #Request radiation date from NASA POWER API
                #url = "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?request=execute&identifier=SinglePoint&parameters=ALLSKY_SFC_SW_DWN&startDate=" + date1 + "&endDate=" + date2 + "&userCommunity=SSE&tempAverage=DAILY&outputList=JSON,ASCII&lat=51.524775&lon=-0.132332&user=anonymous"
                #url = "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?request=execute&identifier=Global&parameters=T2M,ALLSKY_SFC_SW_DWN,PS&userCommunity=SSE&tempAverage=CLIMATOLOGY&outputList=JSON&user=anonymous"
                #req = requests.get(url)
                #status = req.status_code
                #print("NASA API STAT: " , status)
                #data = req.json()
                #data = data['features']
                #nasa = json_normalize(data)
                #nasa = nasa.transpose()
                #print(nasa)
                
                #Iterate Over nodes and calculate their Sensible Heat Flux and Rate of Evaporation
                #Sensible Heat Flux 
                def Qsensible(nodeList):
                    Ca = 1.005 #Atmosperic Heat Capacity (W/m2)
                    Lv = 2.2 #Latent Heat of Vaporization (J/kg)
                    k = 1.4 #Von Karman's Constant
                    z = 20  #Vertical Reference Height for wind speed and temperature measurements
                    results = {}
                    for node in nodeList:
                        U = list(map(applyInt, list(node['windSpeed'])))   #Horizontal Wind Speed
                        T = list(map(applyInt, list(node['tempDiff']))) #Temperature
                        H = list(map(applyInt,list(node['humDiff']))) #Humidity
                       
                        Qsensible = []
                        Qlatent = []
                        n = 1
                        name = "gr_duino" + str(n)
                        QsMean = []
                        QlMean = []
                        
                        for t,u in zip(T,U): #Calulate sensible heat flux
                            Qs = -Ca * (z**2) * (k**2) *((u/z) * (t/z))
                            Qsensible.append(Qs)
                        
                        QsMean.append(np.array(list(Qsensible)))
                   
                        for h,u in zip(H, U): #Calculate vaporization rate
                            Ql = -Lv * (z**2) * (k**2) *((u/z) * (h/z))
                            Qlatent.append(Ql)
                        
                        QlMean.append(np.array(list(Qlatent)))
                         
                         
                        results[name] = {"Qsensible" : Qsensible, "Qlatent": Qlatent}
                        print(results)
                        n = n + 1
                        
                    QsMean = listMean(QsMean)
                    QlMean = listMean(QlMean)
                    results["Aggregate"] = {"Qsensible" : QsMean, "Qlatent" : Qlatent}
                    
                    return results
                        
                output["thermalPerformance"] = Qsensible(grList)
                
                return output
                
            output = thermalPerformance(grList)
            
            return output
            
        nodePerformance = nodePerformance(grList)   
        
        return nodePerformance
        
   
    data = nodes()
    
    
    return render_template('performance.html', data = data, content_type = 'application/json')
    

@app.route("/data", methods = ["GET"])
def getData():
    def jsonData():
        db = Database()
        data = db.jsonOutput()
        return jsonify(data)
        
    
    jsonData = jsonData()
    return jsonData
  

app.run()

