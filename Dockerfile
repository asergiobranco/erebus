FROM python:slim 

RUN python3 -m pip install msgpack

COPY erebus erebus 

WORKDIR erebus

RUN python3 setup.py install

CMD python3 -m erebus
