FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir uv==0.6.6
COPY pyproject.toml uv.lock  ./
RUN uv sync

COPY alembic.ini ./
COPY .env main.py ./
COPY src ./src 

EXPOSE 80

CMD ["uv", "run", "python", "main.py"]
