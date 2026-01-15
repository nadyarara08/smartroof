// ============================================
// SMART ROOF - SERVICE WORKER
// ============================================
// Purpose: Enable PWA offline capabilities
// ============================================

const CACHE_NAME = "smartroof-v1.0.0";
const RUNTIME_CACHE = "smartroof-runtime";

// Assets to cache on install
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/static/css/style.css",
  "/static/js/app.js",
  "/manifest.json"
];

// ============================================
// INSTALL: Cache static assets
// ============================================
self.addEventListener("install", event => {
  console.log("[SW] Installing...");
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log("[SW] Caching static assets");
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log("[SW] Install complete");
        return self.skipWaiting();
      })
      .catch(err => {
        console.error("[SW] Install failed:", err);
      })
  );
});

// ============================================
// ACTIVATE: Clean up old caches
// ============================================
self.addEventListener("activate", event => {
  console.log("[SW] Activating...");
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(name => name !== CACHE_NAME && name !== RUNTIME_CACHE)
            .map(name => {
              console.log("[SW] Deleting old cache:", name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log("[SW] Activation complete");
        return self.clients.claim();
      })
  );
});

// ============================================
// FETCH: Network-first for API, Cache-first for static
// ============================================
self.addEventListener("fetch", event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }
  
  // Strategy: Network-first for API calls
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Clone response to cache
          const responseClone = response.clone();
          caches.open(RUNTIME_CACHE)
            .then(cache => cache.put(request, responseClone));
          return response;
        })
        .catch(() => {
          // Fallback to cache if offline
          return caches.match(request);
        })
    );
    return;
  }
  
  // Strategy: Cache-first for static assets
  event.respondWith(
    caches.match(request)
      .then(cached => {
        if (cached) {
          return cached;
        }
        
        return fetch(request)
          .then(response => {
            // Cache successful responses
            if (response.status === 200) {
              const responseClone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(request, responseClone));
            }
            return response;
          });
      })
  );
});

// ============================================
// MESSAGE: Handle messages from clients
// ============================================
self.addEventListener("message", event => {
  if (event.data.action === "skipWaiting") {
    self.skipWaiting();
  }
});