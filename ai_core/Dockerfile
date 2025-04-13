FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
# Path is relative to the build context (project root)
COPY ai_core/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code from the ai_core directory
# into the /app directory in the image
COPY ai_core/ .

# Expose port for the API
EXPOSE 5000

# Run the application (using the app.py inside /app)
# Ensure app.py is runnable, e.g., using 'python -m ai_core.app' might be safer
# if imports rely on the package structure, but 'python app.py' works
# if app.py is directly runnable from /app.
CMD ["python", "app.py"]
