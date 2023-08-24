

# Local development

## Setup development environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r dev-requirements.txt
```

## Updating requirements

After adding dependency update requirement files by running:

```bash
pip-compile --upgrade -o requirements.txt pyproject.toml
pip-compile --extra dev --upgrade -o dev-requirements.txt pyproject.toml
pip-sync dev-requirements.txt
```

## Run backend

```bash
source venv/bin/activate
python -m wheel_of_fortune
```
 
## Build

Build frontend:

```bash
cd wheel_of_fortune/frontend/
nvm use
npm ci
npm run build
```

Build python package:

```bash
python -m build
```

Build docker image:

```bash
docker build -t wheel_of_fortune .
```
