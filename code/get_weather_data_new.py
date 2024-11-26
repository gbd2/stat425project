import pandas as pd
import csv
from meteostat import Hourly, Point
from datetime import datetime
import numpy as np

# Load the data
racedata_file = 'data/racedate.xlsx'
tracktocoord_file = 'data/tracktocoord.xlsx'

# Read Excel files
racedata = pd.read_excel(racedata_file)
tracktocoord = pd.read_excel(tracktocoord_file)

# Merge the race data with coordinates
racedata = racedata.merge(tracktocoord, on="Track", how="left")

# Open a CSV file to write results
output_file = 'weather_new2.csv'
header_written = False  # Track if we've written the CSV header

# Retry function
def fetch_with_retries(latitude, longitude, start, end, step=0.05, range_limit=0.25):
    for delta_lat in np.arange(-range_limit, range_limit + step, step):
        for delta_lng in np.arange(-range_limit, range_limit + step, step):
            try:
                adjusted_lat = latitude + delta_lat
                adjusted_lng = longitude + delta_lng
                adjusted_point = Point(adjusted_lat, adjusted_lng)
                hourly_data = Hourly(adjusted_point, start, end)
                hourly_data = hourly_data.fetch()
                if not hourly_data.empty and not pd.isna(hourly_data['prcp']).all():
                    return hourly_data
            except Exception as e:
                # Log but continue retrying
                print(f"Retry failed for lat: {adjusted_lat}, lng: {adjusted_lng}: {e}")
    return None

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

            # Fetch hourly weather data
            race_point = Point(latitude, longitude)
            hourly_data = Hourly(race_point, start, end)
            hourly_data = hourly_data.fetch()
            
            # Retry if 'prcp' is NaN
            if hourly_data.empty or pd.isna(hourly_data['prcp']).all():
                print(f"No valid 'prcp' data for {location}, retrying with adjusted coordinates.")
                hourly_data = fetch_with_retries(latitude, longitude, start, end)

            if hourly_data is None or hourly_data.empty:
                print(f"Failed to retrieve valid data for {location} on {date_str}, skipping.")
                continue
            
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
            print(f"Failed to fetch data for {row['Track']} on {date_str}: {e}")
