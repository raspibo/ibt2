# Docker Compose

ibt2 requires MongoDB. The repository's `docker-compose.yml` defines both services and a persistent MongoDB volume.

The Dockerfile builds the frontend in a Node.js stage and copies its production
assets into a Python 3.11 runtime image. The final image contains the backend,
locked Python dependencies, and built frontend; Node.js, npm, and frontend source
remain in the build stage. Rebuild the image after changing application code or
dependency locks.

`.dockerignore` allows only the inputs used by the application Dockerfile into
the build context. Repository metadata, virtual environments, existing `dist/`
output, tests, documentation, and the `ssl/` directory are excluded. Local
environment files, keys, and certificates are also excluded from the allowed
source directories. When adding a new Dockerfile build input, update the
allowlist as well.

For HTTPS, mount your certificate and key into `/ibt2/ssl/ibt2_cert.pem` and
`/ibt2/ssl/ibt2_key.pem`, respectively, using read-only bind mounts. Certificates
and keys are not copied into the image. The `--ssl_cert` and `--ssl_key` arguments
can select other mounted paths.

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

## Versioned container releases

The GitHub Actions workflow includes publication to `ghcr.io/<owner>/<repository>`
on pushes of stable `vX.Y.Z` tags, after browser, backend, and Docker checks pass.
The tag must match the version in `package.json` and both package-lock version
fields. The image receives the `X.Y.Z` tag and source, revision, and version labels;
there is no moving `latest` tag. Published images currently target Linux amd64.

Publication uses the repository's `GITHUB_TOKEN` with package write permission,
so no Docker Hub credentials are required. This is configured automation; an
image is available only after the workflow runs successfully on GitHub. Package
visibility and organization policies may require configuration on GitHub before
other users can pull it.

To use a published image in Compose, replace `build: .` in the `ibt2` service with
`image: ghcr.io/<owner>/<repository>:X.Y.Z`, using your repository name and released
version. MongoDB and its persistent volume remain defined by Compose.

## Initial administrator password

On first start, ibt2 creates the `admin` user with the password `admin`. Change it from the personal page after signing in.

To use a different password from the beginning, set the `--admin_password` argument in the `ibt2` service's `command` in `docker-compose.yml` before the first start. For example:

```yaml
services:
  ibt2:
    command: ["--admin_password=choose-a-strong-password"]
```

The image already supplies the server command, so Compose passes this value as an argument to ibt2. Remove the command after the administrator account has been created; changing it later does not change an existing password.

If no password is supplied, the initial password is `admin`.

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
