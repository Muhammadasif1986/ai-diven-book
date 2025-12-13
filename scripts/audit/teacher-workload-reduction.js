/**
 * Script to verify teacher workload reduction claims in content
 * This script analyzes book content to identify and validate claims about AI reducing teacher workload
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Verifies teacher workload reduction content in book
 * @param {string} content - The book content to analyze
 * @returns {object} - Results containing workload reduction verification
 */
function verifyTeacherWorkloadReduction(content) {
  // Patterns to identify teacher workload reduction claims
  const workloadReductionPatterns = [
    /\b(teacher|instructor|educator)\s+(workload|time|burden|load|effort|tasks|responsibility)\b[\s\S]{0,100}\b(reduction|decrease|save|reduce|ease|lighten|relief)\b/gi,
    /\b(reduction|decrease|save|reduce|ease|lighten)\s+of\s+(teacher|instructor|educator)\s+(workload|time|burden|load|effort|tasks|responsibility)\b/gi,
    /\b(automated|streamlined|efficient|simplified)\s+(grading|assessment|feedback|reporting|administrative|planning)\s+for\s+(teacher|instructor|educator)\b/gi,
    /\b(grading|assessment|feedback|reporting|administrative|planning)\s+(time|hours|effort)\s+(reduced|saved|decreased)\b/gi,
    /\b(ai|automated|artificial intelligence)\s+helps\s+(teacher|instructor|educator)\s+(save|reduce|cut)\s+(time|hours)\b/gi
  ];

  const workloadReductionClaims = [];
  workloadReductionPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      if (cleanMatch.length > 15) { // Avoid very short matches
        workloadReductionClaims.push(cleanMatch);
      }
    });
  });

  // Look for quantitative measures of workload reduction
  const quantitativePatterns = [
    /\b(\d+%)|(reduced by \d+)|(decreased by \d+)|(savings of \d+ hours?)\s+(of teacher|for teachers?|teacher's?|educator's?)\s+(workload|time|tasks|grading|assessment|feedback|planning|administrative work)\b/gi,
    /\b(teacher|instructor|educator)\s+(workload|time|tasks|grading|assessment|feedback|planning|administrative work)\s+(reduced|decreased|cut|saved)\s+by\s+(\d+%)|(\d+\s+hours?)\b/gi
  ];

  const quantitativeMeasures = [];
  quantitativePatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      quantitativeMeasures.push(cleanMatch);
    });
  });

  // Look for specific AI applications that reduce workload
  const aiWorkloadApps = [
    'automated grading',
    'intelligent tutoring systems',
    'automated feedback generation',
    'adaptive assessment',
    'automated report writing',
    'AI-powered lesson planning',
    'automated attendance tracking',
    'AI-powered content curation',
    'automated plagiarism detection',
    'smart classroom management'
  ];

  const identifiedApps = aiWorkloadApps.filter(app =>
    content.toLowerCase().includes(app.toLowerCase())
  );

  // Look for evidence or studies supporting workload reduction
  const evidencePatterns = [
    /\b(study|research|evidence|data|survey|report)\b[\s\S]{0,150}\b(workload|time saving|efficiency|teacher satisfaction)\b/gi,
    /\b(workload|time saving|efficiency|teacher satisfaction)\b[\s\S]{0,150}\b(study|research|evidence|data|survey|report)\b/gi,
    /\b(found|showed|demonstrated|indicated)\s+that\s+ai[\s\S]{0,100}\b(reduced|decreased|saved|eased)\s+(teacher|educator)\s+(workload|time|tasks)\b/gi
  ];

  const evidenceClaims = [];
  evidencePatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      evidenceClaims.push(cleanMatch);
    });
  });

  return {
    workloadReductionClaims: [...new Set(workloadReductionClaims)],
    quantitativeMeasures: [...new Set(quantitativeMeasures)],
    aiApplications: [...new Set(identifiedApps)],
    evidenceClaims: [...new Set(evidenceClaims)],
    totalIndicators: [...new Set(workloadReductionClaims)].length + [...new Set(quantitativeMeasures)].length + identifiedApps.length,
    status: ([...new Set(workloadReductionClaims)].length >= 3 && identifiedApps.length >= 2) ? 'pass' : 'fail',
    requirement: 'Content includes teacher workload reduction verification with evidence'
  };
}

/**
 * Main function to run the teacher workload reduction verification on a book file
 * @param {string} bookPath - Path to the book content directory or file
 */
async function runTeacherWorkloadAudit(bookPath) {
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

    const result = verifyTeacherWorkloadReduction(content);
    console.log('Teacher Workload Reduction Verification Results:');
    console.log(JSON.stringify(result, null, 2));

    // Write results to a file
    const resultsDir = path.join(process.cwd(), 'audit-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsPath = path.join(resultsDir, 'teacher-workload-reduction-results.json');
    await fs.writeFile(resultsPath, JSON.stringify(result, null, 2));

    console.log(`Results saved to ${resultsPath}`);

    return result;
  } catch (error) {
    console.error('Error running teacher workload reduction verification:', error);
    throw error;
  }
}

// Export functions for testing
module.exports = {
  verifyTeacherWorkloadReduction,
  runTeacherWorkloadAudit
};

// If this script is run directly, execute the verification
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node teacher-workload-reduction.js <book-path>');
    process.exit(1);
  }

  runTeacherWorkloadAudit(args[0])
    .catch(error => {
      console.error('Verification failed:', error);
      process.exit(1);
    });
}