# Use an official Python image as the base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .


# Specify the default command to run the app (update as needed)
CMD ["python", "main2.py"]
