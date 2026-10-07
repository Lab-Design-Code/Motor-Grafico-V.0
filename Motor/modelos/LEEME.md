# Modelos opcionales de detección de rostro

No se incluyen en el repositorio. Dejar aquí, si se quieren usar:

- `face_landmarker.task` — mediapipe FaceLandmarker (mejor precisión)
- `face_detection_yunet_2023mar.onnx` — YuNet (OpenCV DNN)

Sin ninguno, el motor usa Haar, que viene dentro de `opencv-python<5`.
Ver la sección 1 del README.
