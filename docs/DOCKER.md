# Docker Compose

ibt2 requires MongoDB. The repository's `docker-compose.yml` defines both services and a persistent MongoDB volume.

## Start and stop

From the repository root, build and start the stack:

```sh
docker compose up --build
```

Open [http://localhost:3000/](http://localhost:3000/). Add `-d` to run the services in the background, view logs with `docker compose logs -f`, and stop the services with:

```sh
docker compose down
```

The MongoDB data is stored in the Compose `data` volume (named `ibt2_data` by default). Do not run `docker compose down --volumes` unless you intentionally want to delete all stored attendance data.

## Initial administrator password

Before the first start, set the `--admin_password` argument in the `ibt2` service's `command` in `docker-compose.yml`. For example:

```yaml
services:
  ibt2:
    command: ["--admin_password=choose-a-strong-password"]
```

The image already supplies the server command, so Compose passes this value as an argument to ibt2. Remove the command after the administrator account has been created; changing it later does not change an existing password.

If no password is supplied, ibt2 generates one and writes it to the server logs on first start. Retrieve it with `docker compose logs ibt2`.

## Database maintenance

The scripts in `docker-tools/` are legacy helpers that assume old Compose-generated network and container names. Use the running `mongo` service instead.

Create an archive backup from the repository root:

```sh
docker compose exec -T mongo mongodump --archive --db=ibt2 > ibt2-backup.archive
```

Restore that archive with:

```sh
docker compose exec -T mongo mongorestore --archive --drop --db=ibt2 < ibt2-backup.archive
```

Restoring replaces the current `ibt2` database. Always create and verify a backup before restoring it.
