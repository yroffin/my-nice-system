# Nice GUI System

Based on https://nicegui.io ... a nice python gui framework

A simple project to describe your models

## config

create a venv

```bash
python3 -m venv $PWD/.my-nice-system
source $PWD/.my-nice-system/bin/activate
```

store a .config.yaml on base path

```yaml
gui:
  base_uri: http://localhost:8080
  login_uri: http://localhost:8080/login
  redirect_uri: http://localhost:8080/redirect
  secret: jCT6pBEZAQDSDQSDQQSDQd
  links:
  - name: Home page
    route: /
```

then run

```bash
python3 src/main.py
```

## docker

```
docker build -t <your-registry>/my-nice-system:1.0 .
```

```
docker run --rm --name my-nice-system -p8080:8080 <your-registry>/my-nice-system:1.0
```
