FROM python:3.10-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY .src /app/src
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN sudo apt update && sudo apt upgrade -y
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]




