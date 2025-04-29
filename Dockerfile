FROM python:3.11-slim
WORKDIR /code

# system deps for Chrome / Playwright
RUN apt-get update && apt-get install -y curl gnupg unzip && \
    curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb && \
    apt-get install -y ./chrome.deb && rm chrome.deb && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt && playwright install --with-deps

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 