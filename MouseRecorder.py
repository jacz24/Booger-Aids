#!/usr/bin/env python3
import csv
import time
from datetime import datetime
from pynput import mouse, keyboard
import argparse
import random

def auto_break_check():
    # 0.5% chance to trigger an auto-break.
    if random.random() < 0.005:
        break_time = random.gauss(15, 10)
        # Clamp the break time between 1 and 85 seconds.
        break_time = max(1, min(break_time, 85))
        print(f"Auto-break triggered: waiting for {break_time:.2f} seconds.", flush=True)
        time.sleep(break_time)

def record_mouse(filename, duration_hours=None):
    """
    Records mouse events and writes them to the specified CSV file.
    If duration_hours is provided, recording stops after that duration;
    otherwise, it runs indefinitely until manually stopped.
    """
    end_time = None
    if duration_hours is not None:
        end_time = time.time() + duration_hours * 3600

    with open(filename, mode='w', newline='') as csvfile:
        fieldnames = ['timestamp', 'event_type', 'x', 'y', 'button', 'pressed', 'dx', 'dy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        def on_move(x, y):
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'move',
                'x': x,
                'y': y,
                'button': '',
                'pressed': '',
                'dx': '',
                'dy': ''
            })
            csvfile.flush()
            auto_break_check()
            if end_time is not None and time.time() >= end_time:
                return False

        def on_click(x, y, button, pressed):
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': str(pressed),
                'dx': '',
                'dy': ''
            })
            csvfile.flush()
            auto_break_check()
            if end_time is not None and time.time() >= end_time:
                return False

        def on_scroll(x, y, dx, dy):
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'scroll',
                'x': x,
                'y': y,
                'button': '',
                'pressed': '',
                'dx': dx,
                'dy': dy
            })
            csvfile.flush()
            auto_break_check()
            if end_time is not None and time.time() >= end_time:
                return False

        print(f"Recording mouse events to {filename}...", flush=True)
        with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()
    print(f"Recording complete. Data saved to {filename}")

def playback_mouse(filename, speedup):
    """
    Reads the CSV log file and replays the mouse events.
    The speedup factor adjusts the delay between events.
    """
    import pyautogui  # Import here because playback uses pyautogui
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        events = list(reader)
    if not events:
        print("No events found in the log.")
        return
    prev_time = datetime.fromisoformat(events[0]['timestamp'])
    print(f"Starting playback of {filename} with speedup factor {speedup}", flush=True)
    for event in events:
        current_time = datetime.fromisoformat(event['timestamp'])
        delay = (current_time - prev_time).total_seconds() * speedup
        if delay > 0:
            time.sleep(delay)
        prev_time = current_time
        event_type = event['event_type']
        x = float(event['x'])
        y = float(event['y'])
        if event_type == 'move':
            pyautogui.moveTo(x, y)
        elif event_type == 'click':
            pyautogui.click(x, y)
        elif event_type == 'scroll':
            try:
                dy = float(event['dy'])
            except:
                dy = 0
            pyautogui.scroll(int(dy), x=x, y=y)
    print("Playback complete.", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Mouse Recorder and Playback")
    parser.add_argument("mode", choices=["record", "playback"], help="Mode: record or playback")
    parser.add_argument("--file", type=str, default="mouse_log.csv", help="Filename for the log")
    parser.add_argument("--duration", type=float, default=None, help="Recording duration in hours (if not provided, records indefinitely)")
    parser.add_argument("--speedup", type=float, default=1.0, help="Playback speedup factor")
    args = parser.parse_args()

    if args.mode == "record":
        record_mouse(args.file, args.duration)
    elif args.mode == "playback":
        playback_mouse(args.file, args.speedup)

if __name__ == "__main__":
    main()
