# Sidharth Dinesh — academic website

A static academic website with separate About, Research, Publications, Projects, Experience, Gallery, and CV pages. The HTML, CSS, JavaScript, optimized media, and current CV are included. No framework or package installation is required to view it.

## Review locally

Open `index.html`, or run this command from the website folder:

```bash
python3 -m http.server 4000
```

Visit http://localhost:4000/. The separate lightweight HTML preview is for convenient review; it is not the deployment source.

## Edit and rebuild

Edit `content/site.json` for project details, repository links, employment, education, and media. Additional narrative text and page structure are in `scripts/build_site.py`. Regenerate the HTML after editing:

```bash
python3 scripts/build_site.py
```

The builder requires Python 3.12 or later. Direct HTML edits are overwritten on the next build. Replace `files/CV_Sidharth_Dinesh.pdf` when the CV changes.

## Repository links

All four projects link to their individual GitHub repositories. The publication entries link to `edge-video-processing`, which contains the thesis and related paper; the thesis entry does not repeat that link. GitHub profile links in the header and contact area intentionally remain profile links.

## Media and layout

All four projects have supplied media. Dinosaur previews on listing pages run at twice the original speed; its detail-page GIF and MP4 retain the original speed. Animation controls and reduced-motion stills are included.

The NYC map illustrates average taxi tips by zone, rather than the hotspot computation's output, and is labeled accordingly. The Facebook illustration reproduces the supplied dataset slide's text and table. Research figures use compact grids. Gallery photographs use equal display frames and short captions; original image proportions are preserved in the underlying files.

Work entries have no image placeholders. Presentation slide-deck and recording links are omitted; the presentation image remains. Optional demo/report fields are empty and hidden, with no unfinished buttons shown. Add a URL only when that material is ready to publish.

## Footer

The footer shows copyright, personal email, and the last-update date. The date uses the latest Git commit timestamp in America/Phoenix, falling back to the build date outside a Git checkout. `SITE_LAST_UPDATED` can supply an ISO timestamp for a reproducible build. Rebuild after committing if publishing the generated HTML manually.

## Publish on GitHub Pages

Copy the contents of this website folder into the website repository. The included `.github/workflows/pages.yml` builds and publishes on pushes to `main` or `master`. In Settings → Pages, choose **GitHub Actions** as the source. Keep only one active Pages deployment workflow when replacing an older site.

The workflow stages only public HTML pages, assets, and the CV. Configuration, source scripts, and this README are not served. The `.nojekyll` file supports direct static serving as well.

This package has not been deployed. Its repository URLs are the links supplied by Sidharth; their public accessibility and contents were not audited as part of the link update.
