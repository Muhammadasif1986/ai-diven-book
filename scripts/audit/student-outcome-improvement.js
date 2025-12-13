/**
 * Script to verify student outcome improvement claims in content
 * This script analyzes book content to identify and validate claims about AI improving student outcomes
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Verifies student outcome improvement content in book
 * @param {string} content - The book content to analyze
 * @returns {object} - Results containing student outcome improvement verification
 */
function verifyStudentOutcomeImprovement(content) {
  // Patterns to identify student outcome improvement claims
  const outcomeImprovementPatterns = [
    /\b(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b[\s\S]{0,100}\b(improved|improvement|increase|enhanced|boost|gain|better|higher)\b/gi,
    /\b(improved|improvement|increase|enhanced|boost|gain|better|higher)\s+(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b/gi,
    /\b(ai|artificial intelligence|adaptive learning|personalized learning)\s+(improved|improvement|increase|enhanced|boost|gain|better|higher)\s+(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b/gi,
    /\b(learning|academic|educational)\s+(outcome|performance|achievement|success)\s+(improved|improvement|increase|enhanced|boost|gain|better|higher)\s+by\s+(ai|artificial intelligence|technology)\b/gi
  ];

  const outcomeImprovementClaims = [];
  outcomeImprovementPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      if (cleanMatch.length > 15) { // Avoid very short matches
        outcomeImprovementClaims.push(cleanMatch);
      }
    });
  });

  // Look for quantitative measures of student outcome improvement
  const quantitativePatterns = [
    /\b(\d+%)|(improved by \d+)|(increased by \d+)|(gains of \d+ points?)\s+(in|for|of)\s+(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score|test|grade)\b/gi,
    /\b(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score|test|grade)\s+(improved|increased|enhanced|boosted)\s+by\s+(\d+%)|(\d+\s+points?)\b/gi,
    /\b(\d+%|significant|measurable)\s+improvement\s+in\s+(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b/gi
  ];

  const quantitativeMeasures = [];
  quantitativePatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      quantitativeMeasures.push(cleanMatch);
    });
  });

  // Look for specific AI applications that improve student outcomes
  const aiOutcomeApps = [
    'intelligent tutoring systems',
    'adaptive learning platforms',
    'personalized learning algorithms',
    'AI-powered content recommendation',
    'learning analytics',
    'automated feedback systems',
    'predictive analytics for student success',
    'AI-powered language learning',
    'virtual teaching assistants',
    'automated essay scoring',
    'personalized learning pathways',
    'AI-powered assessment tools'
  ];

  const identifiedApps = aiOutcomeApps.filter(app =>
    content.toLowerCase().includes(app.toLowerCase())
  );

  // Look for evidence or studies supporting outcome improvement
  const evidencePatterns = [
    /\b(study|research|evidence|data|trial|experiment|survey|report)\b[\s\S]{0,150}\b(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b/gi,
    /\b(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b[\s\S]{0,150}\b(study|research|evidence|data|trial|experiment|survey|report)\b/gi,
    /\b(found|showed|demonstrated|indicated|proved)\s+that\s+ai[\s\S]{0,100}\b(improved|enhanced|increased)\s+(student|learner|pupil)\s+(outcome|performance|achievement|engagement|success|learning|progress|result|score)\b/gi
  ];

  const evidenceClaims = [];
  evidencePatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      evidenceClaims.push(cleanMatch);
    });
  });

  // Look for specific outcome measures
  const outcomeMeasures = [
    'test scores',
    'standardized test scores',
    'grade improvement',
    'retention rates',
    'engagement metrics',
    'completion rates',
    'achievement levels',
    'learning pace',
    'personalized feedback',
    'knowledge retention',
    'critical thinking skills',
    'problem-solving abilities'
  ];

  const foundMeasures = outcomeMeasures.filter(measure =>
    content.toLowerCase().includes(measure.toLowerCase())
  );

  return {
    outcomeImprovementClaims: [...new Set(outcomeImprovementClaims)],
    quantitativeMeasures: [...new Set(quantitativeMeasures)],
    aiApplications: [...new Set(identifiedApps)],
    evidenceClaims: [...new Set(evidenceClaims)],
    outcomeMeasures: [...new Set(foundMeasures)],
    totalIndicators: [...new Set(outcomeImprovementClaims)].length + [...new Set(quantitativeMeasures)].length + identifiedApps.length + foundMeasures.length,
    status: ([...new Set(outcomeImprovementClaims)].length >= 3 && [...new Set(quantitativeMeasures)].length >= 2 && identifiedApps.length >= 3) ? 'pass' : 'fail',
    requirement: 'Content includes student outcome improvement verification with evidence'
  };
}

/**
 * Main function to run the student outcome improvement verification on a book file
 * @param {string} bookPath - Path to the book content directory or file
 */
async function runStudentOutcomeAudit(bookPath) {
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

    const result = verifyStudentOutcomeImprovement(content);
    console.log('Student Outcome Improvement Verification Results:');
    console.log(JSON.stringify(result, null, 2));

    // Write results to a file
    const resultsDir = path.join(process.cwd(), 'audit-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsPath = path.join(resultsDir, 'student-outcome-improvement-results.json');
    await fs.writeFile(resultsPath, JSON.stringify(result, null, 2));

    console.log(`Results saved to ${resultsPath}`);

    return result;
  } catch (error) {
    console.error('Error running student outcome improvement verification:', error);
    throw error;
  }
}

// Export functions for testing
module.exports = {
  verifyStudentOutcomeImprovement,
  runStudentOutcomeAudit
};

// If this script is run directly, execute the verification
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node student-outcome-improvement.js <book-path>');
    process.exit(1);
  }

  runStudentOutcomeAudit(args[0])
    .catch(error => {
      console.error('Verification failed:', error);
      process.exit(1);
    });
}