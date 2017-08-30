var chartColors = {
    hours: 'rgb(220, 57, 18)',
    hours_fill: 'rgba(220, 57, 18, 0.3)',
    devs: 'rgb(51, 102, 204)',
    devs_fill: 'rgba(51, 102, 204, 0.3)'
};
new Chart(document.getElementById("{{ element_id }}").getContext('2d'), {
    type: 'line',
    options: {
        title:{
            display:true,
            text:'OSE Active Developers and Development Effort'
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
            label: "Hours/10",
            borderColor: chartColors.hours,
            backgroundColor: chartColors.hours_fill,
            data: [
                //{% for point in data %}
                    '{% widthratio point.hours 10 1 %}',
                //{% endfor %}
            ]
        }, {
            label: "Developers",
            borderColor: chartColors.devs,
            backgroundColor: chartColors.devs_fill,
            data: [
                //{% for point in data %}
                    '{{ point.users }}',
                //{% endfor %}
            ]
        }]
    }
});
