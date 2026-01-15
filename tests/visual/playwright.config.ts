import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: path.join(__dirname),
  timeout: 60_000,
  expect: {
    toMatchSnapshot: { threshold: 0.02 },
  },
  use: {
    headless: true,
    viewport: { width: 1280, height: 800 },
    ignoreHTTPSErrors: true,
    baseURL: 'http://127.0.0.1:3000',
  },
  webServer: {
    command: 'python -m http.server 3000 -d public',
    url: 'http://127.0.0.1:3000',
    timeout: 30_000,
    reuseExistingServer: true,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});