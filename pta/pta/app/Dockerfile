FROM python:{{ python_version }}-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* requirements.txt requirements-dev.txt ./

RUN python -m pip install --upgrade pip \
    && if [ -f pyproject.toml ]; then pip install poetry && poetry install --no-interaction --no-root; \
       elif [ -f requirements.txt ]; then pip install -r requirements.txt; \
       fi

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
