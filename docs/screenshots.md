# Health Assist — one-pager

<style>
.ha-hero {
  display: flex;
  align-items: center;
  gap: 28px;
  flex-wrap: wrap;
  padding: 26px 28px;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 18px;
  background: var(--md-code-bg-color);
  margin: 18px 0 28px;
}
.ha-hero img { width: 260px; height: auto; }
.ha-hero p { margin: 0 0 6px; }
.ha-hero .tagline { font-weight: 700; font-size: 1.15rem; }
.ha-links { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 10px; font-size: .9rem; }
.ha-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 26px;
  margin: 22px 0 8px;
}
.ha-shot { margin: 0; }
.ha-shot img {
  width: 100%;
  height: auto;
  border-radius: 14px;
  border: 1px solid var(--md-default-fg-color--lightest);
  box-shadow: 0 12px 28px rgba(15, 23, 42, .16);
}
.ha-shot figcaption {
  margin-top: 9px;
  color: var(--md-default-fg-color--light);
  font-size: .8rem;
  line-height: 1.45;
}
.ha-shot strong { display: block; color: var(--md-default-fg-color); }
.ha-copy {
  margin: 16px 0;
  padding: 14px 20px;
  border-left: 4px solid #0f766e;
  border-radius: 0 12px 12px 0;
  background: var(--md-code-bg-color);
}
.ha-copy p { margin: 8px 0; }
.ha-copy ul { margin: 8px 0; padding-left: 22px; }
.ha-sub { color: var(--md-default-fg-color--light); font-size: .88rem; }
.ha-table td:first-child { white-space: nowrap; }
@media print {
  .ha-shot img { box-shadow: none; }
}
</style>

<div class="ha-hero">
  <img src="../images/logo.svg" alt="Health Assist — Apple Health to Home Assistant">
  <div>
    <p class="tagline">Apple Health → Home Assistant.<br>Free, local-first, no vendor cloud.</p>
    <p class="ha-sub">The app, the integration and every promotion asset in one place.</p>
    <div class="ha-links">
      <a href="https://github.com/thebillington/health-assist">GitHub</a>
      <a href="https://healthassist.thebillington.co.uk/">Docs</a>
      <a href="https://healthassist.thebillington.co.uk/privacy/">Privacy</a>
      <a href="https://healthassist.thebillington.co.uk/support/">Support</a>
      <a href="https://github.com/sponsors/thebillington">Sponsor My Work</a>
    </div>
  </div>
</div>

## At a glance

