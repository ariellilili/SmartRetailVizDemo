# SmartRetailVizDemo

This project is to simulate data that could be retained in a smart retail store and then develop visualization dashboard demos.

- `create_tables.py` simulates data tables that can be saved as csv files which then will be used for the visualizations. The tables can also be saved as txt files following InfluxDB line protocol format so that they can be uploaded onto InfluxDB.
- `app_day.py` is a Plotly dashboard for a single store in a single day.
- `app_year.py` is a Plotly dashboard for a single store for an entire year.

To open the dashboards, run `python app_day.py` using command line and then open the shown URL in a browser.
