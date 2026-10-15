import uvicorn
import webbrowser
import threading
import os
import subprocess
import platform
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from jarvis.brain import think
from jarvis.memory import save_message, get_history, clear_history, log_command
from jarvis.commands.vision import full_scan, detect_objects, capture_frame, describe_scene
from jarvis.config import JARVIS_NAME, VISION_SCAN_MARKER
import json
import psutil

app = FastAPI(title="Marco AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/api/system")
async def api_system():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    battery = psutil.sensors_battery()
    uptime = psutil.boot_time()
    net = psutil.net_io_counters()
    return {
        "cpu_percent": cpu,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 1),
        "ram_total_gb": round(ram.total / (1024**3), 1),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024**3), 1),
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "battery_percent": battery.percent if battery else None,
        "battery_plugged": battery.power_plugged if battery else None,
        "platform": platform.system(),
        "hostname": platform.node(),
        "net_sent_mb": round(net.bytes_sent / (1024**2), 1),
        "net_recv_mb": round(net.bytes_recv / (1024**2), 1),
    }


@app.get("/api/history")
async def api_history():
    history = get_history(limit=50)
    return {"messages": history}


@app.post("/api/clear")
async def api_clear():
    clear_history()
    return {"status": "ok"}


@app.post("/api/action")
async def api_action(payload: dict):
    action = payload.get("action", "")
    param = payload.get("param", "")

    actions = {
        "open_browser": lambda: subprocess.Popen(["start", "https://www.google.com"], shell=True),
        "open_youtube": lambda: subprocess.Popen(["start", "https://www.youtube.com"], shell=True),
        "open_github": lambda: subprocess.Popen(["start", "https://www.github.com"], shell=True),
        "open_chatgpt": lambda: subprocess.Popen(["start", "https://chat.openai.com"], shell=True),
        "open_notepad": lambda: subprocess.Popen(["notepad.exe"]),
        "open_calculator": lambda: subprocess.Popen(["calc.exe"]),
        "open_cmd": lambda: subprocess.Popen(["cmd.exe"]),
        "open_explorer": lambda: subprocess.Popen(["explorer.exe"]),
        "open_vscode": lambda: subprocess.Popen(["code"], shell=True),
        "open_spotify": lambda: subprocess.Popen(["start", "spotify:"], shell=True),
        "screenshot": lambda: subprocess.Popen(
            ["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen | ForEach-Object { $bounds = $_.Bounds; $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height); $gfx = [System.Drawing.Graphics]::FromImage($bmp); $gfx.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.Size); $path = \"$HOME\\Desktop\\screenshot_$(Get-Date -f yyyyMMdd_HHmmss).png\"; $bmp.Save($path); $gfx.Dispose(); $bmp.Dispose(); Write-Output $path }"],
            shell=True,
        ),
        "lock_pc": lambda: subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"]),
        "empty_recycle": lambda: subprocess.Popen(
            ["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
            shell=True,
        ),
    }

    if action == "open_url" and param:
        web_url = param if param.startswith("http") else f"https://{param}"
        subprocess.Popen(["start", web_url], shell=True)
        log_command("open_url", {"url": web_url}, "success", f"Opened {web_url}")
        return {"status": "ok", "message": f"Opened {web_url}"}

    if action in actions:
        try:
            actions[action]()
            log_command(action, {}, "success", f"Executed {action}")
            return {"status": "ok", "message": f"Executed {action}"}
        except Exception as e:
            log_command(action, {}, "error", str(e))
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": f"Unknown action: {action}"}


@app.post("/api/vision")
async def api_vision():
    try:
        description, detections = full_scan()
        log_command("vision_scan_web", {"detections": detections}, "success", description)
        return {"description": description, "detections": detections}
    except Exception as e:
        return {"description": f"Vision error: {str(e)}", "detections": []}


@app.post("/api/vision/frame")
async def api_vision_frame():
    try:
        frame = capture_frame()
        if frame is None:
            return {"error": "Could not access camera"}
        detections = detect_objects(frame)
        labels = list(set(d["label"] for d in detections))
        return {"detections": detections, "labels": labels, "count": len(detections)}
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_input = msg.get("message", "")

            if not user_input:
                continue

            if user_input.lower().strip() in ("exit", "quit", "clear"):
                clear_history()
                await websocket.send_text(json.dumps({
                    "type": "assistant",
                    "message": "Memory cleared. Fresh start, sir.",
                }))
                continue

            reply = think(user_input)

            if reply.strip() == VISION_SCAN_MARKER:
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": "Activating visual scan...",
                }))
                try:
                    description, detections = full_scan()
                    labels = list(set(d["label"] for d in detections))
                    await websocket.send_text(json.dumps({
                        "type": "vision",
                        "description": description,
                        "detections": detections,
                        "labels": labels,
                    }))
                    final_reply = think(f"I just scanned the environment and found: {', '.join(labels) if labels else 'nothing distinct'}. {description}")
                    await websocket.send_text(json.dumps({
                        "type": "assistant",
                        "message": final_reply,
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "assistant",
                        "message": f"I was unable to use the camera at this time. {str(e)}",
                    }))
            else:
                await websocket.send_text(json.dumps({
                    "type": "assistant",
                    "message": reply,
                }))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e),
            }))
        except Exception:
            pass


if __name__ == "__main__":
    print("=" * 50)
    print(f"  {JARVIS_NAME} AI - Web Interface")
    print("  http://localhost:8000")
    print("  Opening browser...")
    print("=" * 50)
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8000")).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
