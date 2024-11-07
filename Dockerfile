# Use the official Python image as the base
FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code to the container
COPY . /app

# Expose any necessary port (if your bot listens to a webhook, for example)
# EXPOSE 8443  # Uncomment if you're using webhooks

# Start the bot
CMD ["python", "main.py"]
