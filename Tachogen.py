#    This code reads analogue input (voltage from the tacho generator) and displays the average spindle speed in rpm for every second that the program runs.

import time
import threading
import Adafruit_ADS1x15
import tkinter as tk

# Create an ADS1115 ADC instance
adc = Adafruit_ADS1x15.ADS1115(busnum=1)

# ADS1115 gain setting (1 corresponds to ±4.096V input range)
GAIN = 1

# ADS1115 max voltage based on the gain (±4.096V for GAIN=1)
ADC_MAX_VOLTAGE = 4.096

# Tachogenerator output voltage range - stepped down (from 0.0000V to 4.0960V)
MIN_VOLTAGE = 0.0000
MAX_VOLTAGE = 4.0960

# RPM range (from 0 to 3000 RPM)
MIN_RPM = 0.0000
MAX_RPM = 3000.0000

# Initialize global variables for RPM values and average RPM
rpm_values = []
avg_rpm = 0.0


def read_voltage(adc_value):
    return adc_value * (ADC_MAX_VOLTAGE / 32767.0)


def map_voltage_to_rpm(voltage):
    return MIN_RPM + (
        (voltage - MIN_VOLTAGE) * (MAX_RPM - MIN_RPM) / (MAX_VOLTAGE - MIN_VOLTAGE)
    )


def read_adc():
    global rpm_values, avg_rpm
    start_time = time.time()

    while True:
        adc_value = adc.read_adc(0, gain=GAIN)
        voltage = read_voltage(adc_value)
        rpm = map_voltage_to_rpm(voltage)
        rpm_values.append(rpm)

        duty_cycle = (voltage / MAX_VOLTAGE) * 100
        duty_cycle = min(max(duty_cycle, 0), 100)

        # Print the current values
        print(
            f"POT Value: {duty_cycle:.2f}%, Tacho Voltage: {voltage:.2f}V, RPM: {rpm:.2f}"
        )

        if time.time() - start_time >= 1.0:
            if rpm_values:
                avg_rpm = sum(rpm_values) / len(rpm_values)
            print(f"Average RPM for last second: {avg_rpm:.2f}")
            rpm_values = []  # Clear the list for the next batch
            start_time = time.time()  # Reset the start time

        time.sleep(0.2)


def update_display():
    avg_label.config(text=f"Av. RPM: {avg_rpm:.2f}", font=("Calibri", 28))
    root.after(1000, update_display)  # Update every second


# Create main window
root = tk.Tk()
root.title("RPM Display")

# Create label for displaying average RPM
avg_label = tk.Label(root, text="", font=("Calibri", 28))
avg_label.pack(pady=20)

# Start ADC reading in a separate thread
threading.Thread(target=read_adc, daemon=True).start()

# Start the Tkinter display update loop
update_display()

# Start the Tkinter event loop
root.mainloop()
