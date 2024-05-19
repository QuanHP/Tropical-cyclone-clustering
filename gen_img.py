import numpy as np
import h5py
import matplotlib.pyplot as plt
import os
import glob

from matplotlib.colors import LinearSegmentedColormap

# Tạo danh sách các mốc giá trị và mã màu tương ứng
boundaries = [0, 4, 8, 12, 16, 20]
colors = ['black', 'dimgray', 'darkgray', 'gray', 'lightgray', 'white']
boundaries_normalized = np.linspace(0, 1, len(colors))
cmap = LinearSegmentedColormap.from_list('custom_cmap', list(zip(boundaries_normalized, colors)))

# -- Define a function to calculate the distance in kilometers corresponding to one degree of longitude or latitude
def deg_to_km(latitude):
    R = 6371.0
    lat_deg_to_km = 111.32
    lon_deg_to_km = np.cos(np.radians(latitude)) * lat_deg_to_km
    return lat_deg_to_km, lon_deg_to_km

# -- Read latitude, longitude, and wind speed information from the lat_lon.txt file and store it in a dictionary
lat_lon_wind_dict = {}
with open('data\lat_lon.txt', 'r') as lat_lon_file:
    for line in lat_lon_file:
        parts = line.strip().split('\t')
        if len(parts) == 4:
            timestamp = parts[0][0:4] + parts[0][5:7] + parts[0][8:10] + parts[0][11:13] + parts[0][14:16] + parts[0][17:19]
            wind_speed = parts[3]
            lat_lon_wind_dict[timestamp] = (float(parts[1]), float(parts[2]), wind_speed)

# -- Define the folder paths
input_folder = 'F:\\Data\\WP'
output_folder = 'F:\\Data\\gray60+'


# -- Define a function to process each HDF5 file
def process_hdf5_file(file_path):
    with h5py.File(file_path, 'r') as data:
        # Extract timestamp from file name
        filename = os.path.basename(file_path)
        parts = filename.split('.')
        timestamp_parts = parts[4].split('-')
        timestamp = timestamp_parts[0] + '' + timestamp_parts[1][1:]  # Combine date and time

        # Find matching timestamp in lat_lon_wind_dict
        lat_lon_wind = lat_lon_wind_dict.get(timestamp)

        if lat_lon_wind is not None and int(lat_lon_wind[2]) >= 60:
            center_lat, center_lon, wind_speed = lat_lon_wind[0], lat_lon_wind[1], lat_lon_wind[2]

            # Calculate the distance in kilometers corresponding to one degree of latitude and longitude at the center point
            lat_deg_to_km, lon_deg_to_km = deg_to_km(center_lat)

            # Define the size of the square region (in kilometers)
            region_size_km = 1000

            # Calculate the half size of the square region (in degrees)
            half_region_size_deg = region_size_km / 2 / lat_deg_to_km

            # Calculate the boundaries of the square region
            top_lat = center_lat + half_region_size_deg
            bottom_lat = center_lat - half_region_size_deg
            left_lon = center_lon - half_region_size_deg
            right_lon = center_lon + half_region_size_deg

            # Crop the precipitation data to the specified region
            precip = data['/Grid/precipitationCal'][:]
            precip = np.flip(precip[0, :, :].transpose(), axis=0)
            top_index = int((90 - top_lat) * 10)
            bottom_index = int((90 - bottom_lat) * 10)
            left_index = int((180 + left_lon) * 10)
            right_index = int((180 + right_lon) * 10)
            cropped_precip = precip[top_index:bottom_index, left_index:right_index]
            cropped_precip[cropped_precip < 2] = 0

            # Display the cropped precipitation data with padding
            plt.imshow(cropped_precip,cmap=cmap, vmin=-1, vmax=10,
                       extent=[left_lon - 1, right_lon + 1, bottom_lat - 1, top_lat + 1])

            # Hide axes and labels
            plt.axis('off')

            # Automatically adjust subplot parameters to give specified padding
            plt.tight_layout(pad=0)

            # Save the image to disk
            image_name = f'{timestamp}_{wind_speed}.png'
            plt.savefig(os.path.join(output_folder, image_name), dpi=200, bbox_inches='tight', pad_inches=0)

            # Close the plot
            plt.close()


# -- Define a function to process all HDF5 files in the input folder
def process_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    hdf5_files = glob.glob(os.path.join(input_folder, '*.HDF5'))

    for file_path in hdf5_files:
        process_hdf5_file(file_path)


# -- Call the function to process all HDF5 files
process_files(input_folder, output_folder)
