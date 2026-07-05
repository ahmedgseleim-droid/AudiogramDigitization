# app.py — web wrapper around the AudiogramDigitization model
import subprocess, tempfile, os, json
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# allow your hosted tool (GitHub Pages, etc.) to call this server
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/digitize")
async def digitize(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "img.png")[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        img_path = tmp.name
    try:
        # NOTE: this runs the repo's digitize script and expects JSON on stdout.
        # If the repo's command is different, change the list below to match its README.
        out = subprocess.run(
            ["python", "src/digitize.py", "-i", img_path],
            capture_output=True, text=True, timeout=180
        )
        text = (out.stdout or "").strip()
        try:
            return json.loads(text)
        except Exception:
            return {"error": "could not parse model output",
                    "raw": text[:800], "stderr": (out.stderr or "")[:800]}
    finally:
        try: os.remove(img_path)
        except Exception: pass
