import requests
import time
import datetime
import ttn
import mysql.connector
from dateutil.parser import parse
import json

app_id = "sc_greenroof"
access_key = "ttn-account-v2.-IHcBhSVIOOObrIuGkUf4TaTA3thVVLul4vIsxTIgVM"

def uplink_callback(msg, client):
  print "Received uplink from: "
  print msg.dev_id
  print msg.app_id
  print msg.payload_fields
  print msg.metadata.time

  dt = parse(msg.metadata.time)
  year = int(dt.strftime("%Y"))
  month = int(dt.strftime("%m"))
  day = int(dt.strftime("%d"))
  hour = int(dt.strftime("%H"))
  min = int(dt.strftime("%M"))
  sec = int(dt.strftime("%S"))
  unixtime = datetime.datetime(year, month, day, hour, 0, 0)
  unixtime = int(time.mktime(unixtime.timetuple()))
  print "UNIX TIME: "
  print unixtime

  dt = dt.strftime("%Y-%m-%d  %H:%M:%S")

  print dt

 #WeatherAPI data using corresponding unix timestamp

  url = "https://api.darksky.net/forecast/01d988e604cc11c79bef4df39bbd4210/51.524775,-0.132332," + str(unixtime)


  weatherRequest = requests.get(url)
  status = weatherRequest.status_code
  print "WeatherAPI Status Code: "
  print status

  json = weatherRequest.json()
  weatherData = json["hourly"]
  weatherData = weatherData["data"]

  for i in range(0, len(weatherData)):
    if weatherData[i]["time"] == unixtime:
       wData = weatherData[i]

  print wData

  #SQL DB connection - insert uplink data and weather api data to respective tables
  try:
  	mydb = mysql.connector.connect(
  		host="localhost",
  		user="ttn",
  		password="ttn2019",
  		database="scGreenRoof"
  		)

  	mycursor = mydb.cursor()

  	sql = "INSERT INTO GR_DATA (dev_id, temperature, humidity, moisture, light, time) VALUES (%s, %s, %s, %s, %s, %s)"
	val = (str(msg.dev_id), (msg.payload_fields.temperature),str(msg.payload_fields.humidity), str(msg.payload_fields.soilMoisture), str(msg.payload_fields.light), str(dt))
	print val
  	result = mycursor.execute(sql,val)
  	mydb.commit()
  	print "Record inserted:"
  	print mycursor.rowcount

	#weather data sql insert *note _w suffix corresponds to weather data variables
	sql_w = "INSERT INTO weatherData (data, time) VALUES (%s, %s)"
	val_w = (str(wData), str(dt))
        result_w = mycursor.execute(sql_w, val_w)
	mydb.commit()
	print "Weather Data Inserted:"
	print mycursor.rowcount

  except mysql.connector.Error as error :
  	mydb.rollback()
  	print("Failed to insert into MySQL table {}".format(error))

  finally:
  	if(mydb.is_connected()):
  		mycursor.close()
  		mydb.close()
  		print("MySQL connection closed")


def connect_callback(res, client):
  print "Connection to broker: "
  print res

def close_callback(res, client):
  print "Trying to reconnect"
  mqtt_client.connect()

# handlerclient class constructor
handler = ttn.HandlerClient(app_id, access_key)
print "Handler initialised"

# using mqtt client create an MQTTClient object
mqtt_client = handler.data()
print "MQTT client object created"

# set a connection callback function when client connects to broker
mqtt_client.set_connect_callback(connect_callback)

# set close_callback so that if connection lost we can reconect
mqtt_client.set_close_callback(close_callback)

# set uplink callback to be executed when message arrives
mqtt_client.set_uplink_callback(uplink_callback)
print "Callbacks assigned"

# connect to the application and listen for messages
mqtt_client.connect()

# keep program running - if connection lost should reconnect
while True:
  pass
