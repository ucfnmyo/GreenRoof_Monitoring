
var temperature = [];
var humidity = [];
var moisture = [];
var light = [];
var timeRaw = [];
var time = [];
var data = {};

//Retrieve initial json from server (or local) and push reformat data to JSON with arrays
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

  var h = humidity.length - 1 ;
  document.getElementById('humidity').innerHTML = humidity[h] + " %";

  var m = moisture.length - 1;
  document.getElementById('soilM').innerHTML = moisture[m] + " %";

  var l = light.length - 1;
  document.getElementById('light').innerHTML = light[l] + ' lumens';

  formatDates(timeRaw);

  data.push("temperature" : temperature,
  "humidity" : humidity,
  "soilMoisture" : moisture,
  "light" : light,
  "time" : time)

  console.log(data);
});
console.log(temperature);
//Function to get the latest time period in the format DD/MM/YYYY, hours:minutes
function formatDates(dates){

  for(var i = 0; i < dates.length; i++){
    var dateRaw = new Date(dates[i]);
    var minutes = dateRaw.getMinutes();
    if (minutes.toString().length == 1){
      minutes = minutes + "0"
    }
    var date = dateRaw.getDate() + "/" + dateRaw.getMonth() + "/" + dateRaw.getFullYear() + ", " + dateRaw.getHours() + ":" + minutes;
    time.push(date);
  }

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

//Aggregate Temperature Chart
Highcharts.chart('aggTemp', {

    chart: {
        scrollablePlotArea: {
            minWidth: 700
        }
    },

    data: {
        csvURL: 'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/analytics.csv',
        beforeParse: function (csv) {
            return csv.replace(/\n\n/g, '\n');
        }
    },

    title: {
        text: 'Aggregate Temperature Performance'
    },

    subtitle: {
        text: 'Source: Google Analytics'
    },

    xAxis: {
        tickInterval: 7 * 24 * 3600 * 1000, // one week
        tickWidth: 0,
        gridLineWidth: 1,
        labels: {
            align: 'left',
            x: 3,
            y: -3
        }
    },

    yAxis: [{ // left y axis
        title: {
            text: null
        },
        labels: {
            align: 'left',
            x: 3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }, { // right y axis
        linkedTo: 0,
        gridLineWidth: 0,
        opposite: true,
        title: {
            text: null
        },
        labels: {
            align: 'right',
            x: -3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }],

    legend: {
        align: 'left',
        verticalAlign: 'top',
        borderWidth: 0
    },

    tooltip: {
        shared: true,
        crosshairs: true
    },

    plotOptions: {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        hs.htmlExpand(null, {
                            pageOrigin: {
                                x: e.pageX || e.clientX,
                                y: e.pageY || e.clientY
                            },
                            headingText: this.series.name,
                            maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) + ':<br/> ' +
                                this.y + ' sessions',
                            width: 200
                        });
                    }
                }
            },
            marker: {
                lineWidth: 1
            }
        }
    },

    series: [{
        name: 'All sessions',
        lineWidth: 4,
        marker: {
            radius: 4
        }
    }, {
        name: 'New users'
    }]
});

//Aggregate Humidity Chart
Highcharts.chart('aggHumid', {

    chart: {
        scrollablePlotArea: {
            minWidth: 700
        }
    },

    data: {
        csvURL: 'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/analytics.csv',
        beforeParse: function (csv) {
            return csv.replace(/\n\n/g, '\n');
        }
    },

    title: {
        text: 'Aggregate Temperature Performance'
    },

    subtitle: {
        text: 'Source: Google Analytics'
    },

    xAxis: {
        tickInterval: 7 * 24 * 3600 * 1000, // one week
        tickWidth: 0,
        gridLineWidth: 1,
        labels: {
            align: 'left',
            x: 3,
            y: -3
        }
    },

    yAxis: [{ // left y axis
        title: {
            text: null
        },
        labels: {
            align: 'left',
            x: 3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }, { // right y axis
        linkedTo: 0,
        gridLineWidth: 0,
        opposite: true,
        title: {
            text: null
        },
        labels: {
            align: 'right',
            x: -3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }],

    legend: {
        align: 'left',
        verticalAlign: 'top',
        borderWidth: 0
    },

    tooltip: {
        shared: true,
        crosshairs: true
    },

    plotOptions: {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        hs.htmlExpand(null, {
                            pageOrigin: {
                                x: e.pageX || e.clientX,
                                y: e.pageY || e.clientY
                            },
                            headingText: this.series.name,
                            maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) + ':<br/> ' +
                                this.y + ' sessions',
                            width: 200
                        });
                    }
                }
            },
            marker: {
                lineWidth: 1
            }
        }
    },

    series: [{
        name: 'All sessions',
        lineWidth: 4,
        marker: {
            radius: 4
        }
    }, {
        name: 'New users'
    }]
});

