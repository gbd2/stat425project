import pandas as pd
import csv
from meteostat import Hourly, Point
from datetime import datetime, timedelta
import numpy as np

# Load the weather data
input_file = 'C:/VSCode/stat425project/data/weather_final.csv'
output_file = 'C:/VSCode/stat425project/data/weather_weekly.csv'

# Read the existing weather data and racedate data
weather_data = pd.read_csv(input_file)

# Load the data
racedata_file = 'data/racedate.xlsx'
tracktocoord_file = 'data/tracktocoord.xlsx'

# Read Excel files
racedata = pd.read_excel(racedata_file)
tracktocoord = pd.read_excel(tracktocoord_file)

# Merge the race data with coordinates
racedata = racedata.merge(tracktocoord, on="Track", how="left")

# Ensure date column is in datetime format
weather_data['date'] = pd.to_datetime(weather_data['date'])

# Create a new CSV file to write augmented data
header_written = False

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

# Augment the weather data
with open(output_file, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    for index, row in weather_data.iterrows():
        try:
            # Extract data from current row
            location = row['location']
            date = row['date']
            latitude =racedata[racedata['Track'] == location]['lat'].values[0]
            longitude = racedata[racedata['Track'] == location]['lng'].values[0]
            
            # Skip if coordinates are missing
            if pd.isna(latitude) or pd.isna(longitude):
                print(f"Coordinates missing for location: {location}, skipping.")
                continue
            
            # Compute date range (3 days before and after the race)
            for i in range(-3, 4, 1):
                start_date = date + timedelta(days=i)
                end_date = start_date
                
                race_point = Point(latitude, longitude)

                # Fetch hourly weather data
                hourly_data = Hourly(race_point, start_date, end_date)
                hourly_data = hourly_data.fetch()
                
                # Retry if 'prcp' is NaN
                if hourly_data.empty or pd.isna(hourly_data['prcp']).all():
                    print(f"No valid 'prcp' data for {location}, retrying with adjusted coordinates.")
                    hourly_data = fetch_with_retries(latitude, longitude, start_date, end_date)

                if hourly_data is None or hourly_data.empty:
                    print(f"Failed to retrieve valid data for {location} on {date}, skipping.")
                    continue

                if hourly_data is None or hourly_data.empty:
                    print(f"Failed to retrieve data for {location} from {start_date} to {end_date}, skipping.")
                    continue
    
                # Add metadata to the weather data
                hourly_data['year'] = start_date.year
                hourly_data['date'] = start_date
                hourly_data['location'] = location
                hourly_data['associated_race'] = f"{location}_{date}"

                # Write data to CSV
                if not header_written:
                    writer.writerow(list(hourly_data.columns))
                    header_written = True

                for _, weather_row in hourly_data.iterrows():
                    writer.writerow(weather_row.tolist())

                print(f"Weather data written for {location} from {start_date} to {end_date}.")

        except Exception as e:
            print(f"Failed to process data for {row['location']} on {row['date']}: {e}")
