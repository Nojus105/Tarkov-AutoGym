import sys
import time

import cv2
import mss
import numpy as np
import pyautogui
from pynput import keyboard



# tweaking
MONITOR_INDEX = 1
CANNY_LOW = 60
CANNY_HIGH = 160
EDGE_BLUR_K = 3
EDGE_DILATE = 3
AREA_MIN = 1600
APPROX_EPS = 0.03
HEX_VERT_MIN = 6
HEX_VERT_MAX = 6
IDLE_SLEEP_S = 0.05
LOOP_SLEEP_S = 0.02
CLICK_SLEEP_S = 0.05


running = False
save_frame = False


def detect(frame_bgr: np.ndarray) -> bool:
	gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
	if EDGE_BLUR_K and EDGE_BLUR_K > 1:
		gray = cv2.GaussianBlur(gray, (EDGE_BLUR_K, EDGE_BLUR_K), 0)
	th = cv2.Canny(gray, CANNY_LOW, CANNY_HIGH)
	if EDGE_DILATE and EDGE_DILATE > 1:
		k = np.ones((EDGE_DILATE, EDGE_DILATE), np.uint8)
		th = cv2.dilate(th, k, 1)
	contours, _ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	hexes = 0
	for c in contours:
		if cv2.contourArea(c) < AREA_MIN:
			continue
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, APPROX_EPS * peri, True)
		v = len(approx)
		if HEX_VERT_MIN <= v <= HEX_VERT_MAX and cv2.isContourConvex(approx):
			hexes += 1
	print(f"[hexes detected: {hexes}]")
	return hexes >= 2


def on_press(key) -> None:
	global running, save_frame
	if key == keyboard.Key.f8:
		running = not running
		print("Running:", running)
	elif key == keyboard.Key.f9:
		print("Exiting...")
		sys.exit(0)
	elif key == keyboard.Key.f10:
		save_frame = True


def main() -> None:
	global save_frame
	keyboard.Listener(on_press=on_press).start()
	with mss.mss() as sct:
		mon = sct.monitors[MONITOR_INDEX]
		was_detected = False
		try:
			while True:
				if not running:
					time.sleep(IDLE_SLEEP_S)
					continue
				frame = np.array(sct.grab(mon))[:, :, :3]  # BGRA -> BGR
				if save_frame:
					fname = f"screenshot_{int(time.time())}.png"
					cv2.imwrite(fname, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
					print(f"Saved screenshot to {fname}")
					save_frame = False
				detected = detect(frame)
				if detected and not was_detected:
					print("Detected")
					pyautogui.click()
					time.sleep(CLICK_SLEEP_S)
				else:
					time.sleep(LOOP_SLEEP_S)
				was_detected = detected
		except KeyboardInterrupt:
			print("Exiting...")


if __name__ == "__main__":
	main()