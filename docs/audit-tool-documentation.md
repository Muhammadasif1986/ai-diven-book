# Audit Tool Documentation

## Purpose
This documentation describes the audit tools created to verify academic and technical compliance of the K-12 AI book. These tools ensure the book meets all requirements including word count (3,000-5,000 words), citation compliance (8+ peer-reviewed sources from 2015-2025), APA format correctness, ROI clarity for administrators, and technical functionality.

## Responsibilities
- **Academic Compliance Audit**: Verifies word count, citation standards, and academic rigor
- **Technical Functionality Audit**: Ensures Docusaurus build and deployment work correctly
- **Content Quality Audit**: Validates ROI clarity and AI application identification
- **Comprehensive Audit**: Combines all audit components into a single report

## Input/Output Specifications

### Input
- `bookPath`: Path to the book content directory (typically `my-website/docs/`)

### Output
- JSON reports saved to `audit-results/` directory
- Individual audit results for each component
- Comprehensive summary report

## Dependencies
- Node.js v18+
- Docusaurus v3
- Standard Node.js file system and path modules
- Jest for testing (optional)

## Usage Examples

### Running Individual Audits
```bash
# Word count verification
node scripts/audit/word-count.js my-website/docs/

# Citation verification
node scripts/audit/citation-check.js my-website/docs/

# AI application identification
node scripts/audit/ai-applications.js my-website/docs/

# ROI clarity verification
node scripts/audit/roi-verification.js my-website/docs/
```

### Running Comprehensive Audit
```bash
# Run all audits in sequence
node scripts/audit/comprehensive-audit.js my-website/docs/
```

### Using npm Scripts (Recommended)
```bash
# Full audit
npm run audit:full

# Individual audits
npm run audit:word-count
npm run audit:citations
npm run audit:readability
npm run audit:ai-applications
npm run audit:roi
```

## Error Handling
- Each audit script handles file system errors gracefully
- Invalid paths result in clear error messages
- Network errors (for external validation) are caught and reported
- Parsing errors are logged with context

## Performance Considerations
- Audits complete in under 5 minutes for typical book content
- Efficient pattern matching algorithms used for content analysis
- Results are cached where appropriate to avoid redundant processing
- Memory usage is optimized for large content files

## Testing
All audit scripts include comprehensive Jest tests in the `tests/audit/` directory. Run tests with:
```bash
npm test
# or for specific audit tests:
npm run test:audit
```

## Integration
The audit tools integrate with the Docusaurus build process and can be run as pre-commit hooks to ensure content quality before deployment.