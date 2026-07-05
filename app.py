# app.py — web wrapper around the AudiogramDigitization model
import subprocess, tempfile, os, json, glob
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

    with tempfile.TemporaryDirectory() as tmp_in, tempfile.TemporaryDirectory() as tmp_out:
        img_path = os.path.join(tmp_in, "image" + suffix)
        with open(img_path, "wb") as f:
            f.write(await file.read())

        out = subprocess.run(
            ["python", "src/digitize_report.py", "-i", img_path, "-o", tmp_out],
            capture_output=True, text=True, timeout=180
        )

        json_files = glob.glob(os.path.join(tmp_out, "*.json"))

        if json_files:
            with open(json_files[0]) as f:
                data = json.load(f)
            return {"result": data}
        else:
            return {
                "error": "no output produced by digitize_report.py",
                "stdout": (out.stdout or "")[:1000],
                "stderr": (out.stderr or "")[:1000],
            }