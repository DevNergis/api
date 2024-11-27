FROM python

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD fastapi run
