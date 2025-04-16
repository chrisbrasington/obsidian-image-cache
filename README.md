# Obsidian Image Cache Script

This script scans all Markdown files in your Obsidian vault for image URLs stored in the following frontmatter fields:

- `coverUrlPortrait`
- `coverUrl`
- `image`

It downloads each found image to a local `.img/` folder at the root of your vault, using the original filename (e.g., `header.jpg`, `c84adb3f9...jpg`).

## Features

- Recursively scans all `.md` files
- Skips download if image is already cached
- Prints out each image found, where it’s downloaded from, and the file it came from

## Usage

```bash
python cache_images.py ~/obsidian
```

> Replace `~/obsidian` with the path to your Obsidian vault.

---

## 🔧 Using Cached Images in Obsidian with DataviewJS

Here's a simple snippet showing how you can check if a local `.img/` image exists, and fall back to the URL if not:

```js
const adapter = app.vault.adapter;
const originalUrl = file.coverUrl ?? file.image;
const imageFilename = originalUrl?.split('/').pop();
const localPath = `img/${imageFilename}`;

let imgSrc = originalUrl;

if (imageFilename) {
  const exists = await adapter.exists(localPath);
  if (exists) {
    const fileObj = app.vault.getAbstractFileByPath(localPath);
    if (fileObj) {
      imgSrc = app.vault.getResourcePath(fileObj);
    }
  }
}

dv.paragraph(`![cover](${imgSrc})`);
```

This makes your DataviewJS cards or pages load faster by using local images if available.
