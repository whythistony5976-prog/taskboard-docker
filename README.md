# Taskboard (Flask + SQLite + Docker)


    docker build -t taskboard .
    docker run -d -p 5000:5000 -v taskdata:/data taskboard

Tasks are stored in the `taskdata` volume. `docker compose down` keeps them; `docker compose down -v` deletes them.
