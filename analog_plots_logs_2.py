import Adafruit_ADS1x15
import matplotlib.pyplot as plt
import time
import csv
import os
import pandas as pd
from collections import deque
from datetime import datetime
import signal
import sys

# Create an ADS1115 ADC instance
adc = Adafruit_ADS1x15.ADS1115(busnum=1)

# Set the gain
GAIN = 1  # Gain setting for +/-4.096V input range
REFERENCE_VOLTAGE = 4.096  # Reference voltage for gain=1
MAX_ADC_VALUE = 32767  # 16-bit resolution

# Configuration for real-time plotting
MAX_POINTS = 60  # Maximum points to display on the plot
times = deque(maxlen=MAX_POINTS)
voltages = deque(maxlen=MAX_POINTS)
speeds = deque(maxlen=MAX_POINTS)

# Determine the Desktop path for the current user
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "Data")
screen_folder = os.path.join(desktop_path, "Images")
os.makedirs(data_folder, exist_ok=True)
os.makedirs(screen_folder, exist_ok=True)


# Function to get unique file name
def get_unique_file_name(folder, base_name, extension):
    i = 1
    file_name = f"{base_name}.{extension}"
    while os.path.exists(os.path.join(folder, file_name)):
        file_name = f"{base_name}_{i}.{extension}"
        i += 1
    return os.path.join(folder, file_name)


# Define file names
csv_file = get_unique_file_name(data_folder, "test", "csv")
xlsx_file = get_unique_file_name(data_folder, "test", "xlsx")

# Write CSV header
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Elapsed Time (s)", "Voltage (V)", "Speed (RPM)"])

# Initialize the plot
plt.ion()  # Enable interactive mode
fig, (ax_voltage, ax_speed) = plt.subplots(2, 1, figsize=(4, 6), dpi=100)

# Adjust subplot parameters
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.4, wspace=0.3)

# Voltage plot
(line_voltage,) = ax_voltage.plot([], [], "-")
ax_voltage.set_title("Tacho Voltage", fontsize=8)
ax_voltage.set_xlabel("Time (s)", fontsize=8)
ax_voltage.set_ylabel("Voltage (V)", fontsize=8)
ax_voltage.set_xlim(0, MAX_POINTS)
ax_voltage.set_ylim(0, REFERENCE_VOLTAGE)
ax_voltage.grid()

# Speed plot
(line_speed,) = ax_speed.plot([], [], "-")
ax_speed.set_title("Speed", fontsize=8)
ax_speed.set_xlabel("Time (s)", fontsize=8)
ax_speed.set_ylabel("Speed (RPM)", fontsize=8)
ax_speed.set_xlim(0, MAX_POINTS)
ax_speed.set_ylim(0, 3000)
ax_speed.grid()

plt.tight_layout()

# Global variables for signal handling
is_running = True
start_time = time.time()
all_data = []
last_screenshot_time = time.time()
SCREENSHOT_INTERVAL = 60  # Screenshot interval in seconds


# Save figure screenshot
def save_figure_screenshot(fig, folder, prefix="screenshot"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{prefix}_{timestamp}.png"
    file_path = os.path.join(folder, file_name)
    fig.savefig(file_path)
    print(f"Screenshot saved: {file_path}")


# Signal handler
def signal_handler(sig, frame):
    global is_running
    print("\nTermination signal received. Exiting...")
    is_running = False


# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    print(
        f"Reading data from ADS1115 and plotting in real-time...\nData will be saved in: {data_folder}\nScreenshots will be saved in: {screen_folder}"
    )

    while is_running:
        # Read raw ADC value from AIN0
        raw_value = adc.read_adc(0, gain=GAIN)
        voltage = (raw_value / MAX_ADC_VALUE) * REFERENCE_VOLTAGE

        # Convert voltage to speed
        speed = voltage * (3000 / 4.096)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append data
        times.append(elapsed_time)
        voltages.append(voltage)
        speeds.append(speed)
        all_data.append([timestamp, elapsed_time, voltage, speed])

        # Save data to CSV
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, elapsed_time, voltage, speed])

        # Update voltage plot
        line_voltage.set_xdata(range(len(times)))
        line_voltage.set_ydata(voltages)
        ax_voltage.set_xlim(0, len(times))
        ax_voltage.set_ylim(
            min(voltages, default=0) - 0.1, max(voltages, default=1) + 0.1
        )

        # Update speed plot
        line_speed.set_xdata(range(len(times)))
        line_speed.set_ydata(speeds)
        ax_speed.set_xlim(0, len(times))
        ax_speed.set_ylim(min(speeds, default=0) - 10, max(speeds, default=100) + 10)

        # Redraw the plots
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Save a screenshot every 60 seconds
        if time.time() - last_screenshot_time >= SCREENSHOT_INTERVAL:
            save_figure_screenshot(fig, screen_folder)
            last_screenshot_time = time.time()

        # Pause for a short duration
        time.sleep(0.1)

finally:
    # Save data to XLSX
    df = pd.DataFrame(
        all_data,
        columns=["Timestamp", "Elapsed Time (s)", "Voltage (V)", "Speed (RPM)"],
    )
    df.to_excel(xlsx_file, index=False)

    print(f"Data saved:\nCSV: {csv_file}\nXLSX: {xlsx_file}")
    save_figure_screenshot(fig, screen_folder, prefix="final_screenshot")
    plt.ioff()
    plt.show()
