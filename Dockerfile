FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg MPLCONFIGDIR=/tmp/matplotlib
WORKDIR /opt/forgeloop
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir '.[analysis]' && useradd --uid 10001 --create-home forgeloop && mkdir /work && chown forgeloop:forgeloop /work
USER forgeloop
WORKDIR /work
ENTRYPOINT ["forgeloop"]
CMD ["doctor", "--require-analysis"]
