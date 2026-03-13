"""Webcam capture management.

Wraps OpenCV VideoCapture to support local webcams (by index) and
IP cameras / iPhone streams (by URL).
"""

import cv2


class CaptureError(Exception):
    """Raised when camera cannot be opened or frame cannot be read."""


class WebcamCapture:
    """Manages webcam or IP camera capture via OpenCV.

    Args:
        source: Camera index (int) for local webcam, or URL string
            for IP camera / phone stream (e.g. DroidCam, RTSP).
        width: Requested capture width in pixels.
        height: Requested capture height in pixels.
    """

    def __init__(self, source=0, width=640, height=480):
        self.source = source
        self.width = width
        self.height = height
        self._cap = None

    def open(self):
        """Open the camera. Raises CaptureError if it cannot be opened."""
        self._cap = cv2.VideoCapture(self.source)
        if not self._cap.isOpened():
            kind = "URL" if isinstance(self.source, str) else "index"
            raise CaptureError(
                f"Cannot open camera ({kind}: {self.source}). "
                "Check that the camera is connected and not in use."
            )
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read_frame(self):
        """Read one frame from the camera.

        Returns:
            numpy array (BGR color frame).

        Raises:
            CaptureError: If frame cannot be read.
        """
        if self._cap is None:
            raise CaptureError("Camera not opened. Call open() first.")
        ret, frame = self._cap.read()
        if not ret or frame is None:
            raise CaptureError("Failed to read frame from camera.")
        return frame

    def release(self):
        """Release the camera."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
