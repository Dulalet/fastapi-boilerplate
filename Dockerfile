FROM python:3.10

# create the app user
RUN addgroup --system app && adduser --system --group app

WORKDIR /code/

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - --version 1.2.0 --git https://github.com/python-poetry/poetry.git@master && \
    cd /usr/local/bin && \
    ln -s /etc/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* /code/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=true

RUN sh -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY . /code
RUN chmod +x prestart.sh

ENV PYTHONPATH=/code
# ENV PYTHONPATH "${PYTHONPATH}:/code"

# chown all the files to the app user
RUN chown -R app:app $HOME

# change to the app user
# Switch to a non-root user, which is recommended by Heroku.
USER app

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Uvicorn
CMD ["./prestart.sh"]
