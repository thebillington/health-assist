# Screenshots and promotion

All App Store screenshots are 1290 × 2796 (iPhone 6.9", iPhone-only) and are
committed under `docs/images/store/`. They are generated from the technical
mockups in `screenshots/` by the OSG project in `osg/`.

## App Store screenshots

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:28px;margin-top:24px">

<figure>
  <img src="../images/store/01-setup.png" alt="Health Assist setup screen on an iPhone" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Your health, in your home.</strong><br>A free, local-first bridge from Apple Health to your own Home Assistant.</figcaption>
</figure>

<figure>
  <img src="../images/store/02-history.png" alt="Health Assist sync and history screen" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Every record, not just today.</strong><br>Full HealthKit history on the first sync, then background updates.</figcaption>
</figure>

<figure>
  <img src="../images/store/03-sensors.png" alt="Health Assist latest values screen" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Every metric, as a sensor.</strong><br>Native Home Assistant sensors with long-term statistics.</figcaption>
</figure>

<figure>
  <img src="../images/store/04-privacy.png" alt="Health Assist privacy and security screen" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Your data stays yours.</strong><br>No analytics, no telemetry and no vendor cloud.</figcaption>
</figure>

<figure>
  <img src="../images/store/05-sponsor.png" alt="Health Assist support screen with Sponsor My Work" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Free software, funded by you.</strong><br>Sponsor My Work is optional and unlocks nothing.</figcaption>
</figure>

<figure>
  <img src="../images/store/06-qr-setup.png" alt="Health Assist QR scanner" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Scan once. Sync forever.</strong><br>The QR code carries the webhook URL and secret.</figcaption>
</figure>

<figure>
  <img src="../images/store/07-appstore-search.png" alt="App Store search showing Health Assist" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Find it on the App Store.</strong><br>Search “health assist”.</figcaption>
</figure>

<figure>
  <img src="../images/store/08-appstore-product.png" alt="App Store product page for Health Assist" style="width:100%;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.18)">
  <figcaption><strong>Built for your home.</strong><br>Free, with no subscription, account or in-app purchases.</figcaption>
</figure>

</div>

## Social card

![Health Assist social card](images/og.png)

## Rebuild the set

```bash
python3 osg/make_screens.py
python3 osg/build_project.py
osg render --formats ios-6-9
osg verify
```

Copy the rendered boards to `docs/images/store/` with the names above. The
full copy deck, alt text and social posts are in
[`appstore/PROMOTION.md`](https://github.com/thebillington/health-assist/blob/main/appstore/PROMOTION.md).
