# ==============================================================================
# OmniSpec AI — Frontend Production Dockerfile (Vite Native Preview - Zero Nginx)
# ==============================================================================
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build production bundle
COPY . .
RUN npm run build

# Expose frontend port (Render sets $PORT dynamically, default 3000)
ENV PORT=3000
EXPOSE 3000

# Native Vite production server binding to 0.0.0.0
CMD ["sh", "-c", "npx vite preview --host 0.0.0.0 --port ${PORT:-3000}"]
