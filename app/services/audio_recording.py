import pyaudio
import wave
import time

class AudioRecorder:
    def __init__(self,
                 silence_threshold=500,
                 chunk_size=1024,
                 sample_format=pyaudio.paInt16,
                 channels=1,
                 rate=44100,
                 max_silence_seconds=2):
        self.silence_threshold = silence_threshold
        self.chunk_size = chunk_size
        self.sample_format = sample_format
        self.channels = channels
        self.rate = rate
        self.max_silence_seconds = max_silence_seconds

    def record_until_silence(self, output_filename="output.wav"):
        """
        Record audio from the microphone until a certain period of silence is detected.
        Save the recorded file as 'output.wav' by default.
        """
        p = pyaudio.PyAudio()

        # Print device info
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"Device {i}: {info['name']} "
                  f"Max input channels = {info['maxInputChannels']}")

        stream = p.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=1
        )

        print("Recording started...")
        frames = []
        silent_chunks_in_a_row = 0
        # We define "silence" as amplitude below a certain threshold in each chunk
        # for a certain amount of time.

        while True:
            data = stream.read(self.chunk_size)
            frames.append(data)

            # Check if chunk is silent
            if self._is_silent(data):
                silent_chunks_in_a_row += 1
            else:
                silent_chunks_in_a_row = 0

            # If we've accumulated enough consecutive silent chunks, we stop
            if silent_chunks_in_a_row > (self.rate / self.chunk_size * self.max_silence_seconds):
                break

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("Recording finished. Audio saved:", output_filename)
        return output_filename

    def _is_silent(self, audio_chunk: bytes) -> bool:
        """
        Very naive approach: Convert chunk to integer data and check if
        average amplitude is below the silence_threshold.
        """
        # Note: This is a rudimentary approach. You may want to use more sophisticated methods.
        amplitude = max(abs(int.from_bytes(audio_chunk[i:i+2], 'little', signed=True))
                        for i in range(0, len(audio_chunk), 2))
        return amplitude < self.silence_threshold
