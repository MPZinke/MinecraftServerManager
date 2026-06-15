# FROM: https://hub.docker.com/_/rust/
FROM node:23.5-slim AS builder

RUN apt update
RUN apt install -y git
RUN git clone --depth 1 https://github.com/MPZinke/TypeScript-Jinja.git /Typescript-Jinja
WORKDIR /Typescript-Jinja
RUN npm install
RUN npm run build
# RUN chmod -R 777 /usr/Typescript-Jinja/built
# RUN mkdir /tsc
# COPY ./built /tsc/built

COPY ./source /usr/source
COPY ./tsconfig.json /usr/tsconfig.json
WORKDIR /usr

# RUN node /usr/Typescript-Jinja/built/local/tsc.js --build --verbose
RUN node /Typescript-Jinja/built/local/tsc.js


# ---------------------- #

FROM python:3.13-slim

RUN apt update
# RUN apt install -y docker-cli gcc jq libpq-dev netcat-traditional
RUN apt install -y jq netcat-traditional
RUN pip3 install toml-cli

COPY ./pyproject.toml ./
RUN pip3 install $(toml get --toml-path pyproject.toml project.dependencies | sed -e "s/[']/\"/g" | jq -r '.[]')

COPY --from=builder /usr/source ./source

EXPOSE 443

ENTRYPOINT ["python3", "./source"]
