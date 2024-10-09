# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app/speech_ai_backend

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application AND remove the .env file
COPY . .
RUN rm -f ./.env


# Expose the port Flask runs on
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
