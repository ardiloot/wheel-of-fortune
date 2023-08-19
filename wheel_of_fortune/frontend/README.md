# Frontend

## Setup development environment

Install `nvm` and `node` and install dependencies:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash
source ~/.bashrc
nvm install
nvm use
npm ci
```

## Updating requirements

```bash
nvm use
npm update
```

## Run backend

```bash
nvm use
npm run dev
```

## Prepare release

```bash
nvm use
npm run build
```