FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./smart_city.db
ENV MAX_MODE=mock
ENV JWT_SECRET=change-me-in-production

EXPOSE 8000

CMD ["uvicorn", "interfaces.main:app", "--host", "0.0.0.0", "--port", "8000"]
