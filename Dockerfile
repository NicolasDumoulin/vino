FROM python:2.7-slim
MAINTAINER Nicolas Dumoulin "nicolas.dumoulin@irstea.fr"

RUN apt-get update && apt-get install -y libhdf5-dev python-numpy python-pip ipython

ENV VINOPATH /vino

ADD vino-py/pip-requires.txt ${VINOPATH}/vino-py/pip-requires.txt
WORKDIR ${VINOPATH}/vino-py
RUN HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ pip install -r pip-requires.txt

ADD vinosite/pip-requires.txt ${VINOPATH}/vinosite/pip-requires.txt
WORKDIR ${VINOPATH}/vinosite
RUN pip install -r pip-requires.txt

WORKDIR ${VINOPATH}/vinosite
EXPOSE 8000
CMD ["sh","start.sh"]