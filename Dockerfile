# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install ffmpeg
#RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port the app runs on (not strictly necessary for a Telegram bot)
#EXPOSE 8000

# Run the bot when the container launches
CMD gunicorn --bind 0.0.0.0:8000 app:app & python3 bot.py
#CMD python3 bot.py
