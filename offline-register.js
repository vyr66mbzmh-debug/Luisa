'use strict';
if('serviceWorker' in navigator&&location.protocol!=='file:')navigator.serviceWorker.register(new URL('sw.js',document.currentScript.src)).catch(error=>console.warn('Offline registration failed. Open Offline downloads for recovery instructions.',error));
