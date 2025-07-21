# Setting up Vosk Offline Speech Recognition

## Download Vosk Model

1. **For smaller/faster model (40MB):**
   - Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   - Extract to: `D:\Pys\Myra\models\vosk-model-small-en-us-0.15`

2. **For better accuracy (1.8GB) - what you're downloading:**
   - Download: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip  
   - Extract to: `D:\Pys\Myra\models\vosk-model-en-us-0.22`

## Directory Structure
```
D:\Pys\Myra\
├── models\
│   └── vosk-model-en-us-0.22\
│       ├── am\
│       ├── conf\
│       ├── graph\
│       └── ivector
├── venv\
└── requirements.txt
```

## Update your code
Replace this line in `voice_ass_off.py`:
```python
model = Model("path/to/vosk-model")
```

With:
```python
model = Model("D:/Pys/Myra/models/vosk-model-en-us-0.22")
# or for small model:
# model = Model("D:/Pys/Myra/models/vosk-model-small-en-us-0.15")
```

## Additional packages needed
You might need to install these in your Myra environment:
```bash
pip install vosk pyaudio
```