| | |
| --- | --- |
| **Name** | Health Assist |
| **Tagline** | Apple Health to Home Assistant |
| **Price** | Free — no subscription, no in-app purchases, no paid tier |
| **Platforms** | iOS 18+; Home Assistant 2024.1+ |
| **Integration** | `apple_health_sync` (HACS custom repository or manual copy) |
| **License** | MIT, both the app and the integration |
| **Privacy** | No account, no analytics, no telemetry, no vendor cloud |
| **App Store** | Coming soon |
| **Links** | [GitHub](https://github.com/thebillington/health-assist) · [Docs](https://healthassist.thebillington.co.uk/) · [Support](https://healthassist.thebillington.co.uk/support/) · [Sponsor](https://github.com/sponsors/thebillington) |

## The pitch

**Health Assist connects Apple Health to your own Home Assistant.** The app reads
HealthKit read-only and sends the readings to a webhook on the user's Home
Assistant instance. Home Assistant turns them into native sensors and long-term
statistics, so health data can sit alongside the rest of the home.

- **Local-first** — data goes from the iPhone to the user's Home Assistant, not
  to a vendor cloud.
- **Full history** — the first sync exports all available HealthKit history in
  resumable chunks, then keeps it current.
- **Native sensors** — stable unique IDs, correct units and long-term
  statistics.
- **Free and open source** — MIT on both sides. Sponsor My Work is optional and
  unlocks nothing.

## Screenshots

All eight boards are 1290 × 2796 (iPhone 6.9"). Files live in
`docs/images/store/` and pass `osg verify`.

<div class="ha-grid">

<figure class="ha-shot">
  <img src="../images/store/01-setup.png" alt="Health Assist setup screen on an iPhone" loading="lazy">
  <figcaption><strong>Your health, in your home.</strong>A free, local-first bridge from Apple Health to Home Assistant.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/02-history.png" alt="Health Assist sync and history screen" loading="lazy">
  <figcaption><strong>Every record, not just today.</strong>Full HealthKit history on the first sync, then background updates.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/03-sensors.png" alt="Health Assist latest values screen" loading="lazy">
  <figcaption><strong>Every metric, as a sensor.</strong>Native Home Assistant sensors with long-term statistics.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/04-privacy.png" alt="Health Assist privacy and security screen" loading="lazy">
  <figcaption><strong>Your data stays yours.</strong>No analytics, no telemetry and no vendor cloud.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/05-sponsor.png" alt="Health Assist support screen with Sponsor My Work" loading="lazy">
  <figcaption><strong>Free software, funded by you.</strong>Sponsor My Work is optional and unlocks nothing.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/06-qr-setup.png" alt="Health Assist QR scanner" loading="lazy">
  <figcaption><strong>Scan once. Sync forever.</strong>The QR code carries the webhook URL and secret.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/07-appstore-search.png" alt="App Store search showing Health Assist" loading="lazy">
  <figcaption><strong>Find it on the App Store.</strong>Search “health assist”.</figcaption>
</figure>

<figure class="ha-shot">
  <img src="../images/store/08-appstore-product.png" alt="App Store product page for Health Assist" loading="lazy">
  <figcaption><strong>Built for your home.</strong>Free, with no subscription, account or in-app purchases.</figcaption>
</figure>

</div>


## App Store listing copy

| Field | Copy |
| --- | --- |
| **Name** | Health Assist |
| **Subtitle** | Apple Health to Home Assistant |
| **Promotional text** | Lightweight, local-first Apple Health sync for Home Assistant. Full history, background updates, no account and no vendor cloud. |
| **Keywords** | `home assistant,apple health,healthkit,health,sensors,automation,self-hosted,local,privacy,webhook` |
| **Support URL** | <https://healthassist.thebillington.co.uk/support/> |
| **Marketing URL** | <https://healthassist.thebillington.co.uk/> |
| **Privacy URL** | <https://healthassist.thebillington.co.uk/privacy/> |

### Description

<div class="ha-copy">
<p><strong>Health Assist connects Apple Health to your own Home Assistant — no vendor cloud, no account and no subscription.</strong></p>

<p>The app reads your Apple Health data with HealthKit and sends it straight to a webhook on your Home Assistant instance. Home Assistant creates native sensors and long-term statistics, so you can automate, chart and alert on your health data alongside the rest of your home.</p>

<p><strong>WHY HEALTH ASSIST</strong></p>
<ul>
  <li>Local-first: data goes from your iPhone to your Home Assistant, not to a vendor cloud.</li>
  <li>Free and open source: the iOS app and the Home Assistant integration are MIT licensed.</li>
  <li>No account: nothing to sign up for.</li>
  <li>No analytics or telemetry: the app contains no tracking SDKs.</li>
  <li>Full history: the first sync exports your available Apple Health history in resumable chunks, then keeps it up to date.</li>
  <li>Multi-device: add one integration entry per iPhone or iPad.</li>
</ul>

<p><strong>WHAT YOU NEED</strong></p>
<ul>
  <li>Home Assistant 2024.1 or newer.</li>
  <li>The free Health Assist integration, installed with HACS or manually from the project repository.</li>
  <li>iOS 18 or newer.</li>
  <li>A webhook URL and optional shared secret from the integration.</li>
</ul>

<p><strong>SETUP</strong></p>
<p>1. Install the Health Assist integration in Home Assistant.<br>
2. Add the integration and copy the webhook URL (and optional secret), or scan its QR code with the app.<br>
3. Grant read-only Apple Health access.<br>
4. Run a sync. Sensors appear in Home Assistant automatically.</p>

<p><strong>PRIVACY</strong><br>
Health Assist reads Apple Health only with your permission and never writes to it. Your data is sent only to the Home Assistant address you configure. The developer receives no health data.</p>

<p><strong>SUPPORT</strong><br>
Health Assist is free. If it saves you time, an optional Sponsor My Work link supports ongoing development. Sponsorship unlocks no features.</p>

<p class="ha-sub">Apple Health is a trademark of Apple Inc. Health Assist is not affiliated with or endorsed by Apple.</p>
</div>

### What's new

<div class="ha-copy">
<p>First App Store release. Read-only Apple Health sync to your own Home Assistant, full history export, background delivery, QR setup and an optional Sponsor My Work link.</p>
</div>

## Social card

![Health Assist social card](images/og.png)

## Social copy

### Short — X, Bluesky, Mastodon

> Your health, in your home.
>
> Health Assist is a free, local-first bridge from Apple Health to Home
> Assistant: full history, native sensors, no account, no vendor cloud.
>
> Open source: github.com/thebillington/health-assist

### Long — Mastodon, Threads, LinkedIn

> Apple Health finally speaks Home Assistant.
>
> Health Assist is a free, open-source iOS app plus a Home Assistant custom
> integration. It reads HealthKit read-only and pushes the data to a webhook on
> your own Home Assistant instance. The first sync exports your available
> history, then background delivery keeps it current.
>
> You get native sensors and long-term statistics for steps, sleep, heart rate,
> weight and more — no account, no analytics and no vendor cloud.
>
> iOS 18+, Home Assistant 2024.1+, MIT licensed.
>
> github.com/thebillington/health-assist

### Home Assistant community / Reddit

> Hi all — I built **Health Assist**, a free, open-source iOS app and custom
> integration that pushes Apple Health data to your own Home Assistant over a
> webhook.
>
> What it does today:
>
> - exports all available HealthKit history on the first sync, in resumable
>   chunks, then keeps it up to date;
> - turns the readings into native HA sensors with stable IDs, units and
>   long-term statistics;
> - supports one config entry per iPhone;
> - keeps the webhook URL and optional shared secret in the iOS Keychain;
> - has no account, analytics, telemetry or vendor cloud.
>
> It is read-only: the app never writes to Apple Health. Setup is paste the
> webhook (or scan the QR from the integration) and grant Health access.
>
> Repo and docs: github.com/thebillington/health-assist
>
> I would especially appreciate feedback on sensor naming, statistics metadata
> and anything that breaks on a real device.

## Boilerplate

> Health Assist is a free, open-source Home Assistant integration and iOS app
> that turns Apple Health data into native sensors. It is local-first: the app
> reads HealthKit read-only and sends data only to the user's own Home
> Assistant. MIT licensed. Apple Health is a trademark of Apple Inc.; Health
> Assist is not affiliated with Apple.

## Asset inventory

| Asset | Path |
| --- | --- |
| Logo lockup | [`docs/images/logo.svg`](https://github.com/thebillington/health-assist/blob/main/docs/images/logo.svg) |
| Mark | [`docs/images/logo-mark.svg`](https://github.com/thebillington/health-assist/blob/main/docs/images/logo-mark.svg) |
| App icon | [`docs/images/icon-512.png`](https://github.com/thebillington/health-assist/blob/main/docs/images/icon-512.png) |
| App Store boards | [`docs/images/store/`](https://github.com/thebillington/health-assist/tree/main/docs/images/store) |
| Social card | [`docs/images/og.png`](https://github.com/thebillington/health-assist/blob/main/docs/images/og.png) |
| Source screens | [`screenshots/`](https://github.com/thebillington/health-assist/tree/main/screenshots) |
| Full copy deck | [`appstore/PROMOTION.md`](https://github.com/thebillington/health-assist/blob/main/appstore/PROMOTION.md) |

## Notes

- Do not claim the app is on the App Store until the listing is live. Boards 7
  and 8, and the "coming soon" line, are written for that handover.
- Sponsor My Work is a donation link, not a purchase. Never imply it unlocks a
  feature, data or support.
- The app is free with no in-app purchases. Keep that consistent everywhere.
- Health data is sent only to the address the user configures. Do not describe
  it as "collected by us".
