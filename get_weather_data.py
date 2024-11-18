import pandas as pd
import csv
from meteostat import Hourly, Point
from datetime import datetime

# Load the data
racedata_file = 'racedate.xlsx'
tracktocoord_file = 'tracktocoord.xlsx'

# Read Excel files
racedata = pd.read_excel(racedata_file)
tracktocoord = pd.read_excel(tracktocoord_file)

# Merge the race data with coordinates
racedata = racedata.merge(tracktocoord, on="Track", how="left")

# Open a CSV file to write results
output_file = 'weather.csv'
header_written = False  # Track if we've written the CSV header

with open(output_file, mode='a+', newline='') as csvfile:
    writer = csv.writer(csvfile)

    for index, row in racedata.iterrows():
        try:
            # Extract race data
            year = row['Season']
            month = row['Date'].month
            day = row['Date'].day
            location = row['Track']
            latitude = row['lat']
            longitude = row['lng']
            
            print(year, month, day)

            # Skip if coordinates are missing
            if pd.isna(latitude) or pd.isna(longitude):
                print(f"Coordinates missing for location: {location}, skipping.")
                continue

            # Combine year and month/day to form the date
            date_str = f"{year}-{month}-{day}"
            start = datetime.strptime(date_str, "%Y-%m-%d")
            end = start

            # Define the Point for the location
            race_point = Point(latitude, longitude)

            # Fetch hourly weather data
            hourly_data = Hourly(race_point, start, end)
            hourly_data = hourly_data.fetch()
            
            # Add metadata to the weather data
            hourly_data['year'] = year
            hourly_data['date'] = date_str
            hourly_data['location'] = location

            # Write data to CSV
            if not header_written:
                writer.writerow(list(hourly_data.columns))
                header_written = True

            for _, weather_row in hourly_data.iterrows():
                writer.writerow(weather_row.tolist())

            print(f"Weather data written for {location} on {date_str}.")

        except Exception as e:
            print(f"Failed to fetch data for {row['location']} on {date_str}: {e}")
