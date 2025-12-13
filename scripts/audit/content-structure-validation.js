/**
 * Script to validate content structure for K-12 focus
 * This script analyzes book content structure to ensure it focuses specifically on K-12 applications
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Validates content structure for K-12 focus
 * @param {string} content - The book content to analyze
 * @returns {object} - Results containing structure validation
 */
function validateK12Focus(content) {
  // Count occurrences of K-12 related terms
  const k12Terms = [
    'k-12', 'k12', 'kindergarten', 'elementary', 'middle school', 'high school',
    'grades k-12', 'grades k12', 'primary education', 'secondary education',
    'k through 12', 'k-12 education', 'k12 education', 'grade level', 'classroom'
  ];

  const k12TermCount = k12Terms.reduce((count, term) => {
    const matches = content.toLowerCase().match(new RegExp(term, 'g')) || [];
    return count + matches.length;
  }, 0);

  // Check for K-12 specific sections
  const k12SectionPatterns = [
    /k-12.*application/gi,
    /k12.*application/gi,
    /(elementary|middle school|high school).*ai/gi,
    /classroom.*ai/gi,
    /grade.*ai/gi
  ];

  const k12Sections = [];
  k12SectionPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    matches.forEach(match => k12Sections.push(match));
  });

  // Check for structure elements (headings, sections)
  const headingPatterns = [
    /^#+\s+(.*)$/gm,  // Markdown headings
    /<h[1-6][^>]*>(.*?)<\/h[1-6]>/gi  // HTML headings if present
  ];

  let headings = [];
  headingPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    headings = [...headings, ...matches];
  });

  // Count K-12 related headings
  const k12Headings = headings.filter(heading =>
    k12Terms.some(term => heading.toLowerCase().includes(term))
  );

  // Check for proper content organization
  const hasIntroduction = /introduction|overview|what is ai/gi.test(content);
  const hasApplications = /application|use case|implementation|tool/gi.test(content);
  const hasEvidence = /evidence|study|research|data|result|finding/gi.test(content);
  const hasConclusion = /conclusion|summary|future|recommendation/gi.test(content);

  // Check for educator-focused content
  const educatorTerms = [
    'teacher', 'educator', 'instructor', 'principal', 'administrator',
    'student', 'learning', 'curriculum', 'pedagogy', 'instruction'
  ];

  const educatorTermCount = educatorTerms.reduce((count, term) => {
    const matches = content.toLowerCase().match(new RegExp(term, 'g')) || [];
    return count + matches.length;
  }, 0);

  return {
    k12TermCount,
    k12Sections: [...new Set(k12Sections)],
    k12Headings: k12Headings.length,
    contentStructure: {
      hasIntroduction,
      hasApplications,
      hasEvidence,
      hasConclusion
    },
    educatorFocus: educatorTermCount > 10, // Arbitrary threshold
    totalK12Indicators: k12TermCount + k12Headings.length + (hasApplications ? 1 : 0) + (hasEvidence ? 1 : 0),
    status: (k12TermCount >= 5 && educatorTermCount >= 10 && hasApplications && hasEvidence) ? 'pass' : 'fail',
    requirement: 'Content structure specifically focused on K-12 applications'
  };
}

/**
 * Main function to run the content structure validation on a book file
 * @param {string} bookPath - Path to the book content directory or file
 */
async function runContentStructureValidation(bookPath) {
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

    const result = validateK12Focus(content);
    console.log('Content Structure Validation Results:');
    console.log(JSON.stringify(result, null, 2));

    // Write results to a file
    const resultsDir = path.join(process.cwd(), 'audit-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsPath = path.join(resultsDir, 'content-structure-results.json');
    await fs.writeFile(resultsPath, JSON.stringify(result, null, 2));

    console.log(`Results saved to ${resultsPath}`);

    return result;
  } catch (error) {
    console.error('Error running content structure validation:', error);
    throw error;
  }
}

// Export functions for testing
module.exports = {
  validateK12Focus,
  runContentStructureValidation
};

// If this script is run directly, execute the validation
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node content-structure-validation.js <book-path>');
    process.exit(1);
  }

  runContentStructureValidation(args[0])
    .catch(error => {
      console.error('Validation failed:', error);
      process.exit(1);
    });
}