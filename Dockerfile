# Runtime image for the Visualizador Web de Estructuras de Datos.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SESSION_CACHE_DIR=/var/lib/visualstruct/sessions

WORKDIR /app

# A non-root process prevents the application and its session files from
# gaining unnecessary privileges in the container.
RUN addgroup --system visualstruct \
    && adduser --system --ingroup visualstruct --home /app visualstruct \
    && mkdir -p /var/lib/visualstruct/sessions \
    && chown -R visualstruct:visualstruct /app /var/lib/visualstruct

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# The C sources are intentionally included: the didactic interpreter loads
# them at runtime from docs/tads_C.
COPY --chown=visualstruct:visualstruct app ./app
COPY --chown=visualstruct:visualstruct assets ./assets
COPY --chown=visualstruct:visualstruct static ./static
COPY --chown=visualstruct:visualstruct templates ./templates
COPY --chown=visualstruct:visualstruct docs/tads_C ./docs/tads_C
COPY --chown=visualstruct:visualstruct wsgi.py ./

USER visualstruct

EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5050/healthz', timeout=3)" || exit 1

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5050", "wsgi:app"]
