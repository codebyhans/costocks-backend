# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

# Expose port
EXPOSE 80

# Create a non-root user
RUN useradd -u 5678 --no-log-init -r -g 0 appuser

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=3

WORKDIR /app
COPY . /app

# Install dependencies 
RUN python -m pip install --no-cache-dir pdm && \
    pdm install --prod

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["pdm", "run", "src/app.py"]
