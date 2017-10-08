new Chart(document.getElementById("{{ element_id }}").getContext('2d'), {
    type: 'line',
    options: {
        title:{
            display:true,
            text:"Burn Down Chart for {{ product.name }}"
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
                    min: 0,
                    max: 100
                }
            }]
        },
        //{% if graph.height %}
        maintainAspectRatio: false
        //{% endif %}
    },
    data: {
        labels: [
            //{% for label in labels %}
                "{{ label }}",
            //{% endfor %}
        ],
        datasets: [{
            label: "Remaining",
            borderColor: 'rgb(220, 57, 18)',
            backgroundColor: 'rgba(220, 57, 18, 0.3)',
            data: [
                //{% for point in data %}
                    "{{ point.remaining }}",
                //{% endfor %}
            ]
        }]
    }
});
