FROM python:3.10

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y wkhtmltopdf

COPY app app
COPY main.py .
COPY fill_db.py .

RUN mkdir -p pictures
RUN mkdir -p pdfs
RUN [ "python3", "fill_db.py" ]

ENV FLASK_APP=main.py
ENV FLASK_ENV=development

CMD [ "flask", "run", "--host=0.0.0.0" ]
