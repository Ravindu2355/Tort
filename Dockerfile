# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make sure the bot script is executable
RUN chmod +x bot.py

# Define the environment variables (you can also set them in the Koyeb dashboard)
ENV PYTHONUNBUFFERED=1

#run
CMD gunicorn --bind 0.0.0.0:8000 app:app & python3 bot.py
#CMD python3 bot.py
