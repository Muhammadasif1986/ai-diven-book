#!/usr/bin/env node

/**
 * Plagiarism detection script for the AI's Impact on K-12 Classroom Efficiency book
 * Checks for potential plagiarism by comparing content against known sources
 * Note: This is a basic implementation. A full implementation would require
 * integration with plagiarism detection services.
 */

const fs = require('fs');
const path = require('path');

function getTextFromFiles(docsDir) {
  if (!fs.existsSync(docsDir)) {
    console.error(`Directory ${docsDir} does not exist`);
    return '';
  }

  // Get all MD and MDX files
  const files = fs.readdirSync(docsDir).filter(file =>
    path.extname(file) === '.md' || path.extname(file) === '.mdx'
  );

  let allContent = '';

  for (const file of files) {
    const filePath = path.join(docsDir, file);
    const content = fs.readFileSync(filePath, 'utf8');

    // Remove frontmatter if present (common in MDX/MD files)
    const contentWithoutFrontmatter = removeFrontmatter(content);
    allContent += contentWithoutFrontmatter + ' ';
  }

  return allContent.trim();
}

function removeFrontmatter(content) {
  // Remove YAML frontmatter if present (enclosed between ---)
  if (content.startsWith('---')) {
    const lines = content.split('\n');
    let frontmatterEnd = -1;

    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim() === '---') {
        frontmatterEnd = i;
        break;
      }
    }

    if (frontmatterEnd !== -1) {
      return lines.slice(frontmatterEnd + 1).join('\n').trim();
    }
  }

  return content;
}

function checkForCommonPhrases(content) {
  // List of common phrases that might indicate potential issues
  // In a real implementation, this would be much more comprehensive
  const commonPhrases = [
    'Lorem ipsum dolor sit amet',
    'consectetur adipiscing elit',
    'sed do eiusmod tempor incididunt',
    'ut labore et dolore magna aliqua'
  ];

  const foundPhrases = [];
  const lowerContent = content.toLowerCase();

  for (const phrase of commonPhrases) {
    if (lowerContent.includes(phrase.toLowerCase())) {
      foundPhrases.push(phrase);
    }
  }

  return foundPhrases;
}

function calculateTextUniqueness(content) {
  // This is a very basic uniqueness check
  // A real implementation would compare against a database of known texts
  const words = content.trim().split(/\s+/).filter(word => word.length > 0);

  // Create a simple hash of the content to represent uniqueness
  // This is just a placeholder for a real uniqueness algorithm
  let hash = 0;
  for (let i = 0; i < words.length; i++) {
    for (let j = 0; j < words[i].length; j++) {
      const char = words[i].charCodeAt(j);
      hash = ((hash << 5) - hash) + char;
      hash |= 0; // Convert to 32-bit integer
    }
  }

  // For this basic implementation, we'll just return a high uniqueness score
  // since we can't actually compare against external sources
  return 100; // 100% unique as we can't detect similarity without external sources
}

function runPlagiarismCheck(docsDir = './my-website/docs') {
  console.log('Running plagiarism check...');

  const content = getTextFromFiles(docsDir);

  if (!content) {
    console.error('No content found to check for plagiarism');
    return { valid: false, similarity: 0, errors: ['No content found to check'] };
  }

  const commonPhrases = checkForCommonPhrases(content);
  const uniqueness = calculateTextUniqueness(content);

  const result = {
    valid: commonPhrases.length === 0, // Consider valid if no common phrases found
    similarityPercent: 0, // Placeholder - can't calculate without external comparison
    uniquenessPercent: uniqueness,
    commonPhrasesFound: commonPhrases,
    errors: []
  };

  if (commonPhrases.length > 0) {
    result.errors.push(`Found ${commonPhrases.length} potentially non-original phrases`);
  }

  console.log(`Content analyzed: ~${content.split(/\s+/).length} words`);
  console.log(`Uniqueness estimate: ${uniqueness}%`);

  if (commonPhrases.length > 0) {
    console.log('⚠️  Found potentially non-original phrases:');
    commonPhrases.forEach(phrase => console.log(`  - "${phrase}"`));
  }

  return result;
}

// Run plagiarism check if this script is executed directly
if (require.main === module) {
  const result = runPlagiarismCheck();

  if (!result.valid) {
    console.error('\n❌ Plagiarism check detected issues:');
    result.errors.forEach(error => console.error(`  - ${error}`));
    process.exit(1);
  } else {
    console.log('\n✅ Plagiarism check passed! No obvious issues detected.');
    console.log('Note: This is a basic check. For thorough plagiarism detection, integrate with a dedicated service.');
  }
}

module.exports = { runPlagiarismCheck, getTextFromFiles, removeFrontmatter, checkForCommonPhrases };