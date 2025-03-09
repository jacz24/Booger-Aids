import pyautogui
import random
import time
import math
from pynput import keyboard
import os
import argparse

def on_press(key):
    try:
        if key.char == 'p':
            print("Terminating bot...", flush=True)
            os._exit(0)
    except AttributeError:
        pass  # Ignore non-character keys

# Start the keyboard listener in a separate thread.
listener = keyboard.Listener(on_press=on_press)
listener.start()

def random_point_in_box(x1, y1, x2, y2):
    """Given two corners of a box, returns a random (x, y) coordinate within that box."""
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    return random.randint(left, right), random.randint(top, bottom)

def fast_human_like_move(start, end, desired_speed=6000, min_duration=0.03, max_duration=0.1, steps=5):
    """
    Moves the mouse from 'start' to 'end' along a cubic Bézier curve.
    Total duration is computed from the distance and desired speed, then clamped.
    """
    x0, y0 = start
    x3, y3 = end
    distance = math.hypot(x3 - x0, y3 - y0)
    base_duration = distance / desired_speed
    total_duration = base_duration * random.uniform(0.8, 1.2)
    total_duration = max(total_duration, min_duration)
    total_duration = min(total_duration, max_duration)
    
    dx = x3 - x0
    dy = y3 - y0
    if dx == 0 and dy == 0:
        perp = (0, 0)
    else:
        mag = math.hypot(dx, dy)
        perp = (-dy/mag, dx/mag)
    
    offset_range = 20
    cp1 = (x0 + dx/3 + random.uniform(-offset_range, offset_range) * perp[0],
           y0 + dy/3 + random.uniform(-offset_range, offset_range) * perp[1])
    cp2 = (x0 + 2*dx/3 + random.uniform(-offset_range, offset_range) * perp[0],
           y0 + 2*dy/3 + random.uniform(-offset_range, offset_range) * perp[1])
    
    path = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**3 * x0 + 3*(1-t)**2*t * cp1[0] + 3*(1-t)*t**2 * cp2[0] + t**3 * x3
        y = (1-t)**3 * y0 + 3*(1-t)**2*t * cp1[1] + 3*(1-t)*t**2 * cp2[1] + t**3 * y3
        path.append((x, y))
    
    step_duration = total_duration / steps
    for point in path:
        pyautogui.moveTo(point[0], point[1], duration=step_duration, tween=pyautogui.easeInOutQuad)
        time.sleep(0.001)

def human_like_click(x, y, click_type='left'):
    """Moves the mouse to (x, y) using fast_human_like_move and then performs the click."""
    start = pyautogui.position()
    fast_human_like_move(start, (x, y), desired_speed=6000, min_duration=0.03, max_duration=0.1, steps=5)
    if click_type == 'left':
        pyautogui.click()
    elif click_type == 'right':
        pyautogui.rightClick()
    else:
        pyautogui.click()

def click_in_box(box, click_type='left'):
    """
    Randomly selects a point within the provided box (defined as (x1, y1, x2, y2))
    and performs the click.
    """
    x1, y1, x2, y2 = box
    target_x, target_y = random_point_in_box(x1, y1, x2, y2)
    print(f"Clicking {click_type} at random point ({target_x}, {target_y}) within box {box}.", flush=True)
    human_like_click(target_x, target_y, click_type)

def main(offset=0):
    """
    Processes the sequence of steps with an x-axis offset.
    Each step is defined with a clickable box, click type, and wait time.
    For the 6th step, the wait time is randomized between 50 and 80 seconds.
    """
    steps = [
        {"box": (92, 147, 114, 171), "click_type": "right", "wait": 0},
        {"box": (7, 266, 103, 271), "click_type": "left", "wait": 0},
        {"box": (496, 77, 509, 91), "click_type": "left", "wait": 0},
        {"box": (589, 697, 608, 713), "click_type": "left", "wait": 0},
        {"box": (633, 700, 655, 718), "click_type": "left", "wait": 0},
        {"box": (223, 918, 293, 969), "click_type": "left", "wait": None},  # Wait between 50 and 80 sec.
        {"box": (333, 479, 351, 511), "click_type": "left", "wait": 0},
        {"box": (633, 700, 651, 712), "click_type": "right", "wait": 0},
        {"box": (556, 805, 610, 809), "click_type": "left", "wait": 0},
    ]
    
    for i, step in enumerate(steps):
        # Apply the x-offset to the box.
        box = step["box"]
        new_box = (box[0] + offset, box[1], box[2] + offset, box[3])
        click_in_box(new_box, step["click_type"])
        if i == 5:  # For the sixth step, random wait between 50 and 80 seconds.
            wait_time = random.uniform(50, 80)
        else:
            wait_time = step["wait"]
        if wait_time:
            print(f"Waiting for {wait_time:.2f} seconds.", flush=True)
            time.sleep(wait_time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FletchtingBot: runs a click sequence with an x-offset.")
    parser.add_argument("--offset", type=int, default=0, help="x-axis offset to apply to all click boxes.")
    args = parser.parse_args()
    
    while True:
        main(offset=args.offset)
        print("Sequence complete. Restarting sequence.", flush=True)
        time.sleep(3)
