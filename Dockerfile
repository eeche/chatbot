FROM python:3.11.0-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install --upgrade pip
RUN pip3 --trusted-host pypi.org --trusted-host files.pythonhosted.org install -r requirements.txt

RUN chmod +x /app/start.sh

CMD ["bash", "-c", "/app/start.sh"]