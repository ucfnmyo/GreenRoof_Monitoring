
//Temperature HighChart
Highcharts.chart('tempChart', {

  title: {
      text: 'Historical Temperature Performance'
  },
  yAxis: {
      title: {
          text: 'Temperature'
      }
  },
  xAxis: {
      title: {
          text: 'Time'
      }
  },
  legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
  },

  plotOptions: {
      series: {
          label: {
              connectorAllowed: false
          },

      }
  },

  series: [{
      name: 'Quadrat 1',
      data: temperature
  }, {
      name: 'Quadrat 2',
      data: temperature
  }, {
      name: 'Quadrat 3',
      data: temperature
  }, {
      name: 'Quadrat 4',
      data: temperature
  }, {
      name: 'Quadrat 5',
      data: temperature
  },{
      name: 'Quadrat 6',
      data: temperature
  },{
      name: 'Quadrat 7',
      data: temperature
  }],

  responsive: {
      rules: [{
          condition: {
              maxWidth: 500
          },
          chartOptions: {
              legend: {
                  layout: 'horizontal',
                  align: 'center',
                  verticalAlign: 'bottom'
              }
          }
      }]
  }

});


//Humidity HighChart
Highcharts.chart('humidChart', {

  title: {
      text: 'Historical Humidity Performance'
  },
  yAxis: {
      title: {
          text: 'Relative Humidity (%) '
      }
  },
  xAxis: {
      title: {
          text: 'Time'
      }
  },
  legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
  },

  plotOptions: {
      series: {
          label: {
              connectorAllowed: false
          },
          pointStart: 2010
      }
  },

  series: [{
      name: 'Quadrat 1',
      data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
  }, {
      name: 'Quadrat 2',
      data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
  }, {
      name: 'Quadrat 3',
      data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
  }, {
      name: 'Quadrat 4',
      data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
  }, {
      name: 'Quadrat 5',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  },{
      name: 'Quadrat 6',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  },{
      name: 'Quadrat 7',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  }],

  responsive: {
      rules: [{
          condition: {
              maxWidth: 500
          },
          chartOptions: {
              legend: {
                  layout: 'horizontal',
                  align: 'center',
                  verticalAlign: 'bottom'
              }
          }
      }]
  }

});


//Soil Moisture HighChart
Highcharts.chart('soilChart', {

  title: {
      text: 'Historical Soil Moisture Performance'
  },
  yAxis: {
      title: {
          text: 'Soil Moisture (%)'
      }
  },
  xAxis: {
      title: {
          text: 'Time'
      }
  },
  legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
  },

  plotOptions: {
      series: {
          label: {
              connectorAllowed: false
          },
          pointStart: 2010
      }
  },

  series: [{
      name: 'Quadrat 1',
      data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
  }, {
      name: 'Quadrat 2',
      data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
  }, {
      name: 'Quadrat 3',
      data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
  }, {
      name: 'Quadrat 4',
      data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
  }, {
      name: 'Quadrat 5',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  },{
      name: 'Quadrat 6',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  },{
      name: 'Quadrat 7',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  }],

  responsive: {
      rules: [{
          condition: {
              maxWidth: 500
          },
          chartOptions: {
              legend: {
                  layout: 'horizontal',
                  align: 'center',
                  verticalAlign: 'bottom'
              }
          }
      }]
  }

});


//Temperature HighChart
Highcharts.chart('lightChart', {

  title: {
      text: 'Historical Light Exposure'
  },
  yAxis: {
      title: {
          text: 'Light Intensity (Lumens)'
      }
  },
  xAxis: {
      title: {
          text: 'Time'
      }
  },
  legend: {
      layout: 'vertical',
      align: 'right',
      verticalAlign: 'middle'
  },

  plotOptions: {
      series: {
          label: {
              connectorAllowed: false
          },
          pointStart: 2010
      }
  },

  series: [{
      name: 'Quadrat 1',
      data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
  }, {
      name: 'Quadrat 2',
      data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
  }, {
      name: 'Quadrat 3',
      data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
  }, {
      name: 'Quadrat 4',
      data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
  }, {
      name: 'Quadrat 5',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  },{
      name: 'Quadrat 6',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  },{
      name: 'Quadrat 7',
      data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
  }],

  responsive: {
      rules: [{
          condition: {
              maxWidth: 500
          },
          chartOptions: {
              legend: {
                  layout: 'horizontal',
                  align: 'center',
                  verticalAlign: 'bottom'
              }
          }
      }]
  }

});
