import requests

# URL for the water data service API
url = 'https://waterservices.usgs.gov/nwis/iv/'

# USGS gage number for the stream of interest
gage_num = '01638500'

# Start and end dates for the period of interest
start_date = '2022-01-01'
end_date = '2022-01-31'

# Parameters for the API request
params = {
    'format': 'json',
    'sites': gage_num,
    'startDT': start_date,
    'endDT': end_date,
    'parameterCd': '00060' # USGS code for streamflow
}

# Make the API request
response = requests.get(url, params=params)

# Parse the JSON response
data = response.json()

# Print the first 10 streamflow values
for value in data['value']['timeSeries'][0]['values'][0]['value'][:10]:
    print(f"{value['dateTime']} {value['value']}")