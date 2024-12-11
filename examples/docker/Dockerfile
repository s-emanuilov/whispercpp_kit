FROM python:3.12-slim

# Install only the required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    make \
    g++ \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install the package
RUN pip install whispercpp_kit

# Set working directory
WORKDIR /app

# Copy the transcription script
COPY transcribe.py .

# Make the script the entrypoint
ENTRYPOINT ["python", "transcribe.py"]