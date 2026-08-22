# ==============================================================================
# OmniSpec AI — Frontend Production Dockerfile (Node.js / SPA Serve - No Nginx)
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Production Runner Stage (Pure Node.js, zero Nginx)
FROM node:20-alpine AS runner

WORKDIR /app

# Install lightweight static SPA server
RUN npm install -g serve

# Copy built production assets from builder
COPY --from=builder /app/dist ./dist

# Expose frontend port (Render sets $PORT dynamically, default 3000)
ENV PORT=3000
EXPOSE 3000

# Start static file server with Single Page Application (-s) client-side routing
CMD ["sh", "-c", "serve -s dist -l ${PORT:-3000}"]
