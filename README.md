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

## Sveltia CMS

The Sveltia CMS editor is available at `/admin/index.html`. Run
`astro dev --background` and open `http://localhost:4321/admin/index.html` for
local editing, or use the same path on the deployed site. The public
configuration contains no credentials; Sveltia will ask for GitHub
authentication in the browser.

Blog posts are created as page bundles under `src/content/blog/<slug>/index.md`.
In Sveltia, choose **Homepage / hero image** to upload the image that should
appear on the homepage photo index, blog index, and post page, then provide
**Image alt text**. The uploaded file is stored beside its post, so Astro
resolves it through the `image()` content schema and optimizes it during the
build. Title, Description, and Body are optional for image-only posts. Sveltia
generates a short unique URL slug automatically when Title is blank, and the
image alt text is used for the tile and page metadata. Images inserted in the
Body field are also stored beside the post and rendered from Markdown.
Saving a post to the `master` branch triggers the normal Cloudflare production
build, including the Sequoia publish/inject steps. Keep Sequoia as the
authority for Standard.site records; Sveltia only edits the Markdown and its
adjacent assets.

## 👀 Want to learn more?

Check out [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).

## Credit

This theme is based off of the lovely [Bear Blog](https://github.com/HermanMartinus/bearblog/).
