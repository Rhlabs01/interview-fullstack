FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend/ /app/backend/
COPY --from=frontend /frontend/dist /app/backend/app/static
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
WORKDIR /app/backend
EXPOSE 8000
CMD ["/app/start.sh"]
