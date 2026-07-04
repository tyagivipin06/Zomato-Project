# Deployment Guide: Railway (Backend) & Vercel (Frontend)

This guide walks you through decoupling the Zomato AI Recommendation System to run the FastAPI Python backend on **Railway** and the static frontend on **Vercel**.

## 1. Deploy the Backend on Railway

Railway is excellent for running Python/FastAPI services.

1. Go to [Railway.app](https://railway.app/) and click **New Project** → **Deploy from GitHub repo**.
2. Select your `Zomato-Project` repository.
3. Once the project is created, click on the service box, go to the **Variables** tab, and add:
   - `GROQ_API_KEY` = `your_actual_api_key_here`
4. Go to the **Settings** tab of the service, scroll down to **Build & Deploy** and locate **Start Command**. Set it to:
   ```bash
   uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT
   ```
   *(This ensures Railway only starts the API server and exposes it correctly.)*
5. Go to the **Settings** tab, scroll to **Networking**, and click **Generate Domain**.
6. Copy this domain URL (e.g., `https://zomato-backend-production.up.railway.app`). You will need it for Vercel.

---

## 2. Configure Vercel Proxy

Currently, our frontend (`index.html`) makes API calls to relative paths (like `/api/v1/recommend`). To make this work when deployed separately, we will tell Vercel to route any `/api` requests directly to your Railway backend.

Create a file named `vercel.json` in the **root** of your repository and add the following configuration. Replace the destination URL with the domain you generated on Railway:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://<YOUR-RAILWAY-DOMAIN>.up.railway.app/api/$1"
    }
  ]
}
```

Commit and push this file to your GitHub repository:
```bash
git add vercel.json
git commit -m "Add Vercel proxy configuration"
git push
```

---

## 3. Deploy the Frontend on Vercel

Vercel is perfect for serving lightning-fast static assets like our Vanilla JS UI.

1. Go to [Vercel.com](https://vercel.com/) and click **Add New...** → **Project**.
2. Import your `Zomato-Project` repository.
3. Vercel will automatically detect that this is a static project. Leave the Framework Preset as **Other**.
4. Click **Deploy**.

## 4. Verification

Once Vercel finishes deploying, click on your live Vercel URL.
1. The web interface should load instantly.
2. The location and cuisine dropdowns should populate (this means the `GET /api/v1/locations` rewrite proxy to Railway is working).
3. Try running a search. It should return your 5 AI recommendations!
