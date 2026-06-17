FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY download_data.py .
RUN python download_data.py
COPY main.py .
COPY formatter.py .
COPY propagator.py .
COPY celestrak_client.py .
RUN useradd -m appuser
USER appuser
CMD ["python", "main.py"]