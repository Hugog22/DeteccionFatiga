"""
Módulo de extracción de landmarks faciales con MediaPipe FaceLandmarker (API v1.0+).
Devuelve landmarks normalizados y utilidades para convertirlos a píxeles.
"""

import os
import numpy as np
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


# Ruta al modelo (relativa al directorio de este archivo)
_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")


class FaceMeshDetector:
    """Detecta face mesh usando FaceLandmarker de MediaPipe Tasks y devuelve landmarks normalizados."""

    def __init__(self, max_faces=1, min_detection_conf=0.5, min_tracking_conf=0.5):
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=_MODEL_PATH,
                delegate=BaseOptions.Delegate.CPU,
            ),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=max_faces,
            min_face_detection_confidence=min_detection_conf,
            min_face_presence_confidence=min_detection_conf,
            min_tracking_confidence=min_tracking_conf,
            output_facial_transformation_matrixes=False,
            output_face_blendshapes=False,
        )
        self.landmarker = FaceLandmarker.create_from_options(options)
        self._frame_count = 0

    def process(self, frame_rgb):
        """
        Procesa un frame RGB (numpy array HxWx3, uint8).
        Devuelve lista de arrays de landmarks (Nx3, coordenadas normalizadas 0-1)
        o lista vacía si no se detectó cara.
        """
        # Convertir numpy array a mp.Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # FaceLandmarker en modo VIDEO necesita timestamps crecientes (ms)
        self._frame_count += 1
        timestamp_ms = self._frame_count

        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.face_landmarks:
            return []

        faces = []
        for face_lm_list in result.face_landmarks:
            # face_lm_list es una lista de NormalizedLandmark
            landmarks = np.array(
                [(lm.x, lm.y, lm.z) for lm in face_lm_list],
                dtype=np.float64,
            )
            faces.append(landmarks)

        return faces

    def close(self):
        self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def landmarks_to_pixel(landmarks, frame_width, frame_height):
    """
    Convierte landmarks normalizados (0-1) a coordenadas de píxel.
    Retorna array Nx2 (x_px, y_px).
    """
    pixel_coords = landmarks[:, :2].copy()
    pixel_coords[:, 0] *= frame_width
    pixel_coords[:, 1] *= frame_height
    return pixel_coords.astype(int)
