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
# Firebase Web configuration (public client identifiers, not secrets). Leave
# empty to keep FCM background handling disabled; VAPID Web Push still works.
ARG VITE_FIREBASE_API_KEY=
ARG VITE_FIREBASE_PROJECT_ID=
ARG VITE_FIREBASE_MESSAGING_SENDER_ID=
ARG VITE_FIREBASE_APP_ID=
ARG VITE_FIREBASE_AUTH_DOMAIN=
ARG VITE_FIREBASE_STORAGE_BUCKET=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_DEMO_MODE=${VITE_DEMO_MODE}
ENV VITE_DEMO_TENANT_SLUG=${VITE_DEMO_TENANT_SLUG}
ENV VITE_DEMO_ACCOUNTS_B64=${VITE_DEMO_ACCOUNTS_B64}
ENV VITE_FIREBASE_API_KEY=${VITE_FIREBASE_API_KEY}
ENV VITE_FIREBASE_PROJECT_ID=${VITE_FIREBASE_PROJECT_ID}
ENV VITE_FIREBASE_MESSAGING_SENDER_ID=${VITE_FIREBASE_MESSAGING_SENDER_ID}
ENV VITE_FIREBASE_APP_ID=${VITE_FIREBASE_APP_ID}
ENV VITE_FIREBASE_AUTH_DOMAIN=${VITE_FIREBASE_AUTH_DOMAIN}
ENV VITE_FIREBASE_STORAGE_BUCKET=${VITE_FIREBASE_STORAGE_BUCKET}
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
