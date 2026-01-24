# 🚀 Deployment Guide

## Backend Deployment (Render.com)

The backend is configured for deployment on [Render](https://render.com) using the `render.yaml` specification.

### Steps
1.  Connect your GitHub repository to Render.
2.  Select "Blueprints" and point it to `render.yaml`.
3.  Render will automatically detect the service `debatebot-backend`.
4.  **Environment Variables**:
    - You must add `GROQ_API_KEY` in the Render dashboard (it is marked as `sync: false` in yaml, meaning it's a secret).
    - `PYTHON_VERSION` is set to `3.12.1`.

### Manual Build Command
If deploying elsewhere:
```bash
pip install -r backend/requirements.txt
```

### Start Command
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Frontend Deployment (Vercel/Netlify)

The frontend is a static React application built with Vite.

### Steps
1.  Connect your repository to Vercel or Netlify.
2.  **Build Settings**:
    - **Root Directory**: `frontend`
    - **Build Command**: `npm run build`
    - **Output Directory**: `dist`
3.  **Environment Variables**:
    - If your backend is deployed, you may need to update the API proxy or set a `VITE_API_URL` if you refactor to use absolute URLs (currently uses relative `/api` proxy). *Production tip: Ensure your frontend knows where the backend is hosted.*

### Local Production Build
To test the production build locally:

```bash
cd frontend
npm run build
npm run preview
```
