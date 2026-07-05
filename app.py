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
        # Save the uploaded image with a known basename ("image.<ext>")
        img_path = os.path.join(tmp_in, "image" + suffix)
        with open(img_path, "wb") as f:
            f.write(await file.read())

        # Run the repo's actual digitization script
        out = subprocess.run(
            ["python", "src/digitize_report.py", "-i", img_path, "-o", tmp_out],
            capture_output=True, text=True, timeout=180
        )

        # The script writes <basename>.json into tmp_out — find it
        json_files = glob.glob(os.path.join(tmp_out, "*.json"))

        debug_info = {
            "stdout": (out.stdout or "")[:1500],
            "stderr": (out.stderr or "")[:1500],
        }

        if json_files:
            with open(json_files[0]) as f:
                data = json.load(f)
            return {"result": data, "debug": debug_info}
        else:
            return {
                "error": "no output produced by digitize_report.py",
                **debug_info,
            }