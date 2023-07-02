FROM python:3.9

WORKDIR /jupyter

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y postgresql-15 postgresql-client-15
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /jupyter

EXPOSE 8888

CMD ["jupyter-lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
