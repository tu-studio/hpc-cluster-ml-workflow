# Use an official Debian runtime as a parent image
FROM debian:11-slim

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    curl \
    libbz2-dev \
    git \
    python3-pip \
    openssh-client \
    # Remove apt cache
    && rm -rf /var/lib/apt/lists/*

# Install Python Version 3.12.4 
RUN wget --no-check-certificate https://www.python.org/ftp/python/3.12.4/Python-3.12.4.tgz \
    && tar -xf Python-3.12.4.tgz \
    && cd Python-3.12.4 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    # Delete the unzipped directory and downloaded archive to save space
    && rm -rf Python-3.12.4 Python-3.12.4.tgz \
    # Create symlink for python3
    && ln -s /usr/local/bin/python3.12 /usr/local/bin/python3

# Set the working directory
WORKDIR /home/app

# Copy the python requirements list to /home/app and install them
COPY requirements.txt .
RUN pip3 install -r requirements.txt \
    && rm requirements.txt




