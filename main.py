#!/usr/bin/env python3
"""
main.py — Sistema de Detección de Fatiga al Volante

Ejecuta el pipeline completo:
  Webcam → Face Mesh → Métricas (EAR, PERCLOS, Head Pose) → Alertas

Uso:
  python main.py              # webcam en vivo
  python main.py --video ruta/al/video.mp4  # desde archivo de vídeo

Controles:
  q / ESC  → Salir
  s        → Guardar screenshot
"""

import argparse
import time
import cv2

import config
from capture import VideoCapture
from landmarks import FaceMeshDetector, landmarks_to_pixel
from metrics import (
    compute_both_ears,
    compute_head_pose,
    PerclosTracker,
    LEFT_EYE_IDX,
    RIGHT_EYE_IDX,
)
from alerts import AlertManager
from renderer import (
    draw_landmarks_eyes,
    draw_metrics_hud,
    draw_alerts,
    draw_face_not_found,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Detección de Fatiga al Volante")
    parser.add_argument("--video", type=str, default=None,
                        help="Ruta a vídeo (si no se especifica, usa webcam)")
    parser.add_argument("--no-sound", action="store_true",
                        help="Desactivar alertas sonoras")
    return parser.parse_args()


def main():
    args = parse_args()

    # --- Inicialización ---
    source = args.video if args.video else config.CAMERA_INDEX
    cam = VideoCapture(source, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)

    detector = FaceMeshDetector(
        max_faces=config.MAX_NUM_FACES,
        min_detection_conf=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_conf=config.MIN_TRACKING_CONFIDENCE,
    )

    perclos_tracker = PerclosTracker(
        window_seconds=config.PERCLOS_WINDOW_SECONDS,
        ear_threshold=config.EAR_THRESHOLD,
    )

    alert_manager = AlertManager(
        ear_threshold=config.EAR_THRESHOLD,
        ear_consec_frames=config.EAR_CONSEC_FRAMES_ALERT,
        perclos_threshold=config.PERCLOS_THRESHOLD,
        head_pitch_threshold=config.HEAD_PITCH_THRESHOLD,
        head_yaw_threshold=config.HEAD_YAW_THRESHOLD,
        head_consec_frames=config.HEAD_CONSEC_FRAMES_ALERT,
        sound_enabled=config.SOUND_ALERT_ENABLED and not args.no_sound,
        cooldown_seconds=config.ALERT_COOLDOWN_SECONDS,
    )

    fps_counter = 0
    fps_display = 0.0
    fps_timer = time.time()

    print("[INFO] Sistema de detección de fatiga iniciado.")
    print("[INFO] Pulsa 'q' o ESC para salir, 's' para screenshot.")

    try:
        while True:
            success, frame = cam.read()
            if not success:
                if args.video:
                    print("[INFO] Fin del vídeo.")
                    break
                continue

            h, w = frame.shape[:2]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # --- Detección de landmarks ---
            faces = detector.process(frame_rgb)

            if faces:
                landmarks = faces[0]  # Primera cara detectada

                # --- Métricas ---
                ear_left, ear_right, ear_avg = compute_both_ears(landmarks)

                now = time.time()
                perclos = perclos_tracker.update(ear_avg, timestamp=now)

                pitch, yaw, roll = compute_head_pose(landmarks, w, h)

                # --- Alertas ---
                result = alert_manager.evaluate(ear_avg, perclos, pitch, yaw)

                # --- Renderizado ---
                landmarks_px = landmarks_to_pixel(landmarks, w, h)
                draw_landmarks_eyes(frame, landmarks_px, LEFT_EYE_IDX, RIGHT_EYE_IDX)
                draw_metrics_hud(frame, ear_left, ear_right, ear_avg,
                                 perclos, pitch, yaw, roll)

                if result["alerts"]:
                    draw_alerts(frame, result["alerts"])
            else:
                draw_face_not_found(frame)

            # --- FPS ---
            fps_counter += 1
            elapsed = time.time() - fps_timer
            if elapsed >= 1.0:
                fps_display = fps_counter / elapsed
                fps_counter = 0
                fps_timer = time.time()

            cv2.putText(frame, f"FPS: {fps_display:.0f}",
                        (w - 130, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0), 2)

            # --- Mostrar ---
            cv2.imshow("Deteccion de Fatiga", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):  # q o ESC
                break
            elif key == ord("s"):
                filename = f"screenshot_{int(time.time())}.png"
                cv2.imwrite(filename, frame)
                print(f"[INFO] Screenshot guardado: {filename}")

    finally:
        cam.release()
        detector.close()
        cv2.destroyAllWindows()
        print("[INFO] Sistema cerrado.")


if __name__ == "__main__":
    main()
