FROM python:3.9

# Install OS dependencies for ALSA, PortAudio, etc.
RUN apt-get update && \
    apt-get install -y \
      portaudio19-dev \
      alsa-utils \
      && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]