# Use an official Python runtime as a parent image
FROM python:3.12-slim

ARG DEBIAN_MIRROR=https://mirrors.aliyun.com/debian
ARG DEBIAN_SECURITY_MIRROR=https://mirrors.aliyun.com/debian-security
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
ARG PIP_TRUSTED_HOST=mirrors.aliyun.com

# Set the working directory in the container
WORKDIR /app

# Use Alibaba Cloud mirrors for faster builds on servers in mainland China.
# On Alibaba Cloud ECS VPC, these build args can be pointed at the internal mirror:
#   --build-arg DEBIAN_MIRROR=http://mirrors.cloud.aliyuncs.com/debian
#   --build-arg DEBIAN_SECURITY_MIRROR=http://mirrors.cloud.aliyuncs.com/debian-security
#   --build-arg PIP_INDEX_URL=http://mirrors.cloud.aliyuncs.com/pypi/simple
#   --build-arg PIP_TRUSTED_HOST=mirrors.cloud.aliyuncs.com
# Docker registry mirrors for pulling the base image must be configured on the host Docker daemon.
RUN set -eux; \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i \
            -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
            -e "s|https://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
            -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            -e "s|https://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            -e "s|http://security.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            -e "s|https://security.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            /etc/apt/sources.list.d/debian.sources; \
    fi; \
    if [ -f /etc/apt/sources.list ]; then \
        sed -i \
            -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
            -e "s|https://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
            -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            -e "s|https://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            -e "s|http://security.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            -e "s|https://security.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
            /etc/apt/sources.list; \
    fi

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
RUN pip install --no-cache-dir --index-url "${PIP_INDEX_URL}" --trusted-host "${PIP_TRUSTED_HOST}" -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the necessary output directories (if they don't exist in the context)
RUN mkdir -p uploads outputs

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
