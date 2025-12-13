# Scripts Directory

This directory contains all the audit scripts for the K-12 AI book project.

## Audit Scripts

### `audit/` subdirectory
Contains all the audit tools for verifying academic and technical compliance:

- `word-count.js` - Verifies book meets word count requirements (3,000-5,000 words)
- `citation-check.js` - Validates citations meet academic standards (8+ peer-reviewed sources from 2015-2025, APA format)
- `plagiarism-check.js` - Checks for content originality
- `readability-check.js` - Verifies Flesch-Kincaid readability score (grade 10-12)
- `link-validation.js` - Validates all internal and external links
- `build-validation.js` - Ensures Docusaurus build process works correctly
- `ai-applications.js` - Identifies AI applications with evidence in the content
- `roi-verification.js` - Verifies ROI clarity for education administrators
- `content-structure-validation.js` - Validates K-12 focus in content structure
- `teacher-workload-reduction.js` - Verifies teacher workload reduction claims
- `student-outcome-improvement.js` - Verifies student outcome improvement claims
- `comprehensive-audit.js` - Runs all audits and produces combined report

### `build/` subdirectory
Contains build-related scripts:
- `build-book.js` - Build and validation scripts for the book

## Usage

Run individual audits:
```bash
node scripts/audit/[script-name].js [path-to-book-content]
```

Run comprehensive audit:
```bash
node scripts/audit/comprehensive-audit.js [path-to-book-content]
```

Results are saved to the `audit-results/` directory.