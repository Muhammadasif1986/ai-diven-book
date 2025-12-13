/**
 * Script to verify ROI clarity in K-12 AI implementation content
 * This script analyzes book content to ensure education administrators can clearly understand the ROI
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Verifies ROI clarity in book content
 * @param {string} content - The book content to analyze
 * @returns {object} - Results containing ROI elements
 */
function verifyROIClarity(content) {
  // Patterns to identify ROI-related elements
  const roiPatterns = [
    /\b(cost|investment|expense|spending|budget)\b[\s\S]{0,100}\b(\d+|zero|significant|substantial|considerable)\b/gi,
    /\b(benefit|return|saving|reduction|decrease|gain|advantage|value|impact)\b[\s\S]{0,100}\b(\d+|significant|substantial|measurable|quantifiable)\b/gi,
    /\b(roi|return on investment|financial impact|cost benefit|economic benefit)\b/gi,
    /\b(financial|economic|monetary|dollar|budget|funding|expense|cost savings)\b[\s\S]{0,100}\b(\d+%|\d+\$|significant|measurable)\b/gi,
    /\b(administrative cost|teacher time|grading time|workload reduction|efficiency gain)\b[\s\S]{0,100}\b(\d+%|\d+\$|significant|measurable)\b/gi,
    /\b(quantitative|measure|metric|data|statistic|percentage|dollar amount)\b/gi
  ];

  const roiElements = [];
  roiPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      if (cleanMatch.length > 10) { // Avoid very short matches
        roiElements.push(cleanMatch);
      }
    });
  });

  // Extract quantitative measures
  const quantitativePatterns = [
    /\b\d+%\s*(reduction|decrease|increase|improvement|savings|gain|benefit)\b/gi,
    /\b\d+\s*(hour|minute|day|week|month|year)\s*(saved|reduced|gained)\b/gi,
    /\b\$\d{1,3}(,\d{3})*\s*(saved|cost|investment|saving|expense)\b/gi,
    /\b\d+:\d+\s*(roi|return|ratio)\b/gi,
    /\b(savings|reduction|improvement|increase)\s+of\s+\d+[%$]\b/gi
  ];

  const quantitativeMeasures = [];
  quantitativePatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      quantitativeMeasures.push(cleanMatch);
    });
  });

  // Extract financial impact statements
  const financialImpact = [];
  const financialPatterns = [
    /\$[\d,]+\s*(saved|cost|investment|expense|budget)[\s\S]{0,100}(annually|yearly|per year|initially)/gi,
    /(schools|districts|administrators|education)\s+report\s+[\s\S]{0,50}(saving|reduction|benefit|gain|impact)\s+of\s+\$[\d,]+/gi,
    /(cost|expense|spending)\s+(reduction|decrease|savings)\s+of\s+\$[\d,]+/gi
  ];

  financialPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      financialImpact.push(cleanMatch);
    });
  });

  // Check for administrator-focused language
  const adminFocusPatterns = [
    /\b(administrator|principal|superintendent|education leader|decision maker|policy maker)\b/gi,
    /\b(decision|consideration|implementation|strategy|planning)\b[\s\S]{0,50}\b(roi|cost|benefit|investment)\b/gi
  ];

  let adminFocusCount = 0;
  adminFocusPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    adminFocusCount += matches.length;
  });

  // Structure the results
  return {
    roiElements: [...new Set(roiElements)], // Remove duplicates
    quantitativeMeasures: [...new Set(quantitativeMeasures)], // Remove duplicates
    financialImpact: [...new Set(financialImpact)], // Remove duplicates
    administratorFocus: adminFocusCount > 2 ? true : false,
    totalElements: [...new Set(roiElements)].length + [...new Set(quantitativeMeasures)].length,
    status: ([...new Set(roiElements)].length >= 5 && [...new Set(quantitativeMeasures)].length >= 3) ? 'pass' : 'fail',
    requirement: 'Clear ROI explanation with quantitative measures for administrators'
  };
}

/**
 * Main function to run the ROI clarity verification on a book file
 * @param {string} bookPath - Path to the book content directory or file
 */
async function runROIAudit(bookPath) {
  try {
    let content = '';

    if (fs.statSync(bookPath).isDirectory()) {
      // If it's a directory, read all MDX files
      const files = await fs.readdir(bookPath);
      const mdxFiles = files.filter(file => file.endsWith('.mdx') || file.endsWith('.md'));

      for (const file of mdxFiles) {
        const filePath = path.join(bookPath, file);
        const fileContent = await fs.readFile(filePath, 'utf8');
        content += fileContent + ' ';
      }
    } else {
      // If it's a file, read it directly
      content = await fs.readFile(bookPath, 'utf8');
    }

    const result = verifyROIClarity(content);
    console.log('ROI Clarity Audit Results:');
    console.log(JSON.stringify(result, null, 2));

    // Write results to a file
    const resultsDir = path.join(process.cwd(), 'audit-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsPath = path.join(resultsDir, 'roi-verification-results.json');
    await fs.writeFile(resultsPath, JSON.stringify(result, null, 2));

    console.log(`Results saved to ${resultsPath}`);

    return result;
  } catch (error) {
    console.error('Error running ROI audit:', error);
    throw error;
  }
}

// Export functions for testing
module.exports = {
  verifyROIClarity,
  runROIAudit
};

// If this script is run directly, execute the audit
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node roi-verification.js <book-path>');
    process.exit(1);
  }

  runROIAudit(args[0])
    .catch(error => {
      console.error('Audit failed:', error);
      process.exit(1);
    });
}