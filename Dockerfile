FROM python:alpine3.19

RUN pip install -r requirements.txt

CMD ./start.sh

EXPOSE 2002
