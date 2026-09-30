import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { resolve } from 'node:path';

// This publishing step uses only Node's built-in modules. The website is prebuilt.
const root = resolve(import.meta.dirname, '..');
const output = resolve(root, 'public');
await mkdir(output, { recursive: true });
const configured = process.env.SITE_URL || process.env.VERCEL_PROJECT_PRODUCTION_URL || process.env.VERCEL_URL;
let origin = 'https://speedyhosting.example';
if (configured) {
  const url = new URL(configured.includes('://') ? configured : `https://${configured}`);
  if (!['https:', 'http:'].includes(url.protocol)) throw new Error('SITE_URL must use HTTPS or HTTP.');
  origin = url.origin;
}
const standalone = await readFile(resolve(root, 'index.html'), 'utf8');
await writeFile(resolve(output, 'index.html'), standalone.replaceAll('https://speedyhosting.example', origin));
for (const file of ['speedy-logo.svg', 'social-preview.jpg']) {
  await copyFile(resolve(root, file), resolve(output, file));
}
console.log(`Prepared standalone public website. SEO origin: ${origin}`);
