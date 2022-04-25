[docker image](https://hub.docker.com/repository/docker/coteeq/soa-pdf)

при сборке контейнера автоматически генерится база из 10 игроков.

1. Получить инфу про игрока:
```
curl localbashhost:5000/player/1
```

2. Получить инфу про игроков:
```bash
curl localhost:5000/players?id=1&id=2
```

3. Поменять имя у игрока:
```bash
curl 'localhost:5000/player' -d '{"id": 4, "name":"new"}' -H 'Content-Type: application/json'
```

4. Поменять картинку у игрока:
```bash
curl https://thiscatdoesnotexist.com > pic.jpg
curl 'localhost:5000/player' -d "{\"id\": 4, \"picture\":\"$(cat pic.jpg | base64)\"}' -H 'Content-Type: application/json'
```

5. Создать игрока:
```bash
curl https://thiscatdoesnotexist.com > pic.jpg
curl 'localhost:5000/player' -d "{\"picture\":\"$(cat pic.jpg | base64)\", \"sex\": \"F\", \"name\": \"johnny\", \"email\": \"johnny@best.com\"}" -H 'Content-Type: application/json'
```

6. Запросить пдфку:
```bash
p=$(curl -X POST localhost:5000/player_pdf/9 | jq -r '.path')
    && sleep 3
    && curl localhost:5000/$p > out.pdf
```
