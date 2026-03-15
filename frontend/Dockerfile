# ── Frontend Dockerfile ───────────────────────────────────────────────────────
# Stage 1: Build the React/Vite app
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .
# Inject the backend URL at build time (override via docker-compose or build-arg)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config for SPA routing
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
    location /api/ { proxy_pass http://backend:8000; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