//Aggregate Soil Moisture Chart
Highcharts.chart('aggSoil', {

    chart: {
        scrollablePlotArea: {
            minWidth: 700
        }
    },

    data: {
        csvURL: 'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/analytics.csv',
        beforeParse: function (csv) {
            return csv.replace(/\n\n/g, '\n');
        }
    },

    title: {
        text: 'Aggregate Temperature Performance'
    },

    subtitle: {
        text: 'Source: Google Analytics'
    },

    xAxis: {
        tickInterval: 7 * 24 * 3600 * 1000, // one week
        tickWidth: 0,
        gridLineWidth: 1,
        labels: {
            align: 'left',
            x: 3,
            y: -3
        }
    },

    yAxis: [{ // left y axis
        title: {
            text: null
        },
        labels: {
            align: 'left',
            x: 3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }, { // right y axis
        linkedTo: 0,
        gridLineWidth: 0,
        opposite: true,
        title: {
            text: null
        },
        labels: {
            align: 'right',
            x: -3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }],

    legend: {
        align: 'left',
        verticalAlign: 'top',
        borderWidth: 0
    },

    tooltip: {
        shared: true,
        crosshairs: true
    },

    plotOptions: {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        hs.htmlExpand(null, {
                            pageOrigin: {
                                x: e.pageX || e.clientX,
                                y: e.pageY || e.clientY
                            },
                            headingText: this.series.name,
                            maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) + ':<br/> ' +
                                this.y + ' sessions',
                            width: 200
                        });
                    }
                }
            },
            marker: {
                lineWidth: 1
            }
        }
    },

    series: [{
        name: 'All sessions',
        lineWidth: 4,
        marker: {
            radius: 4
        }
    }, {
        name: 'New users'
    }]
});

//Aggregate Light Chart
Highcharts.chart('aggLight', {

    chart: {
        scrollablePlotArea: {
            minWidth: 700
        }
    },

    data: {
        csvURL: 'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/analytics.csv',
        beforeParse: function (csv) {
            return csv.replace(/\n\n/g, '\n');
        }
    },

    title: {
        text: 'Aggregate Temperature Performance'
    },

    subtitle: {
        text: 'Source: Google Analytics'
    },

    xAxis: {
        tickInterval: 7 * 24 * 3600 * 1000, // one week
        tickWidth: 0,
        gridLineWidth: 1,
        labels: {
            align: 'left',
            x: 3,
            y: -3
        }
    },

    yAxis: [{ // left y axis
        title: {
            text: null
        },
        labels: {
            align: 'left',
            x: 3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }, { // right y axis
        linkedTo: 0,
        gridLineWidth: 0,
        opposite: true,
        title: {
            text: null
        },
        labels: {
            align: 'right',
            x: -3,
            y: 16,
            format: '{value:.,0f}'
        },
        showFirstLabel: false
    }],

    legend: {
        align: 'left',
        verticalAlign: 'top',
        borderWidth: 0
    },

    tooltip: {
        shared: true,
        crosshairs: true
    },

    plotOptions: {
        series: {
            cursor: 'pointer',
            point: {
                events: {
                    click: function (e) {
                        hs.htmlExpand(null, {
                            pageOrigin: {
                                x: e.pageX || e.clientX,
                                y: e.pageY || e.clientY
                            },
                            headingText: this.series.name,
                            maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) + ':<br/> ' +
                                this.y + ' sessions',
                            width: 200
                        });
                    }
                }
            },
            marker: {
                lineWidth: 1
            }
        }
    },

    series: [{
        name: 'All sessions',
        lineWidth: 4,
        marker: {
            radius: 4
        }
    }, {
        name: 'New users'
    }]
});
