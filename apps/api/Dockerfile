FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./

RUN python3 -c "import tomllib,subprocess; f=open('pyproject.toml','rb'); d=tomllib.load(f); f.close(); subprocess.run(['uv','pip','install','--system']+d['project']['dependencies'],check=True)"

COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]
