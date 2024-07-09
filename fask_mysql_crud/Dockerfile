FROM python:3.9-slim

WORKDIR /app

# Installer netcat-openbsd pour attendre la disponibilité de la base de données
RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]
