# Detección de fatiga al volante

Aplicación de visión por computador que analiza vídeo de una cámara web o de un archivo para mostrar indicadores relacionados con el estado del conductor. El programa detecta landmarks faciales con MediaPipe y calcula la apertura de los ojos (EAR), PERCLOS y una estimación de la orientación de la cabeza. Puede mostrar alertas visuales y emitir avisos sonoros.

El proyecto es experimental y no sustituye sistemas certificados de seguridad ni debe utilizarse como único medio para determinar si una persona está en condiciones de conducir.

## Requisitos

- Python 3.8 o posterior.
- Una cámara web para el modo en directo, o un archivo de vídeo compatible con OpenCV.
- El modelo `face_landmarker.task` de MediaPipe Face Landmarker. Descárgalo desde la [documentación de MediaPipe](https://developers.google.com/mediapipe/solutions/vision/face_landmarker) y colócalo en el directorio raíz del proyecto, junto a `landmarks.py`.

## Instalación

Clona el repositorio y crea un entorno virtual:

```bash
git clone https://github.com/Hugog22/DeteccionFatiga.git
cd DeteccionFatiga
python -m venv .venv
```

Activa el entorno e instala las dependencias:

```bash
# macOS o Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Antes de ejecutar la aplicación, comprueba que `face_landmarker.task` está en el directorio del proyecto. El repositorio no incluye este archivo de modelo.

## Uso

Inicia la cámara predeterminada:

```bash
python main.py
```

Procesa un archivo de vídeo:

```bash
python main.py --video ruta/al/video.mp4
```

Desactiva el sonido de las alertas:

```bash
python main.py --no-sound
```

Se puede combinar `--video` con `--no-sound`. Durante la ejecución, pulsa `q` o `Esc` para salir, o `s` para guardar una captura PNG en el directorio actual.

## Configuración

Los parámetros se definen en `config.py`. Entre ellos están el índice y la resolución solicitada a la cámara, los umbrales de EAR y PERCLOS, la ventana de cálculo de PERCLOS, los límites de orientación de la cabeza y la configuración de alertas.

Los umbrales dependen de la cámara, la iluminación y la persona. Los valores incluidos son parámetros iniciales del proyecto y deben ajustarse y validarse para cada entorno; no representan umbrales clínicos ni garantizan la detección de fatiga.

## Estructura

| Archivo | Responsabilidad |
| --- | --- |
| `main.py` | Argumentos de línea de comandos y bucle principal de vídeo. |
| `capture.py` | Captura de frames desde cámara o archivo mediante OpenCV. |
| `landmarks.py` | Detección facial y conversión de landmarks a píxeles. |
| `metrics.py` | Cálculo de EAR, PERCLOS y pose de la cabeza. |
| `alerts.py` | Evaluación de condiciones de alerta y avisos sonoros. |
| `renderer.py` | Visualización de métricas y alertas sobre el vídeo. |
| `config.py` | Parámetros de cámara y umbrales del sistema. |

## Dependencias

Las dependencias de Python están fijadas o acotadas en [`requirements.txt`](requirements.txt): MediaPipe, OpenCV y NumPy.
