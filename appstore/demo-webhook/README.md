# Demo webhook for App Review

A throwaway endpoint that accepts the app's POST and returns the JSON the app
expects. It stores and logs nothing.

```bash
cd appstore/demo-webhook
npx wrangler deploy
```

Then put the deployed `https://…workers.dev/…` URL (and an optional secret) into
`appstore/review-notes.txt`, replacing the placeholders.

Do not point this at real health data. It exists only so App Review can exercise
"Send a Test Payload" and "Sync Now" without a Home Assistant installation.
