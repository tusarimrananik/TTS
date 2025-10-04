# Text-to-Speech (TTS) with Coqui XTTS v2

This project demonstrates how to use the **Coqui TTS (XTTS v2)** model for text-to-speech conversion with custom voice cloning.

---

## 🚀 Features
- Multilingual TTS using **XTTS v2**.
- Custom speaker cloning with an audio sample.
- Output audio saved directly as `.wav` files.
- Compatible with **Windows (Python virtual environment)**.

---

## ⚙️ Requirements

### Python Version
- **Python 3.10.x** (Recommended)

### Dependencies
Install the following main dependencies:

```bash
pip install TTS==0.22.0
pip install torch==2.5.1
pip install torchaudio==2.5.1
pip install soundfile==0.12.1
pip install librosa==0.10.2.post1
⚠️ Make sure torch and torchaudio versions match.
Example: torch==2.5.1 works with torchaudio==2.5.1.

🐛 Errors You May Encounter & Fixes
1. ImportError: cannot import name 'BeamSearchScorer' from 'transformers'
Cause: Wrong version of transformers.

Fix:

bash
Copy code
pip install transformers==4.44.2
2. FileNotFoundError: model.pth not found
Cause: Model weights not downloaded.

Fix:

python
Copy code
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
This auto-downloads weights to your ~/.local/share/tts or Windows equivalent.

3. _pickle.UnpicklingError: Weights only load failed
Cause: PyTorch 2.6+ changed default torch.load behavior.

Fix: Downgrade PyTorch:

bash
Copy code
pip uninstall torch torchaudio
pip install torch==2.5.1 torchaudio==2.5.1
4. soundfile.LibsndfileError: Error opening 'Brain.mp3'
Cause: .mp3 is not supported by soundfile.

Fix: Convert audio to .wav:

bash
Copy code
ffmpeg -i Brain.mp3 Brain.wav
Then use:

python
Copy code
speaker_wav="Brain.wav"
▶️ Usage
Example main.py:

python
Copy code
from TTS.api import TTS

# Load XTTS v2 model
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Run inference
tts.tts_to_file(
    text="There are four things you must never do if you want to rise.",
    file_path="output.wav",
    speaker_wav="Brain.wav",   # Speaker audio sample (must be .wav)
    language="en"
)
Run with:

bash
Copy code
python main.py
Output: output.wav

📂 Project Structure
bash
Copy code
TTS/
│── main.py
│── Brain.wav
│── README.md
│── .gitignore
│── venv/        # Virtual environment
🔥 Notes
Always use .wav speaker files, not .mp3.

Make sure Python is 3.10 for maximum compatibility.

If you update Torch in future, check if Coqui supports that version.

👨‍💻 Author
Created with Coqui TTS and tested on Windows 10.

yaml
Copy code

---

👉 Copy everything above into a file named **`README.md`** in your project folder.  

Do you also want me to generate a **`.gitignore`** file content here (so you can paste it too)?