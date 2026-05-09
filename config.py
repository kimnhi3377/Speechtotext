import os

FFMPEG_PATH = r"C:\Users\admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ["PATH"]

FS = 16000
MODEL_SIZE = "small"

SILENCE_LIMIT = 3