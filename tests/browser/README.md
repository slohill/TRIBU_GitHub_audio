# Targeted online browser regressions

Run from a development checkout with the server dependencies installed, plus Playwright and socket.io-client available to Node:

```sh
node tests/browser/ogre-cascade-online.cjs
```

The default browser is installed Microsoft Edge. Set `TRIBU_BROWSER_CHANNEL` to another installed Chromium channel if needed. `TRIBU_PLAYWRIGHT_MODULE` and `TRIBU_SOCKET_CLIENT_MODULE` can point to external module installations; server dependencies must also resolve (for example through `NODE_PATH`).

Use free local ports 8791 and 8792 and run tests sequentially. The script creates a temporary server fixture in `server/`, starts a separate local server and two browser views, then removes the fixture. Do not run against a production server. A complete checkout supplies the assets; `TRIBU_TEST_ASSET_ROOT` optionally supplies the historical development workspace fallback assets.

The scenario seeds two nested legacy battles with an Ogre power and pending Gold gain. It destroys both attacking origins through the engine, checks one-time card discards, two owners' loss choices through UI, reload during the second choice, and Gold held until all choices complete then paid once. Browser/socket state is bridged by the harness. This is a targeted engine/synchronization regression, not a full natural UI match or a real-device/audio test.
