FROM python:2.7-slim
MAINTAINER Nicolas Dumoulin "nicolas.dumoulin@irstea.fr"

RUN apt-get update && apt-get install -y libhdf5-dev python-numpy python-pip ipython

ENV VINOPATH /vino
ENV DJANGO_VERSION 1.9.7
RUN pip install django=="$DJANGO_VERSION"

ADD vino-py/pip-requires.txt ${VINOPATH}/vino-py/pip-requires.txt
WORKDIR ${VINOPATH}/vino-py
RUN HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ pip install -r pip-requires.txt

WORKDIR ${VINOPATH}/vinosite
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]