# Marco AI - Futuristic Voice Assistant

A full-featured AI assistant inspired by Iron Man's JARVIS, built with Python and a holographic HUD web interface.

## Features

**AI Brain** - GPT-4 powered conversations with persistent memory via Supabase

**Futuristic HUD Interface** - Rotating circular rings, orbiting particles, scanner lines, glassmorphism panels, and audio visualizer

**Voice Input** - Browser-based speech recognition (Chrome)

**Voice Output** - AI speaks responses back with text-to-speech

**YOLO Object Detection** - Real-time object detection through webcam using YOLOv8, described naturally by GPT-4

**System Monitor** - Live CPU, RAM, Disk, and Battery status with animated indicators

**Quick Actions** - One-click system commands (open apps, browser, screenshot, lock PC, etc.)

**Persistent Memory** - All conversations stored in Supabase database, remembers context across sessions

**Activity Log** - Real-time tracking of all actions and commands

## Tech Stack

- Python 3.12
- FastAPI + WebSocket
- OpenAI GPT-4
- Supabase (database)
- YOLOv8 (ultralytics)
- OpenCV
- HTML/CSS/JS (Orbitron font, glassmorphism UI)
- psutil (system monitoring)

## Quick Start

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create Supabase project and run `setup.sql`
4. Add your keys to `.env`
5. Run: `python server.py`
6. Open http://localhost:8000

## Screenshots

[Add a screenshot of your HUD interface here]

## License

MIT
