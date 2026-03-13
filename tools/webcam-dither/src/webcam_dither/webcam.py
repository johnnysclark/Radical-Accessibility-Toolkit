"""Webcam capture with live dithered preview and keyboard controls."""

import cv2
import numpy as np

from webcam_dither.dither_engine import dither, ALGORITHM_NAMES
from webcam_dither.export import (
    save_screenshot_with_pdf,
    save_bracket,
)


# Key codes (OpenCV waitKey returns)
KEY_ESC = 27
KEY_Q = ord("q")
KEY_S = ord("s")
KEY_B = ord("b")
KEY_H = ord("h")
KEY_I = ord("i")
KEY_1 = ord("1")
KEY_2 = ord("2")
KEY_3 = ord("3")
KEY_LBRACKET = ord("[")
KEY_RBRACKET = ord("]")
KEY_MINUS = ord("-")
KEY_EQUALS = ord("=")

# Arrow keys come through as special codes on different platforms.
# OpenCV on Linux often returns these via waitKeyEx.
KEY_UP = 82
KEY_DOWN = 84
KEY_LEFT = 81
KEY_RIGHT = 83
# Some systems use higher codes
KEY_UP_ALT = 2490368
KEY_DOWN_ALT = 2621440
KEY_LEFT_ALT = 2424832
KEY_RIGHT_ALT = 2555904


class DitherParams:
    """Mutable container for live-tunable dithering parameters."""

    def __init__(self, spacing=8, dot_scale=0.8, algorithm="halftone",
                 brightness=0, contrast=1.0, invert=False):
        self.spacing = spacing
        self.dot_scale = dot_scale
        self.algorithm = algorithm
        self.brightness = brightness
        self.contrast = contrast
        self.invert = invert

    # Spacing bounds
    SPACING_MIN = 3
    SPACING_MAX = 30

    # Dot scale bounds
    DOT_SCALE_MIN = 0.2
    DOT_SCALE_MAX = 2.0
    DOT_SCALE_STEP = 0.1

    # Brightness bounds
    BRIGHTNESS_MIN = -100
    BRIGHTNESS_MAX = 100
    BRIGHTNESS_STEP = 5

    # Contrast bounds
    CONTRAST_MIN = 0.3
    CONTRAST_MAX = 3.0
    CONTRAST_STEP = 0.1

    def summary(self):
        """Return a one-line summary of current parameters."""
        algo_name = ALGORITHM_NAMES.get(self.algorithm, self.algorithm)
        inv = " [INVERTED]" if self.invert else ""
        return (
            "algorithm={}, spacing={}, dot_scale={:.1f}, "
            "brightness={}, contrast={:.1f}{}"
        ).format(algo_name, self.spacing, self.dot_scale,
                 self.brightness, self.contrast, inv)


def _print_controls():
    """Print keyboard controls to console."""
    print("OK: Keyboard controls:")
    print("OK:   [ / ]       Decrease / increase dot spacing")
    print("OK:   - / =       Decrease / increase dot scale")
    print("OK:   Up / Down   Increase / decrease brightness")
    print("OK:   Left / Right  Decrease / increase contrast")
    print("OK:   1 / 2 / 3   Halftone / Ordered / Floyd-Steinberg")
    print("OK:   i           Toggle invert")
    print("OK:   s           Take screenshot (PNG + PDF)")
    print("OK:   b           Bracket mode (tight/medium/loose)")
    print("OK:   h           Show current parameters")
    print("OK:   q / ESC     Quit")


