# ShopSense frontend

React + TypeScript retail analytics interface. See the project README for verified results and complete setup.

```powershell
npm ci
npm run dev -- --host 127.0.0.1
npm run build
npm run lint
```

The FastAPI server must run on port 8000. Vite proxies `/api` to `127.0.0.1:8000` in development and preview. An explicit deployment can set `VITE_API_BASE` in `.env.local`. Charts are loaded in separate bundles and use actual computed customer data. There is no mock-data fallback.
