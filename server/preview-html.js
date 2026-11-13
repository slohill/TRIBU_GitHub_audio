'use strict';
// Enable trials only on a separately configured preview service.
function previewHtml(html, enabled) {
 if (!enabled) return html;
 return html.replace('<head>', '<head><script>window.TRIBU_CORRUPTION_PREVIEW=true;</script>')
  .replaceAll('https://tribu-online.onrender.com/socket.io/socket.io.js', '/socket.io/socket.io.js')
  .replace("const ONLINE_SERVER='https://tribu-online.onrender.com';", 'const ONLINE_SERVER=location.origin;');
}
module.exports={previewHtml};
