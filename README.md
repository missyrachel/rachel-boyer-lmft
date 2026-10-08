# Rachel Boyer website and editing dashboard

Prepared for the existing rachelboyerlmft.com Netlify project (chic-elf-916778).
This source package is for GitHub-connected publishing, not Netlify Drop.
The repository is configured. Netlify connection, OAuth setup, and an authenticated editor publish test are still required.

## Features

- Existing lavender design, headshot, contact links, Headway booking, and original reflection PDF.
- Decap editor at `/admin/` for fees, hours, contact details, ten website text sections, and reflections.
- Reflections support drafts using “Show on website”, categories, images, and optional PDF downloads.
- Automatically generated, searchable reflections page at `/reflections/`.
- Existing `/understanding-before-judging` and `.html` links continue to work with Netlify Pretty URLs.
- Only GitHub users with write access to the configured repository can save through Decap. No open editor registration.
- No inquiry form or patient information storage is included. Therapy booking goes to Headway; email remains an email-app link.

## Connection steps

1. Source repository: `missyrachel/rachel-boyer-lmft`, branch `main`. This existing repository is public. Unpublished reflections are excluded from the website, but their source text is visible on GitHub; do not put private material in drafts. Older starter files are retained in `legacy-starter/`.
2. Run `python3 configure.py VERIFIED_OWNER/VERIFIED_REPOSITORY` with the actual repository name and commit `cms/repository.json`. Alternatively set the `CMS_REPOSITORY` environment variable in Netlify. There are no stored credentials in the source.
3. In the existing Netlify project, connect that GitHub repository and `main` branch. Use the settings in `netlify.toml`: build command `pip install -r requirements.txt && python3 build.py`, publish directory `dist`. Keep the current domain and email DNS records unchanged.
4. Create a GitHub OAuth application in the owner's account for the website editor. Homepage: `https://rachelboyerlmft.com`. Callback: `https://api.netlify.com/auth/done`.
5. In the existing Netlify project's Security → OAuth → Authentication Providers, install GitHub using that OAuth app's client ID and secret. Enter the secret directly into Netlify; never commit it or paste it in chat. GitHub/Netlify may require owner approval.
6. Verify the deploy preview before publishing. Open `/admin/`, sign in with the repository owner's GitHub account, save a small reversible change, and confirm the resulting Netlify deploy and live page.

Official setup references:
- https://decapcms.org/docs/github-backend/
- https://docs.netlify.com/manage/security/secure-access-to-sites/oauth-provider-tokens/

## Editing after activation

Open `https://rachelboyerlmft.com/admin/` and sign in with GitHub.

- **Fees, hours & contact:** change session prices, durations, hours, email, phone, headshot, and Headway URL. Shared values update wherever generated.
- **Website text:** select the relevant section and edit its headings or paragraphs. Keep links in rich text where appropriate.
- **Reflections:** create or edit a reflection. Leave **Show on website** off while drafting. Turn it on when ready, then publish. Keep an existing article's filename stable to preserve its links.
- Publishing commits to GitHub and starts a Netlify build. It is not instant; wait for a successful deploy. Each production deploy and visitor traffic consume hosting allowance.
- PDFs are separate documents and do not update when article text changes. Replace the PDF or remove its link when needed. The existing PDF is labeled as the original reflection.

Netlify's free allowance is finite; check account usage before enabling frequent publishing. This package does not enable paid add-ons or auto-recharge.

## Local validation

Install `requirements.txt`, then run `python3 build.py --preview`. Without a repository configured, preview builds deliberately show an editor setup notice instead of a nonfunctional login screen. A normal production build fails until a repository is configured.

Generated pages are in `dist/`. Source content lives in `content/`; templates live in `templates/`. Do not edit `dist/` as the next build replaces it. The standard build excludes drafts and clears stale generated articles.

## Validation status

Local build and content-change checks can verify rendering and links. GitHub login, authenticated saving, automatic deployment, and the live editor require the owner's account connections and have not yet been verified.
