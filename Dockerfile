FROM ollama/ollama

COPY ./scripts/run-ollama.sh /tmp/scripts/run-ollama.sh

WORKDIR /tmp

RUN chmod +x /scripts/run-ollama.sh \
    && ./scripts/run-ollama.sh

EXPOSE 11434