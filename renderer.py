"""
Módulo de renderizado: dibuja métricas y alertas sobre el frame de vídeo.
"""

import cv2
import numpy as np


# Colores (BGR)
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (255, 255, 0)


def draw_landmarks_eyes(frame, landmarks_px, left_idx, right_idx):
    """Dibuja los puntos de los ojos sobre el frame."""
    for eye_idx in [left_idx, right_idx]:
        pts = [landmarks_px[eye_idx[k]] for k in eye_idx]
        for (x, y) in pts:
            cv2.circle(frame, (x, y), 2, CYAN, -1)


def draw_metrics_hud(frame, ear_left, ear_right, ear_avg, perclos, pitch, yaw, roll):
    """Dibuja el panel de métricas en la esquina superior izquierda."""
    h, w = frame.shape[:2]

    # Fondo semitransparente para el HUD
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (340, 200), BLACK, -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Color del EAR según estado
    ear_color = GREEN if ear_avg >= 0.22 else RED

    y0 = 35
    dy = 25
    cv2.putText(frame, f"EAR L: {ear_left:.3f}  R: {ear_right:.3f}",
                (20, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 1)

    cv2.putText(frame, f"EAR AVG: {ear_avg:.3f}",
                (20, y0 + dy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ear_color, 2)

    perclos_color = GREEN if perclos < 40 else (YELLOW if perclos < 60 else RED)
    cv2.putText(frame, f"PERCLOS: {perclos:.1f}%",
                (20, y0 + 2 * dy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, perclos_color, 2)

    cv2.putText(frame, f"Pitch: {pitch:.1f}  Yaw: {yaw:.1f}  Roll: {roll:.1f}",
                (20, y0 + 3 * dy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)

    # Barra visual de PERCLOS
    bar_x, bar_y, bar_w, bar_h = 20, y0 + 4 * dy, 300, 15
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), WHITE, 1)
    fill_w = int(bar_w * min(perclos / 100.0, 1.0))
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), perclos_color, -1)
    cv2.putText(frame, "PERCLOS", (bar_x + bar_w + 5, bar_y + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1)


def draw_alerts(frame, alerts):
    """Dibuja alertas prominentes en la parte inferior de la pantalla."""
    if not alerts:
        return

    h, w = frame.shape[:2]

    # Flash rojo en los bordes
    cv2.rectangle(frame, (0, 0), (w, h), RED, 8)

    # Texto de cada alerta
    for i, alert_text in enumerate(alerts):
        y_pos = h - 50 - i * 40
        # Sombra
        cv2.putText(frame, alert_text, (52, y_pos + 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, BLACK, 3)
        # Texto
        cv2.putText(frame, alert_text, (50, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, RED, 2)


def draw_face_not_found(frame):
    """Muestra mensaje cuando no se detecta cara."""
    h, w = frame.shape[:2]
    cv2.putText(frame, "No se detecta rostro",
                (w // 2 - 180, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, YELLOW, 2)
