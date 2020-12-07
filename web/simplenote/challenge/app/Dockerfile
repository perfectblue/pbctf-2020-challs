FROM python:3.8.5-buster

ARG FLAG

RUN mkdir -p /app /tmp/notes
COPY app.py /app/
COPY requirements.txt /app/
RUN echo $FLAG > /flag.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN groupadd -r app && useradd --no-log-init -r -g app app
RUN chown app:app /tmp/notes
USER app

EXPOSE 4444

CMD [   \
        "uwsgi", "--puwsgi-socket", "0.0.0.0:4444", "--manage-script-name", "--mount", "/=app:app", "--mount", "=app:app", \
        "--max-requests=50", "--min-worker-lifetime=15", "--max-worker-lifetime=30", "--reload-on-rss=512", "--worker-reload-mercy=10", \
        "--master", "--enable-threads", "--vacuum", "--single-interpreter", "--die-on-term" \
]