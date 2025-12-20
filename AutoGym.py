import time

import mss
import numpy as np
import pyautogui


def detect_event(frame_bgr: np.ndarray) -> bool:
	"""Return True when the on-screen event is detected.

	`frame_bgr` is a HxWx3 uint8 image in BGR order.

	TODO: implement your detection here.
	"""
	return False


def main() -> None:
	# Simple knobs
	poll_interval_s = 0.02  # ~50 FPS; raise to reduce CPU
	click_pause_s = 0.05    # small pause after clicking

	# Optional safety: moving mouse to top-left aborts (PyAutoGUI default).
	pyautogui.FAILSAFE = True

	with mss.mss() as sct:
		monitor = sct.monitors[1]  # primary monitor

		while True:
			# Grab screen; MSS returns BGRA
			shot = sct.grab(monitor)
			frame = np.asarray(shot)[..., :3]  # BGR

			if detect_event(frame):
				pyautogui.click(button="left")
				time.sleep(click_pause_s)
			else:
				time.sleep(poll_interval_s)


if __name__ == "__main__":
	main()
