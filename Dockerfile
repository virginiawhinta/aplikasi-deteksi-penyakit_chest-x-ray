# Install OpenGL dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install -r requirements.txt
# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
