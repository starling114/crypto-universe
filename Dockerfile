# -------------------
# Stage 1: Builder
# -------------------
FROM node:24-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-venv \
  python3-pip \
  build-essential \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY package*.json ./

RUN npm ci --only=production || npm install --only=production

COPY scripts/requirements.txt ./scripts/requirements.txt
RUN python3 -m venv scripts/myenv \
  && scripts/myenv/bin/pip install --no-cache-dir --upgrade pip \
  && scripts/myenv/bin/pip install --no-cache-dir -r scripts/requirements.txt

# -------------------
# Stage 2: Final image
# -------------------
FROM node:24-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/scripts/myenv ./scripts/myenv

COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/
COPY scripts/ ./scripts/
COPY erc20abi.json ./erc20abi.json

COPY bin/docker_entrypoint.sh /app/docker_entrypoint.sh
RUN chmod +x /app/docker_entrypoint.sh

ENV ADSPOWER_PORT=50325
ENV HOST_URL=host.docker.internal
ENV NODE_ENV=production

EXPOSE 3000

ENTRYPOINT ["/app/docker_entrypoint.sh"]
