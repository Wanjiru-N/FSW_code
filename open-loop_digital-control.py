import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO

# Set up GPIO
PWM_PIN = 19  # GPIO pin connected to the device
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 8000)  # PWM with 8kHz frequency
pwm.start(0)  # Start with 0% duty cycle


def update_value(val):
    """Callback function to display the knob's value and update PWM output."""
    knob_value = int(val)  # Convert the value to an integer
    label.config(text=f"Knob Value: {knob_value}")  # Update the label
    pwm.ChangeDutyCycle(knob_value)  # Update PWM duty cycle
    print(f"Motor Set Point: {knob_value}% of full speed")


# Create the main application window
root = tk.Tk()
root.title("Control Knob")
root.geometry("320x240")

# Add a label to display the knob's value
label = tk.Label(root, text="Knob Value: 0", font=("Arial", 16))
label.pack(pady=20)

# Create a Scale widget to simulate a control knob
knob = tk.Scale(
    root,
    from_=0,  # Minimum value
    to=100,  # Maximum value
    orient="horizontal",  # Horizontal orientation
    command=update_value,  # Callback function
)
knob.pack(pady=20, padx=40, fill="x")


# Add an exit button to close the application
def on_exit():
    pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO
    root.quit()  # Close the application


exit_button = tk.Button(root, text="Exit", command=on_exit)
exit_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
