import pyautogui
import random
import time  # Correct import
import numpy as np
from pynput import keyboard  # Using pynput for key listening

# Global flag to control the loop
running = True

def on_press(key):
    """Stops the script when 'p' is pressed."""
    global running
    try:
        if key.char == 'p':
            running = False
            print("\n[PRESSED 'P']: Stopping script...")
    except AttributeError:
        pass  # Ignore special keys

# Start a listener in the background
listener = keyboard.Listener(on_press=on_press)
listener.start()

def random_clicker():
    global running
    total_clicks = 9255  # Total number of clicks to attempt
    clicks_until_pause = random.randint(550, 1250)

    def get_click_interval():
        # Generate a normally distributed interval with mean 1.40 seconds and standard deviation 0.25
        interval = np.random.normal(loc=1.40, scale=0.25)
        return max(0.33, min(interval, 92))  # Ensure the interval is within a reasonable range

    def get_double_click_time():
        # Generate a normally distributed double-click delay with mean 2.5 seconds and standard deviation 0.4
        double_click_time = np.random.normal(loc=2.5, scale=0.4)
        return max(0.5, min(double_click_time, 5))  # Ensure delay is within a reasonable range

    for i in range(total_clicks):
        if not running:
            break  # Stop if 'p' was pressed

        interval = get_click_interval()
        pyautogui.click()  # Perform a click at the current mouse location
        print(f"Click {i + 1}/{total_clicks} done! Waiting {interval:.2f} seconds for the next click...")

        # 1-in-33 chance to perform a double-click with a variable delay
        if random.randint(1, 35) == 1:
            double_click_time = get_double_click_time()
            time.sleep(double_click_time)
            pyautogui.click()
            print(f"Double click executed (after {double_click_time:.2f} seconds)")

        time.sleep(interval)

        # Every 'clicks_until_pause' clicks, pause for a random duration between 5 and 95 seconds
        if (i + 1) % clicks_until_pause == 0:
            pause_duration = random.uniform(5, 95)
            print(f"Pausing for {pause_duration:.2f} seconds after {clicks_until_pause} clicks...")
            time.sleep(pause_duration)
            clicks_until_pause = random.randint(300, 1250)
            print("Resuming clicks...")

    print("Script stopped.")

if __name__ == "__main__":
    random_clicker()
p