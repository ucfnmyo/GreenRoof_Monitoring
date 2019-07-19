
var temperature = [];
var humidity = [];
var moisture = [];
var light = [];
var timeRaw = [];
var time = [];
var data = {"temperature" : temperature, "humidity" : humidity, "soilMoisture" : moisture,"light" : light, "time" : time, "timeRaw" : timeRaw};
var nDays = [];
var n;

formatJSON();
getWeatherData();
console.log(data);
//Retrieve initial json from server (or local) and push reformat data to JSON with arrays
function formatJSON(){

$.getJSON('data.json', function(json){
  for (var i = 0; i < json.length; i++){
    temperature.push(json[i].temperature);
    humidity.push(json[i].humidity);
    moisture.push(json[i].soilMoisture);
    light.push(json[i].light);
    timeRaw.push(json[i].time);
  }

  var t = temperature.length - 1;
  document.getElementById('temp').innerHTML = temperature[t] + " C";

  var h = humidity.length - 1;
  document.getElementById('humidity').innerHTML = humidity[h] + " %";

  var m = moisture.length - 1;
  document.getElementById('soilM').innerHTML = moisture[m] + " %";

  var l = light.length - 1;
  document.getElementById('light').innerHTML = light[l] + ' lumens';

  formatDates(timeRaw); //Reformat time data to DD/MM/YY, HH:MM

  document.getElementById('time').innerHTML = time[t];
  document.getElementById('time1').innerHTML = time[h];
  document.getElementById('time2').innerHTML = time[m];
  document.getElementById('time3').innerHTML = time[l];

});

};
//Function to get the latest time period in the format DD/MM/YYYY, hours:minutes
function formatDates(dates){

  for(var i = 0; i < dates.length; i++){
    var dateRaw = new Date(dates[i]);
    var minutes = dateRaw.getMinutes();
    if (minutes.toString().length == 1){
      minutes = "0" + minutes;
    }
    var month = dateRaw.getMonth() + 1
    var day = dateRaw.getFullYear() + "-" + month + "-" + dateRaw.getDate();
    nDays.push(day);
    var timestamp = dateRaw.getDate() + "-" + month + "-" + dateRaw.getFullYear() + ", " + dateRaw.getHours() + ":" + minutes;
    time.push(timestamp);

  }
  nDays = [...new Set(nDays)];


}

updateData();
showData();
//Check the length of the latest arrays and update dashboard if they exceed the initial length
function updateData(){
  var temp = [];
  var humid = [];
  var luminance = [];
  var soilM = [];
  var clock = [];
  //populate local arrays for later comparison with global arrays
  $.getJSON('data.json', function(json){
    for (var i = 0; i < json.length; i++){
      temp.push(json[i].temperature);
      humid.push(json[i].humidity);
      soilM.push(json[i].soilMoisture);
      luminance.push(json[i].light);
      clock.push(json[i].time);
    }


  });
  //update global array if local array is longer.
  if (temperature.length < temp.length){
    temperature = temp;
  }
  if (humidity.length < humid.length){
    humidity = humid;
  }
  if (light.length < luminance.length){
    light = luminance;
  }
  if (moisture.length < soilM.length){
    moisture = soilM;
  }
  if (time.length < clock.length){
      time = clock;
  }


}

function showData(){

  //update global array if local array is longer.
  if (temperature.length != 0){
    var t = temperature.length
    console.log(temperature[t]);
    document.getElementById('temp').value = temperature[t];
  }
  if (humidity.length != 0){
    humidity = humid;
  }
  if (light.length != 0){
    light = luminance;
  }
  if (moisture.length != 0){
    moisture = soilM;
  }
  if (time.length != 0){
      time = clock;
  }
}

