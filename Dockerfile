FROM python:3.13-slim

RUN apt update
RUN apt install -y docker-cli gcc jq libpq-dev netcat-traditional
RUN pip3 install toml-cli

COPY ./pyproject.toml ./
RUN pip3 install $(toml get --toml-path pyproject.toml project.dependencies | sed -e "s/[']/\"/g" | jq -r '.[]')

COPY ./source ./source

EXPOSE 443

ENTRYPOINT ["python3", "./source"]
