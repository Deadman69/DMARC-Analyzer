FROM python:3.13.3-slim
RUN useradd -ms /bin/bash appuser
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /home/appuser/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# Utilise l'utilisateur non root (créer des problèmes de permission, donc désactivé pour le moment)
# USER appuser
CMD ["python", "main.py"]
