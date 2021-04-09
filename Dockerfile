FROM python:3.7

COPY . /mara_nlp_suite_private/mara_nlp_suite_public

WORKDIR /mara_nlp_suite_private/mara_nlp_suite_public

RUN apt update
RUN pip install -r requirements.txt
