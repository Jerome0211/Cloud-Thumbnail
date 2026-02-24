# REST Thumbnail Creation Service

A production-ready REST API service built with FastAPI that dynamically resizes images into thumbnails while preserving the aspect ratio.

## Features
- **Concurrent Processing:** Handles multiple image uploads simultaneously.
- **Aspect Ratio Preservation:** Automatically scales images within boundaries without distortion.
- **Flexible Resizing:** Supports presets (`small`, `medium`, `large`) or custom `width`/`height` parameters.
- **Auto-generated Docs:** Interactive Swagger UI available out-of-the-box.

## How to Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt