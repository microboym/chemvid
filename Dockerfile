# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - ImageMagick is required by MoviePy for rendering text (Chinese subtitles)
# - ffmpeg is required by MoviePy for audio/video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow rendering text with MoviePy
# By default, some ImageMagick installations restrict certain operations for security.
# This removes the restrictions so MoviePy can generate TextClips.
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"\/>/<!-- <policy domain="path" rights="none" pattern="@\*"\/> -->/g' /etc/ImageMagick-6/policy.xml || true

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the necessary output directories (if they don't exist in the context)
RUN mkdir -p uploads outputs

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]