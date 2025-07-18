FROM python:3.12

# Install OpenGL dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy application files
COPY . /app/

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
