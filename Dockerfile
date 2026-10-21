FROM python:3.13-alpine

ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV EXPOSED_PORT=${APP_EXPOSED_PORT}
ENV GRPC_SUB_PORT=${GRPC_SUB_PORT}

ARG RELEASE_TYPE=dev

WORKDIR /code

RUN apk add --no-cache gcc musl-dev linux-headers

COPY . .

 RUN python -m venv venv

 RUN source venv/bin/activate

RUN if [ "$RELEASE_TYPE" = "prod" ]; then pip install -r requirements.txt; \
    else pip install -r requirements_dev.txt; fi

EXPOSE $EXPOSED_PORT

CMD ["flask", "run", "--debug"]