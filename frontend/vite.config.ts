import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Dev server on :5173. The API stays on :8000 and allows
// this origin via CORS (see backend/app/main.py). No proxy, no magic:
// pages fetch http://localhost:8000/api/v1/* directly.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
  },
});
