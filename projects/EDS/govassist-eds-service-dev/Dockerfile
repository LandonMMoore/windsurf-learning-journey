FROM python:3.13-slim

# Set environment variables
ENV ACCEPT_EULA=Y \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libgnutls30 gnutls-bin && \
    apt-get upgrade -y && \
    apt-get install -y \
    libc6 \
    libasound2 \
    libasound2-dev \
    libffi-dev \
    unixodbc-dev \
    alsa-utils \
    curl \
    gnupg \
    build-essential \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install poetry

# Copy project files
COPY pyproject.toml /code/
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install
RUN poetry update

COPY . /code/

# Expose port and run app
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]