"""
Módulo de métricas geométricas: EAR, PERCLOS, Head Pose.

Cada función toma landmarks (array Nx3 normalizado) y devuelve
los valores numéricos correspondientes.
"""

import math
from collections import deque
import time

import cv2
import numpy as np


# ============================================================
# Índices de landmarks de MediaPipe Face Mesh para cada ojo
# (basados en la malla de 468+10 puntos con refine_landmarks=True)
# ============================================================

# Ojo izquierdo (desde la perspectiva de la persona)
LEFT_EYE_IDX = {
    "outer": 263,   # comisura externa
    "inner": 362,   # comisura interna
    "top1": 386,    # párpado superior
    "top2": 385,
    "bottom1": 374, # párpado inferior
    "bottom2": 380,
}

# Ojo derecho
RIGHT_EYE_IDX = {
    "outer": 33,
    "inner": 133,
    "top1": 159,
    "top2": 158,
    "bottom1": 145,
    "bottom2": 153,
}

# Puntos de referencia para solvePnP (nariz, barbilla, ojos, boca)
FACE_3D_MODEL = np.array([
    (0.0, 0.0, 0.0),           # Punta de la nariz
    (0.0, -330.0, -65.0),      # Barbilla
    (-225.0, 170.0, -135.0),   # Comisura ojo izquierdo
    (225.0, 170.0, -135.0),    # Comisura ojo derecho
    (-150.0, -150.0, -125.0),  # Comisura boca izquierda
    (150.0, -150.0, -125.0),   # Comisura boca derecha
], dtype=np.float64)

# Índices de MediaPipe correspondientes al modelo 3D anterior
FACE_2D_LANDMARK_IDX = [1, 152, 263, 33, 287, 57]


# ============================================================
# EAR (Eye Aspect Ratio)
# ============================================================

def _distance(p1, p2):
    """Distancia euclidiana entre dos puntos (x, y) o (x, y, z)."""
    return np.linalg.norm(np.array(p1) - np.array(p2))


def compute_ear(landmarks, eye_idx):
    """
    Calcula el Eye Aspect Ratio para un ojo.

    EAR = (|P2-P6| + |P3-P5|) / (2 * |P1-P4|)

    Donde P1-P4 es la distancia horizontal (comisuras)
    y P2-P6, P3-P5 son las distancias verticales (párpados).
    """
    p_outer = landmarks[eye_idx["outer"]]
    p_inner = landmarks[eye_idx["inner"]]
    p_top1 = landmarks[eye_idx["top1"]]
    p_top2 = landmarks[eye_idx["top2"]]
    p_bot1 = landmarks[eye_idx["bottom1"]]
    p_bot2 = landmarks[eye_idx["bottom2"]]

    # Distancias verticales
    vert1 = _distance(p_top1, p_bot1)
    vert2 = _distance(p_top2, p_bot2)

    # Distancia horizontal
    horiz = _distance(p_outer, p_inner)

    if horiz < 1e-6:
        return 0.0

    ear = (vert1 + vert2) / (2.0 * horiz)
    return ear


def compute_both_ears(landmarks):
    """Devuelve (ear_left, ear_right, ear_avg)."""
    ear_left = compute_ear(landmarks, LEFT_EYE_IDX)
    ear_right = compute_ear(landmarks, RIGHT_EYE_IDX)
    ear_avg = (ear_left + ear_right) / 2.0
    return ear_left, ear_right, ear_avg


# ============================================================
# PERCLOS
# ============================================================

class PerclosTracker:
    """
    Mantiene una ventana deslizante de registros (timestamp, ojo_cerrado)
    y calcula el % de tiempo con ojos cerrados (PERCLOS).
    """

    def __init__(self, window_seconds=60.0, ear_threshold=0.22):
        self.window_seconds = window_seconds
        self.ear_threshold = ear_threshold
        # deque de tuplas (timestamp, is_closed: bool)
        self._buffer = deque()

    def update(self, ear_avg, timestamp=None):
        """Registra un nuevo frame. Devuelve PERCLOS actual (0-100%)."""
        if timestamp is None:
            timestamp = time.time()

        is_closed = ear_avg < self.ear_threshold
        self._buffer.append((timestamp, is_closed))

        # Purgar entradas fuera de la ventana temporal
        cutoff = timestamp - self.window_seconds
        while self._buffer and self._buffer[0][0] < cutoff:
            self._buffer.popleft()

        return self._compute()

    def _compute(self):
        if not self._buffer:
            return 0.0

        closed_count = sum(1 for _, closed in self._buffer if closed)
        perclos = (closed_count / len(self._buffer)) * 100.0
        return perclos


# ============================================================
# Head Pose Estimation (Pitch / Yaw / Roll)
# ============================================================

def compute_head_pose(landmarks, frame_width, frame_height):
    """
    Estima la orientación de la cabeza usando solvePnP.

    Devuelve (pitch, yaw, roll) en grados.
    - pitch negativo = cabeza inclinada hacia abajo (cabeceo)
    - yaw positivo = mirar a la derecha; negativo = mirar a la izquierda
    """
    # Extraer los 6 puntos 2D correspondientes
    image_points = np.array([
        (landmarks[idx][0] * frame_width, landmarks[idx][1] * frame_height)
        for idx in FACE_2D_LANDMARK_IDX
    ], dtype=np.float64)

    # Parámetros intrínsecos aproximados de la cámara
    focal_length = frame_width
    center = (frame_width / 2.0, frame_height / 2.0)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1],
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))  # Sin distorsión

    success, rotation_vec, translation_vec = cv2.solvePnP(
        FACE_3D_MODEL,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return 0.0, 0.0, 0.0

    # Convertir vector de rotación a matriz y extraer ángulos de Euler
    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    proj_matrix = np.hstack((rotation_mat, translation_vec))
    euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)[6]

    pitch = euler_angles[0, 0]
    yaw = euler_angles[1, 0]
    roll = euler_angles[2, 0]

    # Normalizar ángulos al rango [-180, 180]
    for angle_name in ['pitch', 'yaw', 'roll']:
        val = locals()[angle_name]
        if val > 180:
            val -= 360
        locals()[angle_name]  # no-op, usamos directamente
    if pitch > 180:
        pitch -= 360
    if yaw > 180:
        yaw -= 360
    if roll > 180:
        roll -= 360

    return pitch, yaw, roll
