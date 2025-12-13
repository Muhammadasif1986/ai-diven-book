# Quickstart Guide: Audit K-12 AI Book

## Overview
This guide provides instructions for setting up and running the audit process for the K-12 AI book.

## Prerequisites
- Node.js v18+ installed
- Git installed
- Access to the repository

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Navigate to the website directory:
   ```bash
   cd my-website
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

## Running the Audit Process

### 1. Full Audit
Run all audit checks in sequence:
```bash
npm run audit:full
```

### 2. Individual Audit Steps
Run specific audit checks:

- Word count verification:
  ```bash
  npm run audit:word-count
  ```

- Citation verification:
  ```bash
  npm run audit:citations
  ```

- Readability check:
  ```bash
  npm run audit:readability
  ```

- Plagiarism check:
  ```bash
  npm run audit:plagiarism
  ```

- Link validation:
  ```bash
  npm run audit:links
  ```

- Build validation:
  ```bash
  npm run audit:build
  ```

## Audit Results
Audit results are stored in the `audit-results/` directory with detailed reports for each check.

## Correcting Issues
After running the audit, address any issues found:

1. Check the audit reports in `audit-results/`
2. Update content in `docs/` directory as needed
3. Update citations and references following APA 7th edition format
4. Verify word count is between 3,000-5,000 words
5. Ensure 8+ peer-reviewed sources from 2015-2025
6. Confirm 3+ AI applications with empirical evidence
7. Re-run the audit to verify corrections

## Deployment
After all audits pass, build and deploy the book:

```bash
npm run build
```

The built site will be in the `build/` directory and ready for deployment to GitHub Pages.

## Key Requirements Checklist
Before final deployment, ensure:
- [ ] Word count: 3,000-5,000 words
- [ ] Citations: 8+ peer-reviewed sources (2015-2025)
- [ ] APA format: All citations properly formatted
- [ ] 3+ AI applications with evidence
- [ ] ROI clearly explained for administrators
- [ ] Readability: Flesch-Kincaid grade 10-12
- [ ] Zero plagiarism detected
- [ ] All links functional
- [ ] Mobile responsive
- [ ] Accessible (WCAG 2.1 AA)