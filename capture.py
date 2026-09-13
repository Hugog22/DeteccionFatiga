"""
Módulo de captura de vídeo.
Encapsula OpenCV VideoCapture para facilitar reutilización y limpieza.
"""

import cv2


class VideoCapture:
    """Wrapper sobre cv2.VideoCapture con configuración de resolución."""

    def __init__(self, source=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara (índice {source})")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Leer FPS real de la cámara (fallback a 30)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 30.0

    def read(self):
        """Devuelve (success, frame). El frame es BGR de OpenCV."""
        return self.cap.read()

    def release(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()
