import sys
import time
import cv2
import mss
import numpy as np
import pyautogui
from pynput import keyboard

MONITOR = 1
REGION = {"left": 750, "top": 620, "width": 400, "height": 400}
GAP_THRESHOLD = 70
BRIGHTNESS_THRESH = 100

running = False
save_screenshot = False

def find_hexagon_radii(frame):
    """Find bright hexagon contours and return their enclosing circle radii."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    _, thresh = cv2.threshold(gray, BRIGHTNESS_THRESH, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    radii = []
    center = (frame.shape[1] // 2, frame.shape[0] // 2)
    
    for c in contours:
        (cx, cy), radius = cv2.minEnclosingCircle(c)
        
        dist_from_center = np.sqrt((cx - center[0])**2 + (cy - center[1])**2)
        if dist_from_center < radius * 0.5:
            radii.append(radius)
    
    return sorted(radii, reverse=True)

def should_click(frame):
    """Return True when the gap between hexagons is small enough."""
    radii = find_hexagon_radii(frame)
    if len(radii) < 2:
        return False
    
    outer, inner = radii[0], radii[1]
    gap = outer - inner
    
    if 0 < gap <= GAP_THRESHOLD:
        print(f"CLICK! Gap: {gap:.1f}px, radii: {outer:.0f}, {inner:.0f}")
        return True
    return False

def on_press(key):
    global running, save_screenshot
    if key == keyboard.Key.f8:
        running = not running
        print(f"{'Started' if running else 'Stopped'}")
    elif key == keyboard.Key.f9:
        print("Exiting...")
        sys.exit(0)
    elif key == keyboard.Key.f10:
        save_screenshot = True

def main():
    global save_screenshot
    print("Tarkov AutoGym - F8: start/stop, F9: exit, F10: screenshot")
    keyboard.Listener(on_press=on_press).start()
    
    with mss.mss() as sct:
        last_click = 0
        while True:
            if not running:
                time.sleep(0.05)
                continue
            
            frame = np.array(sct.grab(REGION))[:, :, :3]
            
            if save_screenshot:
                fname = f"debug_{int(time.time())}.png"
                cv2.imwrite(fname, frame)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, BRIGHTNESS_THRESH, 255, cv2.THRESH_BINARY)
                cv2.imwrite(f"debug_thresh_{int(time.time())}.png", thresh)
                print(f"Saved debug screenshots")
                save_screenshot = False
            
            if should_click(frame) and time.time() - last_click > 0.3:
                pyautogui.click()
                last_click = time.time()
                time.sleep(0.1)
            else:
                time.sleep(0.01)

if __name__ == "__main__":
    main()