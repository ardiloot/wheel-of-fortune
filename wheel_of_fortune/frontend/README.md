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

## Run backend in developer mode

Create `.env.local` file for overriding environment:

```bash
VITE_API_URL=https://wheel.int.example.com/api/v1
VITE_WS_URL=wss://wheel.int.example.com/api/v1/ws
```

Run frontend in `dev` mode:

```bash
nvm use
npm run dev
```

## Prepare release

```bash
nvm use
npm run build
```

## Updating packages

```bash
npm update
npm install
```

or to also update (`package.json`) file

```bash
npm install -g npm-check-updates
ncu -u
npm install
```
