# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# 1. Copy ONLY the requirements first
COPY requirements.txt .

# 2. Install dependencies (This layer will be cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of the application code (This happens AFTER the install)
COPY . .

# Keep the container running
CMD ["bash"]
