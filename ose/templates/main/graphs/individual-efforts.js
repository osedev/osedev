new Chart(document.getElementById("{{ element_id }}").getContext('2d'), {
    type: 'line',
    options: {
        legend: {
            display: true
        },
        title: {
            display:true,
            text:'OSE Individual Development Effort'
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
        datasets: [
        //{% for user in data %}
        {
            label: "{{ user.name }}",
            borderColor: "{{ user.color }}",
            data: [
                //{% for point in user.data %}
                    "{{ point.hours }}",
                //{% endfor %}
            ]
        },
        //{% endfor %}
        ]
    }
});
