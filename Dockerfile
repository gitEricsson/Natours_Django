FROM python:3.11.4-slim-buster

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies and GDAL
RUN apt-get update && apt-get install -y netcat \
    gcc \
    python3-dev \
    postgresql-client \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Ensure the dev-data directory has correct permissions
COPY ./dev-data .
RUN chmod +x ./dev-data

# Copy and set entrypoint
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh


# Run entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
