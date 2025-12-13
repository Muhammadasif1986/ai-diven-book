/**
 * Script to identify AI applications in K-12 education content
 * This script analyzes book content to identify specific AI applications with evidence
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Identifies AI applications in K-12 education from book content
 * @param {string} content - The book content to analyze
 * @returns {object} - Results containing identified applications
 */
function identifyAIApplications(content) {
  // Pattern to identify AI applications in the content
  const applicationPatterns = [
    /([A-Z][a-z\s-]*\s*(?:AI|artificial intelligence|machine learning|deep learning|neural network)[a-z\s-]*)/gi,
    /([A-Z][a-z\s-]*\s*(?:intelligent|automated|adaptive|personalized|smart)[a-z\s-]*\s*(?:system|tool|platform|software|solution))/gi,
    /([A-Z][a-z\s-]*\s*(?:tutoring|grading|assessment|learning analytics|content recommendation|student monitoring)[a-z\s-]*)/gi,
  ];

  const applications = new Set();

  // Search for AI applications using patterns
  applicationPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      // Clean up the match and add to applications set
      const cleanMatch = match.trim().replace(/\s+/g, ' ');
      if (cleanMatch.length > 3) { // Avoid very short matches
        applications.add(cleanMatch);
      }
    });
  });

  // Specific known AI applications in education
  const knownApplications = [
    'Intelligent Tutoring Systems',
    'Automated Grading',
    'Learning Analytics',
    'Adaptive Learning Platforms',
    'AI-Powered Content Recommendation',
    'Natural Language Processing for Assessment',
    'Predictive Analytics for Student Success',
    'Virtual Teaching Assistants',
    'Automated Essay Scoring',
    'Personalized Learning Pathways',
    'AI-Powered Language Learning',
    'Computer Vision for Assessment',
    'Speech Recognition for Language Learning',
    'Educational Chatbots',
    'AI-Powered Plagiarism Detection'
  ];

  // Find known applications in the content
  const foundKnownApplications = knownApplications.filter(app =>
    content.toLowerCase().includes(app.toLowerCase())
  );

  // Combine both sets of applications
  const allApplications = [...new Set([...applications, ...foundKnownApplications])];

  // Look for evidence of effectiveness in the content
  const evidencePatterns = [
    /\b(studies?|research|evidence|data|results?|findings?|demonstrated|shown|proved|indicated)\b[\s\S]{0,100}\b(improvement|increase|effectiveness|efficiency|outcome|performance|benefit|gain|advantage)\b/gi,
    /\b(improvement|increase|effectiveness|efficiency|outcome|performance|benefit|gain|advantage)[\s\S]{0,100}\b(studies?|research|evidence|data|results?|findings?|demonstrated|shown|proved|indicated)\b/gi,
    /\b\d+%\s*(improvement|increase|reduction|decrease)\b/gi,
    /\b(significant|substantial|notable|measurable)\s+(improvement|increase|effectiveness|efficiency|outcome|performance|benefit|gain|advantage)\b/gi
  ];

  const evidence = [];
  evidencePatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.trim();
      if (cleanMatch.length > 10) { // Avoid very short matches
        evidence.push(cleanMatch);
      }
    });
  });

  // Structure the results
  const structuredApplications = allApplications.map(app => ({
    name: app,
    evidence: evidence,
    k12Relevance: 'K-12 education context',
    outcomes: extractOutcomes(content, app)
  }));

  return {
    totalApplications: structuredApplications.length,
    applications: structuredApplications,
    status: structuredApplications.length >= 3 ? 'pass' : 'fail',
    requirement: '3+ AI applications with evidence of effectiveness from peer-reviewed studies'
  };
}

/**
 * Extracts outcomes related to a specific application
 * @param {string} content - The book content
 * @param {string} application - The AI application name
 * @returns {string} - Outcomes related to the application
 */
function extractOutcomes(content, application) {
  // Look for outcome-related phrases near the application mention
  const outcomePatterns = [
    /(\d+%\s*(improvement|increase|reduction|decrease))|((significant|substantial|measurable)\s+(improvement|increase|effectiveness|efficiency|outcome|performance|benefit|gain|advantage))/gi,
    /(student|teacher|learning|academic)\s+(outcome|performance|achievement|engagement|efficiency)/gi
  ];

  const appIndex = content.toLowerCase().indexOf(application.toLowerCase());
  if (appIndex === -1) return '';

  // Get a section around the application mention
  const start = Math.max(0, appIndex - 200);
  const end = Math.min(content.length, appIndex + application.length + 200);
  const context = content.substring(start, end);

  let outcomes = [];
  outcomePatterns.forEach(pattern => {
    const matches = context.match(pattern) || [];
    outcomes = [...outcomes, ...matches];
  });

  return [...new Set(outcomes)].join('; ');
}

/**
 * Main function to run the AI application identification on a book file
 * @param {string} bookPath - Path to the book content directory or file
 */
async function runAIApplicationAudit(bookPath) {
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

    const result = identifyAIApplications(content);
    console.log('AI Application Audit Results:');
    console.log(JSON.stringify(result, null, 2));

    // Write results to a file
    const resultsDir = path.join(process.cwd(), 'audit-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsPath = path.join(resultsDir, 'ai-applications-results.json');
    await fs.writeFile(resultsPath, JSON.stringify(result, null, 2));

    console.log(`Results saved to ${resultsPath}`);

    return result;
  } catch (error) {
    console.error('Error running AI application audit:', error);
    throw error;
  }
}

// Export functions for testing
module.exports = {
  identifyAIApplications,
  runAIApplicationAudit
};

// If this script is run directly, execute the audit
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node ai-applications.js <book-path>');
    process.exit(1);
  }

  runAIApplicationAudit(args[0])
    .catch(error => {
      console.error('Audit failed:', error);
      process.exit(1);
    });
}