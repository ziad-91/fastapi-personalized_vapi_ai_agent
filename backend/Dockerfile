# Use the official lightweight Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing pyc files to disc (equivalent to python -B)
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout and stderr (equivalent to python -u)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local directory to the working directory
COPY . .

# Cloud Run defaults to port 8080
EXPOSE 8080

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
