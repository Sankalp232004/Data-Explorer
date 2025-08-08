document.addEventListener('DOMContentLoaded', () => {
    const controls = document.querySelectorAll('.plot-control');
    const plotDiv = document.getElementById('plot-div');
    const filename = plotDiv.dataset.filename;

    async function updatePlot() {
        const payload = {
            x_axis: document.getElementById('x_axis').value,
            y_axis: document.getElementById('y_axis').value,
            chart_type: document.getElementById('chart_type').value,
        };

        const response = await fetch(`/update_plot/${filename}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            console.error("Failed to fetch plot data.");
            plotDiv.innerHTML = "<p>Error loading plot.</p>";
            return;
        }

        const graphJSON = await response.json();

        if (graphJSON.error) {
            plotDiv.innerHTML = `<p style="color: red;">${graphJSON.error}</p>`;
        } else {
            const graphData = JSON.parse(graphJSON);
            Plotly.react(plotDiv, graphData.data, graphData.layout);
        }
    }

    controls.forEach(control => {
        control.addEventListener('change', updatePlot);
    });

    updatePlot();
});