function getWeatherData(){
  //Pull weather data from Dark Sky API, Key :
  //Lat lon coords for bloomsbury weather station
  var lat = 51.524775;
  var lon = -0.132332;
  var timeRange = [];
  var weatherData = {};
  //Wait for data to load then generate time range in UNIX format for Weather API Call.
  window.addEventListener('load', (event) => {
    for (var i = 0; i < nDays.length; i++){
      var date = new Date(nDays[i]);
      var month = date.getMonth() + 1
      var unix = new Date(Date.UTC(date.getFullYear(), month, date.getDate(), 0, 0, 0))
      var secs = unix.getTime() / 1000;
      timeRange.push(secs);
      console.log(timeRange);
    }

    var tempAPI = [];
    var humidAPI = [];
    var rainfallAPI = [];
    var dewpointAPI = [];
    var windBearingAPI = [];
    var windSpeedAPI = [];
    var pressureAPI = [];
    //Iterate Over TimeRange and retrieve weather API data for corresponding days
    for(var i = 0; i < timeRange.length; i++){
      var url = 'https://api.darksky.net/forecast/01d988e604cc11c79bef4df39bbd4210/' + lat + "," + lon + "," + timeRange[i];
      console.log(timeRange[i]);
      fetch(url).then((resp) => resp.text()).then((body) => {
        var json = JSON.parse(body);
        console.log(json)
        var hourlyData = json.hourly.data;
        console.log(hourlyData)
        for (var i = 0; i < hourlyData.length; i++){
          var dateObj = new Date(hourlyData[i].time * 1000);
          var month = dateObj.getMonth() + 1
          var date = dateObj.getFullYear() + "-" + month + "-" + dateObj.getDate()+ ", " + dateObj.getHours() + ":" + "00";
          //console.log(date)
          var temp = (hourlyData[i].apparentTemperature - 32) * 5/9; //convert Farenheit to Celcius
          var humidity = hourlyData[i].humidity;
          var rainfall = hourlyData[i].precipIntensity;
          var dewPoint = hourlyData[i].dewPoint;
          var windBearing = hourlyData[i].windBearing;
          var windSpeed = hourlyData[i].windSpeed;
          var pressure = hourlyData[i].pressure;
          //Find matches between the time series within Green roof data set and append weather data for correspondong 1-hour time slots
          for (var j = 0; j < timeRaw.length; j++){
            var stamp = timeRaw[j]
            var timeStamp = new Date(stamp);
            var month1 = timeStamp.getMonth() + 1
            //console.log(timeStamp.getFullYear() + " : " + dateObj.getFullYear() + " Y " + month1 + ":" + dateObj.getMonth() + " M " + timeStamp.getDate() + ":" + dateObj.getDate() + " D " + timeStamp.getHours())
            if(timeStamp.getFullYear() === dateObj.getFullYear() && month1 === dateObj.getMonth() && timeStamp.getDate() === dateObj.getDate() && timeStamp.getHours() === dateObj.getHours()){
              tempAPI.push(temp);
              humidAPI.push(humidity);
              rainfallAPI.push(rainfall);
              dewpointAPI.push(dewPoint);
              windBearingAPI.push(windBearing);
              windSpeedAPI.push(windSpeed);
              pressureAPI.push(pressure);

            }

          }
        }

      });
    }
    //Return weather data to master dataset
    data['ambTemperature'] = humidAPI;
    data['ambHumidity'] = tempAPI;
    data['rainfall'] = rainfallAPI;
    data['dewpoint'] = dewpointAPI;
    data['windBearing'] = windBearingAPI;
    data['windSpeed'] = windSpeedAPI;
    data['pressure'] = pressureAPI;
  });
};

//Using Ajax send json to python
window.addEventListener('load',  (event) => {

 $.ajax({
      type:'get',
      url:'/json_io.py',
      cache:false,
      async:'asynchronous',
      dataType:'json',
      success: function(data) {
        console.log(JSON.stringify(data))
      },
      error: function(request, status, error) {
        console.log("Error: " + error)
      }
   });

});


//Wait for page to load then send data to highcharts
window.addEventListener('load', (event) => {

  //Aggregate Humidity Chart
  Highcharts.chart('aggTemp', {
      chart: {
          type: 'line'
      },
      title: {
          text: 'Historical Thermal Performance'
      },
      subtitle: {
          text: 'Source: WorldClimate.com'
      },
      xAxis: {
          categories: data.time
      },
      yAxis: {
          title: {
              text: 'Temperature (°C)'
          }
      },
      plotOptions: {
          line: {
              dataLabels: {
                  enabled: false
              },
              enableMouseTracking: true
          }
      },
      series: [{
          name: 'Temperature',
          data: data.temperature
      }, {
          name: 'Ambient Temperature',
          data: data.ambTemperature
      } ]
  });

  //Aggregate Humidity Chart
  Highcharts.chart('aggHumid', {
      chart: {
          type: 'line'
      },
      title: {
          text: 'Historical Evapotranspiration'
      },
      subtitle: {
          text: 'Source: WorldClimate.com'
      },
      xAxis: {
          categories: data.time,
          tickInterval: 24 * 3600 * 1000
      },
      yAxis: {
          title: {
              text: 'Relative Humidity (%)'
          }
      },
      plotOptions: {
          line: {
              dataLabels: {
                  enabled: false
              },
              enableMouseTracking: true
          }
      },
      series: [{
          name: 'Relative Humidity',
          data: data.humidity
      }, ]
  });

  //Aggregate Soil Moisture Chart
  Highcharts.chart('aggSoil', {
      chart: {
          type: 'line'
      },
      title: {
          text: 'Historical Hydrological Performance'
      },
      subtitle: {
          text: 'Source: WorldClimate.com'
      },
      xAxis: {
          categories: data.time
      },
      yAxis: {
          title: {
              text: 'Soil Moisture (%)'
          }
      },
      plotOptions: {
          line: {
              dataLabels: {
                  enabled: false
              },
              enableMouseTracking: true
          }
      },
      series: [{
          name: 'Soil Moisture',
          data: data.soilMoisture
      }, ]
  });

  //Aggregate Light Chart
  Highcharts.chart('aggLight', {
      chart: {
          type: 'line'
      },
      title: {
          text: 'Historical Light Exposure'
      },
      subtitle: {
          text: 'Source: WorldClimate.com'
      },
      xAxis: {
          categories: data.time
      },
      yAxis: {
          title: {
              text: 'Light Intensity (lumens)'
          }
      },
      plotOptions: {
          line: {
              dataLabels: {
                  enabled: false
              },
              enableMouseTracking: true
          }
      },
      series: [{
          name: 'Light Intensity',
          data: data.light
      }, ]
  });

});
