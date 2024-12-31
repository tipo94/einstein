from fastapi import FastAPI, BackgroundTasks
from services.audio_recording import AudioRecorder
from services.external_oai import send_audio_for_processing

app = FastAPI()

# Instantiate our AudioRecorder with default settings
audio_recorder = AudioRecorder(
    chunk_size=512
)

@app.get("/start_recording")
def start_recording(background_tasks: BackgroundTasks):
    """
    Endpoint that, when called, starts recording from the microphone until silence is detected,
    then sends the audio to an external service, and returns the response.
    """

    # Step 1: Record audio until silence
    recorded_file_path = audio_recorder.record_until_silence()

    # Step 2: Call external service
    result = send_audio_for_processing(recorded_file_path)

    # Step 3: Return the response from the external service
    return {
        "message": "Recording finished and processed successfully.",
        "service_result": result
    }
