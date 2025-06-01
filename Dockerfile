FROM continuumio/miniconda3:latest  as builder

WORKDIR /app

COPY environment.yml .
#COPY environment-minimal.yml .


#RUN conda env create -f environment-minimal.yml  && conda clean -afy
RUN conda env create -f environment.yml  && conda clean -afy

FROM python:slim

WORKDIR /app

COPY --from=builder /opt/conda/envs/agent /opt/conda/envs/agent
COPY . .

RUN echo "conda activate agent" >> ~/.bashrc

ENV PATH /opt/conda/envs/agent/bin:$PATH

CMD ["streamlit", "run", "streamlit_main.py"]

