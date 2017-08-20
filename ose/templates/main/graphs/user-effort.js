new Chart(document.getElementById("{{ element_id }}").getContext('2d'), {
    type: 'line',
    options: {
        title:{
            display:true,
            text:"Level of Effort for {{ user_name }}"
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: "{{ period_label }}"
                }
            }],
            yAxes: [{
                ticks: {
                    min: 0
                }
            }]
        }
    },
    data: {
        labels: [
            //{% for label in labels %}
                "{{ label }}",
            //{% endfor %}
        ],
        datasets: [{
            label: "Hours",
            borderColor: 'rgb(220, 57, 18)',
            backgroundColor: 'rgba(220, 57, 18, 0.3)',
            data: [
                //{% for point in data %}
                    "{{ point.hours }}",
                //{% endfor %}
            ]
        }]
    }
});
