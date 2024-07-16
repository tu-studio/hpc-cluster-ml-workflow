# Use an official Debian runtime as a parent image
FROM debian:11-slim

# Install dependencies
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
    && rm -rf /var/lib/apt/lists/*

# Install Python Version
RUN wget --no-check-certificate https://www.python.org/ftp/python/${{ env.TUSTU_PYTHON_VERSION }}/Python-${{ env.TUSTU_PYTHON_VERSION }}.tgz \
    && tar -xf Python-{{ env.TUSTU_PYTHON_VERSION }}.tgz \
    && cd Python-{{ env.TUSTU_PYTHON_VERSION }}\
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && ln -s /usr/local/bin/python3.12 /usr/local/bin/python3

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends git

# Install python3-pip
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip

# Install OpenSSH-Client 
RUN apt-get update && apt-get install -y openssh-client

# Set the working directory
WORKDIR /usr/src

# Create a virtual environment and install dependencies
RUN python3 -m venv cntnrvenv
COPY requirements.txt .
RUN . cntnrvenv/bin/activate && pip3 install -r requirements.txt

# Set the working directory
WORKDIR /usr/src/app

CMD ["sh", "-c", ". /usr/src/cntnrvenv/bin/activate"]
