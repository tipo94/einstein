import uvicorn
from fastapi import FastAPI, HTTPException
import sounddevice as sd
import numpy as np
import wave
import queue
import pyaudio
from struct import unpack

app = FastAPI()



def record_audio(
        output_filename="output.wav",
        record_seconds=10,
        silence_threshold=500,  # Amplitude threshold for silence
        silence_duration=2.0  # Seconds of silence before we stop
):
    """
    Records audio until either `record_seconds` elapse OR
    there is a silence of `silence_duration` seconds.
    """

    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  # Mono
    RATE = 44100

    p = pyaudio.PyAudio()

    # If you don't want to pick device_index explicitly, remove 'input_device_index'
    # or set it to the index you need from p.get_device_info_by_index(...).
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=1,
    )

    print("Recording started. Speak into the microphone...")
    frames = []

    # Number of frames that correspond to the desired silence duration
    max_silent_frames = int(silence_duration * (RATE / CHUNK))
    silent_frame_count = 0

    for i in range(int(RATE / CHUNK * record_seconds)):
        # Read audio data
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        # Convert raw bytes to 'short' samples to check amplitude
        samples = unpack("<" + "h" * (len(data) // 2), data)
        peak = max(abs(s) for s in samples)

        # Check if this chunk is silent (peak below threshold)
        if peak < silence_threshold:
            silent_frame_count += 1
        else:
            silent_frame_count = 0

        # If we've accumulated enough silent frames, stop recording
        if silent_frame_count >= max_silent_frames:
            print(f"Detected {silence_duration}s of silence. Stopping early...")
            break

    print("Recording finished.")

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save as WAV
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Audio saved as {output_filename}")

@app.get("/start_recording")
def start_recording_endpoint():
    """
    Endpoint to start recording until silence is detected.
    Triggers a blocking call to record_until_silence() and returns when complete.
    """
    output_file = "my_recording.wav"
    record_audio(output_file, record_seconds=120)
    return {
        "message": "Recording finished due to silence.",
        "filename": output_file
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
