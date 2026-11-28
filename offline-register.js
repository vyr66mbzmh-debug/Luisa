'use strict';
if('serviceWorker' in navigator&&location.protocol!=='file:')navigator.serviceWorker.register(new URL('sw.js',document.currentScript.src)).catch(error=>console.warn('Offline registration failed. Open Offline downloads for recovery instructions.',error));

if (!window.LUISA_NAVIGATION) {const script=document.createElement('script');script.src=new URL('app-navigation.js',document.currentScript.src);document.head.append(script);}
