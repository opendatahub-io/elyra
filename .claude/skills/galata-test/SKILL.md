---
name: galata-test
description: Write Galata/Playwright UI integration tests for JupyterLab extensions in this elyra project
---

# Write Galata Tests for JupyterLab

You are an expert in writing UI integration tests using **Galata** — the official JupyterLab testing framework built on Playwright. Your task is to write production-quality Galata tests for the feature or component described by the user.

## What is Galata

Galata (`@jupyterlab/galata`) wraps Playwright and provides JupyterLab-specific helpers:
- `IJupyterLabPageFixture` — the `page` fixture, augmented with JupyterLab-aware methods
- High-level APIs for notebooks, the file browser, menus, panels, and the status bar
- Visual regression via `page.compareScreenshot()`
- Content helpers to create/upload/delete files before and after tests

## Project Context

This project is the **ODH fork of elyra-ai/elyra**, a set of JupyterLab extensions. The existing integration test suite uses **Cypress** (in `cypress/tests/`). Galata tests are a **new addition** and should live in a `ui-tests/` directory at the repository root, following standard JupyterLab extension conventions.

> **Airflow is permanently out of scope.** Never write tests for anything under `elyra/airflow/` or for the Airflow pipeline processor.

Active runtimes and surfaces to test:
- **KFP (Kubeflow Pipelines)** pipeline editor and submission
- **Local** pipeline processor
- Python script editor (`packages/python-editor`)
- Pipeline editor (`packages/pipeline-editor`)
- Metadata UI (`packages/metadata`, `packages/metadata-common`)
- Code snippet manager (`packages/code-snippet`)

## File Layout

```
ui-tests/
├── playwright.config.ts      # Playwright + Galata config
├── package.json              # devDependency: @jupyterlab/galata
├── tsconfig.json
└── tests/
    └── <feature>.test.ts     # Test files — one per feature/surface
```

## Standard Test File Structure

```typescript
import { expect } from '@playwright/test';
import { test } from '@jupyterlab/galata';

test.describe('<Feature> Tests', () => {
  // Upload or create files needed by all tests in this suite
  test.beforeEach(async ({ page, tmpPath }) => {
    // tmpPath is a unique temporary directory per test run
    await page.contents.uploadFile(
      'path/to/fixture.ipynb',
      `${tmpPath}/fixture.ipynb`
    );
    await page.filebrowser.openDirectory(tmpPath);
  });

  // Clean up after each test
  test.afterEach(async ({ page, tmpPath }) => {
    await page.contents.deleteDirectory(tmpPath);
  });

  test('should <do something>', async ({ page }) => {
    // Arrange: open a file, navigate to a panel, etc.
    // Act: click, type, select
    // Assert: expect DOM state, screenshots, or API responses
  });
});
```

## Key Galata APIs

### File browser and navigation
```typescript
await page.filebrowser.openDirectory(path);
await page.filebrowser.open(filename);          // open a file in the editor
await page.sidebar.openTab('filebrowser');
```

### Menus
```typescript
await page.menu.clickMenuItem('File>New>Notebook');
await page.menu.clickMenuItem('Run>Run All Cells');
```

### Notebooks
```typescript
await page.notebook.open('notebook.ipynb');
await page.notebook.runAllCells();
await page.notebook.waitForRun();
const cellOutput = await page.notebook.getCellOutput(0); // by index
await page.notebook.addCell('code', 'print("hello")');
await page.notebook.save();
```

### Activity bar / panels / tabs
```typescript
await page.activity.activateTab('notebook.ipynb');
await page.activity.closeTab('notebook.ipynb');
await page.sidebar.openTab('jp-property-inspector');
```

### Waiting and assertions
```typescript
await page.waitForSelector('.jp-Notebook');
await expect(page.locator('.jp-NotebookPanel')).toBeVisible();
await page.waitForCondition(() => page.evaluate(() => /* browser expr */ true));
```

### Visual regression
```typescript
expect(await page.screenshot()).toMatchSnapshot('feature-state.png');
// or for a specific element:
expect(await page.locator('.jp-PipelineEditor').screenshot()).toMatchSnapshot();
```

### Contents API (file management in tests)
```typescript
await page.contents.uploadFile(localPath, remotePath);
await page.contents.downloadFile(remotePath);           // returns Buffer
await page.contents.deleteFile(remotePath);
await page.contents.deleteDirectory(remotePath);
await page.contents.createDirectory(remotePath);
```

### Kernel interactions
```typescript
await page.kernel.shutdownAll();
const kernelStatus = await page.kernel.status('notebook.ipynb');
```

## playwright.config.ts Template

```typescript
import { defineConfig } from '@playwright/test';
import { baseConfig } from '@jupyterlab/galata';

export default defineConfig({
  ...baseConfig,
  webServer: {
    command: 'jupyter lab --no-browser --port 8888',
    url: 'http://localhost:8888/lab',
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
  use: {
    ...baseConfig.use,
    baseURL: 'http://localhost:8888',
  },
  testDir: 'tests',
});
```

## Writing Guidelines

1. **One `test.describe` block per feature or surface.** Don't mix pipeline editor tests with metadata tests in the same file.

2. **Use `tmpPath` for all file fixtures.** Each test gets an isolated directory — don't write to the root.

3. **Prefer `page.locator()` with semantic selectors** (ARIA roles, data-testid, JP CSS classes like `.jp-PipelineEditor`) over brittle nth-child or pixel coords.

4. **Await every async call.** Galata/Playwright operations are always async.

5. **Don't add `page.waitForTimeout()` sleeps.** Use explicit condition waits (`waitForSelector`, `waitForResponse`, `waitForFunction`) instead.

6. **Cover the unhappy path.** If a feature can fail (bad input, network error, missing dependency), write a test for it.

7. **Screenshot tests are optional but valuable** for visual components like the pipeline canvas. Name snapshots descriptively.

8. **Skip Airflow.** Do not write tests for the Airflow processor, `elyra/airflow/`, or any Airflow-related UI.

## Your Task

Based on the feature or component the user describes (or the code they point you to), do the following:

1. **Read the relevant source files** in `packages/` and `elyra/` to understand the component's behavior, API surface, and existing test patterns.
2. **Identify the meaningful user flows** to cover — happy path, error states, edge cases.
3. **Write the Galata test file(s)** in `ui-tests/tests/<feature>.test.ts`, following all conventions above.
4. **If `ui-tests/` does not yet exist**, also generate a minimal `playwright.config.ts` and `package.json` scaffold so the tests can run immediately.
5. **Do not write tests for Airflow.**

Begin by asking the user which feature or component to target if they haven't specified one.
