<script>

    var labels = {{ content_data.date_list.date|tojson }};
    var data = parseTime({{ content_data.time_list.time|tojson }});
    Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",' +
            'Arial,sans-serif';
    Chart.defaults.global.defaultFontColor = '#292b2c';

    function parseTime(times) {
        let parsedTime = []
        for (let x = 0; x < times.length; x++) {
            let words = times[x].split(':')
            parsedTime.push(
                parseInt(words[0] * 3600) + parseInt(words[1]) * 60 + parseInt(words[2])
            )
        }
        return parsedTime
    }

    // Area Chart Example
    var ctx = document.getElementById("myAreaChart");
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Sessions",
                    lineTension: 0.3,
                    backgroundColor: "rgba(2,117,216,0.2)",
                    borderColor: "rgba(2,117,216,1)",
                    pointRadius: 5,
                    pointBackgroundColor: "rgba(2,117,216,1)",
                    pointBorderColor: "rgba(255,255,255,0.8)",
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "rgba(2,117,216,1)",
                    pointHitRadius: 50,
                    pointBorderWidth: 2,
                    data: data
                }
            ]
        },
        options: {
                
            tooltips: {
                callbacks: {
                    label: function (tooltipItem, data) {
                        let value = parseInt(tooltipItem.value)
                        return
                        // return Math.floor(value/3600)+":"+ Math.floor( (value%3600)/60)+":"+
                        // ((value%3600)%60)%60
                    }
                    /*
                                              ,
                                              title: function(tooltipItem, data){
                                                let label = tooltipItem[0].label
                                                console.log(label)
                                                console.log(moment(label).format('DD.MM.YYYY'))
                                                return moment(label).format('DD.MM.YYYY')
                                              }*/
                },
                displayColors: false
            },
            /*
                                        tooltips: {
                                            callbacks: {
                                              label: function(tooltipItem, data){
                                                let value = parseInt(tooltipItem.value)

                                                if (value%60 < 10)
                                                  return Math.floor(value/60) + ":" + 0 + value%60
                                                else
                                                  return Math.floor(value/60) + ":" + value%60
                                              },
                                              title: function(tooltipItem, data){
                                                let label = tooltipItem[0].label
                                                console.log(label)
                                                console.log(moment(label).format('DD.MM.YYYY'))
                                                return moment(label).format('DD.MM.YYYY')
                                              }
                                            },
                                            displayColors: false
                                        },*/
            scales: {
                xAxes: [
                    {
                        time: {
                            unit: 'date'
                        },
                        gridLines: {
                            display: false
                        },
                        ticks: {
                            //maxTicksLimit: 7
                            precision: 0
                        }
                    }
                ],
                yAxes: [
                    {
                        time: {
                            unit: 'second',
                            displayFormats: {
                                hour: 'HH:mm:ss'
                            }
                        },
                        ticks: {
                            //min: 0, max: 1000, maxTicksLimit: 5,
                            precision: 0,
                            callback: function (value, index, values) {
                                /*
                                                            if( value%3600 < 100){
                                                                return Math.floor(value/3600)+":"+ Math.floor(value/60) + ":" + 0 + value%60
                                                            }
                                                            else if (value%60 < 10) //초
                                                              return Math.floor(value/60) + ":" + 0 + value%60
                                                            else
                                                              return Math.floor(value/60) + ":" + value%60
                                                              */
                                return Math.floor(value / 3600) + ":" + Math.floor((value % 3600) / 60) + ":" + (
                                    (value % 3600) % 60
                                ) % 60
                            }
                        },
                        gridLines: {
                            color: "rgba(0, 0, 0, .125)"
                        }
                    }
                ]
            },
            legend: {
                display: false
            }
        }
    });
</script>