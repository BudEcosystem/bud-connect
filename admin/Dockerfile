# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application with base path
ENV VITE_BASE_PATH=/admin
# Use /admin/api for production API calls (will be proxied by nginx)
ENV VITE_API_BASE_URL=/admin/api
# Enable debug mode to see what's happening
ENV VITE_DEBUG_MODE=true
RUN npm run build

# Runtime stage
FROM nginx:alpine

# Remove default nginx config
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create a health check endpoint
RUN echo "OK" > /usr/share/nginx/html/health

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]