def _handle_key(key, params, last_dithered, output_dir, paper_size,
                generate_pdf):
    """Handle a keypress. Returns True to quit, False to continue."""

    if key == KEY_Q or key == KEY_ESC:
        return True

    # Spacing
    elif key == KEY_LBRACKET:
        params.spacing = max(params.SPACING_MIN, params.spacing - 1)
        print("OK: Spacing = {}".format(params.spacing))

    elif key == KEY_RBRACKET:
        params.spacing = min(params.SPACING_MAX, params.spacing + 1)
        print("OK: Spacing = {}".format(params.spacing))

    # Dot scale
    elif key == KEY_MINUS:
        params.dot_scale = max(
            params.DOT_SCALE_MIN,
            round(params.dot_scale - params.DOT_SCALE_STEP, 1),
        )
        print("OK: Dot scale = {:.1f}".format(params.dot_scale))

    elif key == KEY_EQUALS:
        params.dot_scale = min(
            params.DOT_SCALE_MAX,
            round(params.dot_scale + params.DOT_SCALE_STEP, 1),
        )
        print("OK: Dot scale = {:.1f}".format(params.dot_scale))

    # Brightness (up/down)
    elif key in (KEY_UP, KEY_UP_ALT):
        params.brightness = min(
            params.BRIGHTNESS_MAX,
            params.brightness + params.BRIGHTNESS_STEP,
        )
        print("OK: Brightness = {}".format(params.brightness))

    elif key in (KEY_DOWN, KEY_DOWN_ALT):
        params.brightness = max(
            params.BRIGHTNESS_MIN,
            params.brightness - params.BRIGHTNESS_STEP,
        )
        print("OK: Brightness = {}".format(params.brightness))

    # Contrast (left/right)
    elif key in (KEY_LEFT, KEY_LEFT_ALT):
        params.contrast = max(
            params.CONTRAST_MIN,
            round(params.contrast - params.CONTRAST_STEP, 1),
        )
        print("OK: Contrast = {:.1f}".format(params.contrast))

    elif key in (KEY_RIGHT, KEY_RIGHT_ALT):
        params.contrast = min(
            params.CONTRAST_MAX,
            round(params.contrast + params.CONTRAST_STEP, 1),
        )
        print("OK: Contrast = {:.1f}".format(params.contrast))

    # Algorithm switching
    elif key == KEY_1:
        params.algorithm = "halftone"
        print("OK: Algorithm = Halftone (dithertone)")

    elif key == KEY_2:
        params.algorithm = "ordered"
        print("OK: Algorithm = Ordered (Bayer 8x8)")

    elif key == KEY_3:
        params.algorithm = "floyd_steinberg"
        print("OK: Algorithm = Floyd-Steinberg (slow, best for screenshots)")

    # Invert
    elif key == KEY_I:
        params.invert = not params.invert
        state = "ON" if params.invert else "OFF"
        print("OK: Invert = {}".format(state))

    # Screenshot
    elif key == KEY_S:
        if last_dithered is not None:
            png_path, pdf_path = save_screenshot_with_pdf(
                last_dithered, output_dir,
                paper_size=paper_size, generate_pdf=generate_pdf,
            )
            print("OK: Screenshot saved to {}".format(png_path))
            if pdf_path:
                print("OK: PIAF PDF saved to {}".format(pdf_path))
        else:
            print("ERROR: No frame to capture")

    # Bracket
    elif key == KEY_B:
        if last_dithered is not None:
            _save_bracket_from_params(params, last_dithered, output_dir,
                                      paper_size, generate_pdf)
        else:
            print("ERROR: No frame to capture")

    # Help
    elif key == KEY_H:
        print("OK: {}".format(params.summary()))

    return False


def _save_bracket_from_params(params, gray_frame, output_dir, paper_size,
                              generate_pdf):
    """Generate and save 3 bracket variants from the current gray frame."""
    base_spacing = params.spacing
    variants = {
        "tight": max(params.SPACING_MIN, int(base_spacing * 0.7)),
        "medium": base_spacing,
        "loose": min(params.SPACING_MAX, int(base_spacing * 1.3)),
    }

    frames = {}
    for label, sp in variants.items():
        frames[label] = dither(
            gray_frame,
            algorithm=params.algorithm,
            spacing=sp,
            dot_scale=params.dot_scale,
            brightness=params.brightness,
            contrast=params.contrast,
            invert=params.invert,
        )

    results = save_bracket(frames, output_dir, paper_size=paper_size,
                           generate_pdf=generate_pdf)
    for label, png_path, pdf_path in results:
        print("OK: Bracket {} saved to {}".format(label, png_path))
    print("OK: Bracket complete — tight(sp={}), medium(sp={}), loose(sp={})".format(
        variants["tight"], variants["medium"], variants["loose"],
    ))


def run_webcam(camera_index=0, resolution=(640, 480), params=None,
               output_dir="./captures", paper_size="letter",
               generate_pdf=True, verbose=False):
    """Main webcam loop with live dithered preview.

    Args:
        camera_index: camera device index.
        resolution: tuple (width, height).
        params: DitherParams instance (created with defaults if None).
        output_dir: directory for screenshots.
        paper_size: PIAF paper size for PDF export.
        generate_pdf: generate PDF alongside screenshots.
        verbose: print extra info.
    """
    if params is None:
        params = DitherParams()

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("ERROR: Could not open camera {}".format(camera_index))
        return

    w, h = resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("OK: Webcam dithering started — camera {}, {}x{}".format(
        camera_index, actual_w, actual_h))
    print("OK: {}".format(params.summary()))
    _print_controls()
    print("READY:")

    window_name = "Webcam Dither"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    last_gray = None
    last_dithered = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read from camera")
                break

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            last_gray = gray

            # Apply dithering
            dithered = dither(
                gray,
                algorithm=params.algorithm,
                spacing=params.spacing,
                dot_scale=params.dot_scale,
                brightness=params.brightness,
                contrast=params.contrast,
                invert=params.invert,
            )
            last_dithered = dithered

            cv2.imshow(window_name, dithered)

            # waitKeyEx captures arrow keys properly
            key = cv2.waitKeyEx(1) & 0xFFFFFF
            if key == 0xFFFFFF:
                # No key pressed
                continue

            should_quit = _handle_key(
                key, params, last_dithered, output_dir, paper_size,
                generate_pdf,
            )
            if should_quit:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("OK: Exiting webcam dither")
        print("READY:")
