FROM openjdk:24-slim

# RUN java -jar server.jar nogui

WORKDIR /usr/app
COPY server.jar server.jar
COPY ./* ./
RUN tar -xvf server.tar.gz
RUN rm server.tar.gz Dockerfile

EXPOSE 25565

CMD ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui", "--bonusChest"]
