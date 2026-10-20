# Models kept in the repo

The face detector the recipe uses (PIP-04, F-12). It's small, free and MIT-licensed, so it's committed here and the build and the tests never download it.

| File | What | SHA-256 |
|---|---|---|
| `face_detection_yunet_2023mar.onnx` | YuNet, fixed input shape. For OpenCV 4.x, including OpenCV.js's `FaceDetectorYN`, and for the Python prototype | `8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4` |
| `face_detection_yunet_2026may.onnx` | The same model, re-exported with dynamic height and width. For `onnxruntime-node`, the fallback when OpenCV.js has no `FaceDetectorYN` (architecture.md, "Porting traps") | `ebafce4e3c118d6554634be5c27ab333b4c047a9a8c3faf1d7cf93101c22f0f0` |
| `LICENSE-yunet` | Its licence: MIT, copyright 2020 Shiqi Yu | |

- **Source:** [opencv/opencv_zoo](https://github.com/opencv/opencv_zoo), `models/face_detection_yunet/`, at commit `48b10fa505aeb51fbd127fc60a5c660040e823b7`, copied on 2026-10-20. The files are copied unchanged. Their SHA-256s match the Git LFS pointers at that commit.
- **What it finds:** a face box and five landmarks (the two eyes, the nose tip and the two mouth corners). YuNet finds faces of about 10 to 300 px, so a large original is searched on a reduced copy (F-12).
- **Box format:** OpenCV returns `[x, y, width, height]`. The recipe uses corners, `[x0, y0, x1, y1]` (architecture.md, "Porting traps").
- **Since recipe 0.5.0** the crop's constants are measured with this detector (prototype/README.md).
