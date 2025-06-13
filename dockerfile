
FROM python:3.12

WORKDIR /app

RUN pip install uv
COPY pyproject.toml uv.lock  ./
RUN uv sync

COPY .env main.py ./
COPY src ./src
COPY static ./static

CMD ["uv", "run", "python", "main.py"]
