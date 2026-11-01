/**
 * Open Screenshot Generator config.
 *
 * This file is the source of truth for how this app's store assets look. A
 * flag on one run is a try, an edit in here is a decision, so anything worth
 * keeping belongs in this file and gets committed next to the code it sells.
 *
 * Every field is optional and every value below is what the CLI would infer on
 * its own, so deleting a line changes nothing. Commented fields are the ones
 * with no inferred value: uncomment one and it overrides the template.
 *
 * The type comes from the package. If your editor cannot resolve it, run
 * npm i -D open-screenshot-generator. The import is erased before the file is
 * loaded, so the config works either way.
 */
import type { OsgConfig } from 'open-screenshot-generator';

const config: OsgConfig = {
  // Used in output filenames, in osg.manifest.json, and by the AI agent as the
  // name of the app it is writing copy for.
  name: 'Health Assist',

  // The committed project file. Every command reads and writes this one file,
  // so reviewing a design change is reading a diff.
  project: 'osg/project.json',

  // Where rendered PNGs, MP4s and the manifest land. Ignored by git.
  out: 'osg/out',

  // Your app's own screenshots, the images that go inside the device frames.
  // They are used in filename order, so name them 01-, 02-, 03-.
  screenshots: 'screenshots',

  // 'auto' ranks the 101 bundled templates against your screenshots and picks
  // one. Pin an id from "osg templates" to stop it changing between runs.
  template: 'template_somnia-sleep',

  // Store size presets to render. Run "osg render --help" for the full list.
  formats: ['ios-6-9'],

  // The languages the listing ships in. Uncomment once "osg localize --add"
  // has actually put them in the project: a project with no languages renders
  // whatever is on the canvas, which is what you want until then.
  // locales: ['en-US', 'de-DE', 'ja'],
  // baseLocale: 'en-US',

  // Decides which store's rules "osg verify" enforces, and what "osg upload"
  // talks to. 'appstore' or 'play'.
  store: 'appstore',

  // Applied on top of whatever the template already says. Every field here is
  // a deliberate override, which is why none of them are set by default.
  design: {
    // background: '#0B1020',
    // background: 'linear-gradient(135deg, #6366F1, #22D3EE)',
    // headlineFont: 'Inter',
    // headlineColor: '#FFFFFF',
    // subheadColor: '#B4B9C9',
    // device: 'iphone-17-pro-max',
    // layout: 'alternating',
  },

  video: {
    // 'store-raw' is the screen recording alone, which is what Apple prefers.
    // 'store-text' adds the board's headlines. 'styled' animates the whole
    // board, which reads better on social than it does in the store.
    mode: 'store-raw',
    fps: 30,
    // Seconds. Apple accepts 15 to 30.
    duration: 20,
    // A screen recording on disk, served to the page during the run.
    // recording: 'osg/recording.mp4',
  },

  ai: {
    // Only "osg design" reads this. Everything else is model free.
    // provider: 'anthropic',
    // model: 'claude-sonnet-4-5',
    // baseUrl: 'https://api.openai.com/v1',

    // Never put a key in this file. Name the variable that holds it.
    apiKeyEnv: 'OSG_API_KEY',
  },

  // Where the artwork the templates paint is hydrated from, cached per machine
  // after the first run.
  // assetsBaseUrl: 'https://editor.openscrgen.app',

  // Drive a running editor instead of the bundled one, for example a local
  // "npm run dev" while you are working on the app itself.
  // editorUrl: 'http://localhost:9002',

  // An explicit browser. Chrome and Edge can encode MP4, open Chromium builds
  // cannot, so name one here if the CLI picks the wrong build.
  // browser: '/path/to/chrome',
};

export default config;
