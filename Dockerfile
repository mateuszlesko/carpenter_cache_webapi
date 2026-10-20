FROM python:3.13-alpine

ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV EXPOSED_PORT=${APP_EXPOSED_PORT}

ARG RELEASE_TYPE=dev

WORKDIR /code

#RUN apk add --no-cache gcc musl-dev linux-headers

COPY . .

# RUN python -m venv venv

# RUN source venv/bin/activate

RUN if [ "$RELEASE_TYPE" = "dev" ]; then \
        pip install -r requirements.txt;
    elsif [ "$RELEASE_TYPE" = "prod" ]; then \
        pip install -r requirements.txt --no-dev;
    else \
        echo "Invalid RELEASE_TYPE specified. Use 'dev' or 'prod'."; \
        exit 1; \
    fi

EXPOSE $EXPOSED_PORT

#RUN flask run --debug
CMD ["flask", "run", "--debug"]