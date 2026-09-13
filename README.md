# 🚗 Sistema de Detección de Fatiga al Volante (Driver Drowsiness Detection)

Un sistema de visión artificial en tiempo real diseñado para prevenir accidentes de tráfico mediante la monitorización del estado de alerta del conductor. Utiliza técnicas avanzadas de procesamiento de imágenes y la malla facial de MediaPipe para evaluar el nivel de fatiga y distracción.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-orange)

## ✨ Características Principales

El sistema procesa la señal de vídeo (webcam en vivo o archivo) y calcula en tiempo real métricas críticas:

- **🥱 EAR (Eye Aspect Ratio):** Mide la apertura de los ojos para detectar parpadeos lentos y cierres prolongados.
- **😴 PERCLOS (Percentage of Eyelid Closure):** Calcula el porcentaje de tiempo que los ojos están cerrados (típicamente > 40% indica somnolencia severa).
- **🗣️ Head Pose Estimation (Pose de la cabeza):** Evalúa la inclinación (*pitch*) y el giro (*yaw*) de la cabeza para detectar distracciones (ej. mirar el móvil o cabeceos bruscos).
- **🚨 Sistema de Alertas:** Genera alertas visuales (HUD en pantalla) y sonoras cuando se superan los umbrales de peligro definidos en configuración.

## 🛠️ Tecnologías Utilizadas

- **Python 3:** Lenguaje principal.
- **OpenCV (`cv2`):** Captura de vídeo, procesamiento de fotogramas y renderizado de la interfaz visual (HUD).
- **MediaPipe:** Detección robusta de landmarks faciales (Face Mesh) con aceleración e inferencia de alta precisión.
- **Numpy:** Cálculos matemáticos y manipulaciones de matrices para las métricas geométricas (como `solvePnP` para Head Pose).

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Hugog22/DeteccionFatiga.git
   cd DeteccionFatiga
   ```

2. **Instalar dependencias:**
   Se recomienda usar un entorno virtual (venv).
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar el sistema:**
   - **Usando la webcam (por defecto):**
     ```bash
     python main.py
     ```
   - **Analizando un archivo de vídeo:**
     ```bash
     python main.py --video ruta/al/video.mp4
     ```
   - **Silenciar alertas sonoras:**
     ```bash
     python main.py --no-sound
     ```

## ⚙️ Configuración (`config.py`)

El sistema es altamente parametrizable. En el archivo `config.py` puedes ajustar los umbrales para adaptarlos a tu cámara, iluminación y características físicas:

- `EAR_THRESHOLD`: Umbral de apertura de ojos (típicamente 0.20 - 0.35).
- `EAR_CONSEC_FRAMES_ALERT`: Frames consecutivos por debajo del umbral para disparar alerta.
- `PERCLOS_WINDOW_SECONDS`: Ventana de tiempo (en segundos) para el cálculo de PERCLOS.
- `HEAD_PITCH_THRESHOLD` / `HEAD_YAW_THRESHOLD`: Límites en grados para detectar desvío de la mirada o cabeceo.

## 🎮 Controles durante la ejecución

- `q` o `ESC`: Cerrar la aplicación.
- `s`: Guardar un screenshot del frame actual.

## 📁 Estructura del Proyecto

- `main.py`: Punto de entrada que orquesta el pipeline completo.
- `config.py`: Parámetros globales y umbrales.
- `capture.py`: Manejo del flujo de vídeo.
- `landmarks.py`: Inferencia de MediaPipe y extracción de coordenadas.
- `metrics.py`: Cálculos matemáticos y lógicos (EAR, PERCLOS, Head Pose).
- `alerts.py`: Gestión del estado de alarmas y notificaciones.
- `renderer.py`: Interfaz gráfica sobre OpenCV (dibujo de métricas y HUD).

## 📄 Licencia

Este proyecto está bajo licencia MIT. ¡Siéntete libre de utilizarlo y mejorarlo!
