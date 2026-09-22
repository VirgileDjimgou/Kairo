# ── Stage 1: development ──────────────────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# --host 0.0.0.0 makes the dev server reachable from outside the container
CMD ["npm", "run", "dev"]

# ── Stage 2: production build ──────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_DEMO_MODE=true
ARG VITE_DEMO_TENANT_SLUG=demo
ARG VITE_DEMO_ACCOUNTS_B64=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_DEMO_MODE=${VITE_DEMO_MODE}
ENV VITE_DEMO_TENANT_SLUG=${VITE_DEMO_TENANT_SLUG}
ENV VITE_DEMO_ACCOUNTS_B64=${VITE_DEMO_ACCOUNTS_B64}
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ── Stage 3: production serve (nginx) ─────────────────────────────────────────
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
