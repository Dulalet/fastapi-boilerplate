FROM python:3.10

# create the app user
ARG USERNAME=app
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG HOME=/code/
ARG ENVIRONMENT=development

# RUN groupadd --gid $USER_GID $USERNAME \
#     && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
RUN addgroup --system $USERNAME && adduser --system --group $USERNAME
WORKDIR $HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT ${ENVIRONMENT}

ENV SHELL /bin/bash

RUN apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - --version 1.2.0 --git https://github.com/python-poetry/poetry.git@master && \
    cd /usr/local/bin && \
    ln -s /etc/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* $HOME

# Allow installing dev dependencies to run tests
# ARG INSTALL_DEV=true

RUN bash -c "if [ $ENVIRONMENT == 'development' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

COPY . $HOME
RUN chmod +x prestart.sh

ENV PYTHONPATH=$HOME
# ENV PYTHONPATH "${PYTHONPATH}:/code"

# chown all the files to the app user
RUN chown -R $USERNAME:$USERNAME $HOME

# change to the app user
# Switch to a non-root user, which is recommended by Heroku.
USER $USERNAME

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Uvicorn
CMD ["./prestart.sh"]
