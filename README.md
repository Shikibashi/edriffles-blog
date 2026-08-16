# Astro Starter Kit: Blog

```sh
npm create astro@latest -- --template blog
```

> 🧑‍🚀 **Seasoned astronaut?** Delete this file. Have fun!

Features:

- ✅ Minimal styling (make it your own!)
- ✅ 100/100 Lighthouse performance
- ✅ SEO-friendly with canonical URLs and Open Graph data
- ✅ Sitemap support
- ✅ RSS Feed support
- ✅ Markdown & MDX support

## 🚀 Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── content/
│   ├── layouts/
│   └── pages/
├── astro.config.mjs
├── README.md
├── package.json
└── tsconfig.json
```

Astro looks for `.astro` or `.md` files in the `src/pages/` directory. Each page is exposed as a route based on its file name.

There's nothing special about `src/components/`, but that's where we like to put any Astro/React/Vue/Svelte/Preact components.

The `src/content/` directory contains "collections" of related Markdown and MDX documents. Use `getCollection()` to retrieve posts from `src/content/blog/`, and type-check your frontmatter using an optional schema. See [Astro's Content Collections docs](https://docs.astro.build/en/guides/content-collections/) to learn more.

Any static assets, like images, can be placed in the `public/` directory.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Installs dependencies                            |
| `npm run dev`             | Starts local dev server at `localhost:4321`      |
| `npm run build`           | Build Astro output locally to `./dist/`          |
| `npm run build:production` | Build, publish Standard.site records, and inject verification links |
| `npm run build:cloudflare` | Select the production or preview build for Cloudflare Pages |
| `npm run preview`         | Preview your build locally, before deploying     |
| `npm run audit:standard-site` | Run the read-only Standard.site interoperability audit |
| `npm run astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `npm run astro -- --help` | Get help using the Astro CLI                     |

## Standard.site and Cloudflare Pages

The Cloudflare Pages build command should be `npm run build:cloudflare` and the
build output directory should be `dist`. On the configured production branch
(currently `master`), the command runs this pipeline:

```text
astro build → sequoia publish → sequoia inject --output dist
```

Set `ATP_IDENTIFIER` and `ATP_APP_PASSWORD` as encrypted variables in the
Cloudflare Pages **Production** environment only. Preview builds use Astro only,
even if those variables are accidentally present there. If the production
branch changes, set the non-secret `CF_PAGES_PRODUCTION_BRANCH` variable to the
new branch name in both Cloudflare environments; it defaults to `master`.

`sequoia publish` and `sequoia sync` are the only commands intended to interact
with AT Protocol records. Use `npm run sequoia:sync` manually to reconstruct
the ignored `.sequoia-state.json` from records already on the PDS. The audit
command performs read-only HTTP/XRPC requests and never applies remediation;
append `--strict` when warnings should also fail CI.

## Homepage images

Homepage images are managed through the hosted [Pages CMS](https://app.pagescms.org/).
Sign in with GitHub, install the Pages CMS GitHub App for this repository, and
open the **Homepage images** collection. Each entry only needs an image; alt
text is optional but recommended. Pages CMS writes the image entry and its
asset directly to GitHub, and the normal Cloudflare production build publishes
it on `/`.

Image entries live under `src/content/gallery/` and do not create blog routes.
Written posts remain separate, manually authored Markdown files under
`src/content/blog/`. The repository's `.pages.yml` is the Pages CMS schema;
there is no CMS server or `/admin` application to maintain. Sequoia remains the
authority for Standard.site records and runs in the production build.

## 👀 Want to learn more?

Check out [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).

## Credit

This theme is based off of the lovely [Bear Blog](https://github.com/HermanMartinus/bearblog/).
