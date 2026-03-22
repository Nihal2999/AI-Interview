self.addEventListener('install', e => e.waitUntil(
  caches.open('interview-ai-v1').then(cache =>
    cache.addAll(['/', '/index.html', '/interview.html', '/report.html'])
  )
));

self.addEventListener('fetch', e => e.respondWith(
  caches.match(e.request).then(r => r || fetch(e.request))
));