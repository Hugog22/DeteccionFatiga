"""
Configuración centralizada de umbrales y parámetros del sistema.
Ajusta estos valores según tu cámara y condiciones de iluminación.
"""

# === Cámara ===
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# === MediaPipe Face Mesh ===
MAX_NUM_FACES = 1
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# === EAR (Eye Aspect Ratio) ===
# Umbral por debajo del cual se considera que el ojo está cerrado.
# Valores típicos: 0.20 - 0.25. Ajustar experimentalmente.
EAR_THRESHOLD = 0.35

# Número de frames consecutivos con EAR bajo para considerar "cierre prolongado"
EAR_CONSEC_FRAMES_ALERT = 40  # ~1.3s a 30fps (evita que un parpadeo normal active la alerta)

# === PERCLOS ===
# Ventana temporal en segundos para calcular PERCLOS
PERCLOS_WINDOW_SECONDS = 60

# Umbral de PERCLOS (%) para disparar alerta.
# PERCLOS > 40% se asocia con somnolencia significativa.
PERCLOS_THRESHOLD = 40.0

# === Pose de cabeza (Head Pose) ===
# Umbral de pitch (cabeceo hacia abajo) en grados para alerta
HEAD_PITCH_THRESHOLD = 0.0  # grados positivos = cabeza inclinada hacia abajo

# Umbral de yaw (giro lateral) en grados para alerta
HEAD_YAW_THRESHOLD = 30.0  # valor absoluto

# Frames consecutivos con pitch/yaw fuera de rango para alerta
HEAD_CONSEC_FRAMES_ALERT = 10  # ~0.33s a 30fps

# === Alertas ===
# Activar alerta sonora (beep del sistema)
SOUND_ALERT_ENABLED = True

# Cooldown entre alertas sonoras en segundos (evitar spam)
ALERT_COOLDOWN_SECONDS = 3.0
