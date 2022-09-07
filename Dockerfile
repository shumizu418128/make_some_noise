FROM python:3.9
USER root

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm
RUN pip install git+https://github.com/Pycord-Development/pycord \
    pip install pynacl
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN  apt-get update \
    && apt-get install -y ffmpeg \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
COPY discordbot.py discordbot.py
COPY battle_start.mp3 battle_start.mp3
COPY bunka.mp3 bunka.mp3
COPY countdown.mp3 countdown.mp3
COPY dismuch.mp3 dismuch.mp3
COPY dismuch_2.mp3 dismuch_2.mp3
COPY dismuch_3.mp3 dismuch_3.mp3
COPY dismuch_4.mp3 dismuch_4.mp3
COPY esh.mp3 esh.mp3
COPY esh_2.mp3 esh_2.mp3
COPY kansei.mp3 kansei.mp3
COPY kansei_2.mp3 kansei_2.mp3
COPY kbbtime.mp3 kbbtime.mp3
COPY msn.mp3 msn.mp3
COPY olala.mp3 olala.mp3
COPY round2switch.mp3 round2switch.mp3
COPY round3switch.mp3 round3switch.mp3
COPY round4switch.mp3 round4switch.mp3
COPY time.mp3 time.mp3
COPY time_2.mp3 time_2.mp3
COPY time_3.mp3 time_3.mp3
CMD ["python", "-u", "discordbot.py"]
ARG EnvironmentVariable
