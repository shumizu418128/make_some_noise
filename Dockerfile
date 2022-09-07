FROM python:3.9
USER root

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm
RUN pip install git+https://github.com/Pycord-Development/pycord \
    pip install pynacl \
    pip install asyncio \
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY discordbot.py discordbot.py
CMD ["python", "-u", "discordbot.py"]
ARG EnvironmentVariable
