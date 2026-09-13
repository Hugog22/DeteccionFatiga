"""
Módulo de alertas: evalúa las métricas y dispara alertas visuales/sonoras.
"""

import time
import os
import platform


class AlertManager:
    """
    Evalúa métricas frame a frame y decide cuándo disparar alertas.
    Mantiene contadores de frames consecutivos para evitar falsos positivos.
    """

    def __init__(
        self,
        ear_threshold=0.22,
        ear_consec_frames=15,
        perclos_threshold=40.0,
        head_pitch_threshold=20.0,
        head_yaw_threshold=30.0,
        head_consec_frames=10,
        sound_enabled=True,
        cooldown_seconds=3.0,
    ):
        self.ear_threshold = ear_threshold
        self.ear_consec_frames = ear_consec_frames
        self.perclos_threshold = perclos_threshold
        self.head_pitch_threshold = head_pitch_threshold
        self.head_yaw_threshold = head_yaw_threshold
        self.head_consec_frames = head_consec_frames
        self.sound_enabled = sound_enabled
        self.cooldown_seconds = cooldown_seconds

        # Contadores internos
        self._ear_counter = 0
        self._head_counter = 0
        self._last_sound_time = 0.0

    def evaluate(self, ear_avg, perclos, pitch, yaw):
        """
        Evalúa las métricas del frame actual.

        Devuelve un dict con:
          - alerts: lista de strings con las alertas activas
          - ear_closed: bool, si EAR está por debajo del umbral
          - ear_consec: int, frames consecutivos con ojo cerrado
          - head_alert: bool, si la cabeza está fuera de rango
        """
        alerts = []

        # --- EAR: cierre prolongado ---
        if ear_avg < self.ear_threshold:
            self._ear_counter += 1
        else:
            self._ear_counter = 0

        if self._ear_counter >= self.ear_consec_frames:
            alerts.append("⚠️ OJOS CERRADOS - ¡DESPIERTA!")

        # --- PERCLOS ---
        if perclos > self.perclos_threshold:
            alerts.append(f"⚠️ PERCLOS ALTO ({perclos:.0f}%) - SOMNOLENCIA")

        # --- Head pose ---
        head_out = False
        if pitch > self.head_pitch_threshold:
            head_out = True
        if abs(yaw) > self.head_yaw_threshold:
            head_out = True

        if head_out:
            self._head_counter += 1
        else:
            self._head_counter = 0

        if self._head_counter >= self.head_consec_frames:
            alerts.append("⚠️ CABECEO DETECTADO - ¡ATENCIÓN!")

        # --- Sonido ---
        if alerts and self.sound_enabled:
            self._try_beep()

        return {
            "alerts": alerts,
            "ear_closed": ear_avg < self.ear_threshold,
            "ear_consec": self._ear_counter,
            "head_alert": head_out,
        }

    def _try_beep(self):
        """Emite un beep del sistema respetando el cooldown."""
        now = time.time()
        if now - self._last_sound_time < self.cooldown_seconds:
            return

        self._last_sound_time = now
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                os.system("afplay /System/Library/Sounds/Sosumi.aiff &")
            elif system == "Linux":
                os.system("paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga &")
            elif system == "Windows":
                import winsound
                winsound.Beep(1000, 500)
        except Exception:
            pass  # Silenciar errores de audio
