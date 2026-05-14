# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend
WORKDIR /frontend

# Firebase config passed as build-time args (set as HF Space secrets)
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID

COPY mantarang-ui/package*.json ./
RUN npm ci --silent
COPY mantarang-ui/ ./
RUN npm run build

# ── Stage 2: Python backend ────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies (slim set — no ML libs needed)
COPY requirements-hf.txt ./
RUN pip install --no-cache-dir -r requirements-hf.txt

# Copy backend source
COPY mantarang/ ./mantarang/

# Copy data files
COPY track_data_final.csv ./
COPY ["spotify_data clean.csv", "./"]
COPY MD-1M.csv ./

# Copy React build output
COPY --from=frontend /frontend/dist ./dist

# HuggingFace Spaces requires port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "mantarang.src.api.backend:app", "--host", "0.0.0.0", "--port", "7860"]
