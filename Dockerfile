FROM continuumio/miniconda:latest
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

# Install app dependencies
COPY environment.yml /usr/src/app/

RUN conda install psutil
RUN conda env create -f environment.yml
RUN source activate KhuromApp

COPY . /usr/src/app

ENV PATH /opt/conda/envs/KhuromApp/bin:$PATH

ENTRYPOINT ["python"]
CMD ["app.py"]
EXPOSE 5000