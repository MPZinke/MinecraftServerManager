FROM python:3.13-slim

RUN apt update
RUN apt install -y docker-cli jq
RUN pip3 install toml-cli

COPY ./pyproject.toml ./
RUN pip3 install $(toml get --toml-path pyproject.toml project.dependencies | sed -e "s/[']/\"/g" | jq -r '.[]')

COPY ./src ./src

EXPOSE 443

ENTRYPOINT ["python3", "./src"]
