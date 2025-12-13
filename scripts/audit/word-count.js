#!/usr/bin/env node

/**
 * Word count verification script for the AI's Impact on K-12 Classroom Efficiency book
 * Checks that content meets the required word count (3,000-5,000 words)
 */

const fs = require('fs');
const path = require('path');

function countWordsInFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return countWords(content);
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error.message);
    return 0;
  }
}

function countWords(content) {
  if (!content || typeof content !== 'string') {
    return 0;
  }

  // Remove extra whitespace and split by spaces
  const words = content.trim().split(/\s+/).filter(word => word.length > 0);
  return words.length;
}

function getMdxFiles(dir) {
  const files = [];
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      files.push(...getMdxFiles(fullPath));
    } else if (path.extname(fullPath) === '.mdx' || path.extname(fullPath) === '.md') {
      files.push(fullPath);
    }
  }

  return files;
}

function verifyWordCount(docsDir = './my-website/docs') {
  console.log('Verifying word count...');

  if (!fs.existsSync(docsDir)) {
    console.error(`Directory ${docsDir} does not exist`);
    return { valid: false, totalWords: 0, errors: [`Directory ${docsDir} does not exist`] };
  }

  const mdxFiles = getMdxFiles(docsDir);
  let totalWords = 0;
  const fileCounts = [];

  for (const file of mdxFiles) {
    const wordCount = countWordsInFile(file);
    totalWords += wordCount;
    fileCounts.push({ file, wordCount });
    console.log(`${file}: ${wordCount} words`);
  }

  console.log(`\nTotal word count: ${totalWords}`);

  const minWords = 3000;
  const maxWords = 5000;

  const result = {
    valid: totalWords >= minWords && totalWords <= maxWords,
    totalWords,
    minRequired: minWords,
    maxAllowed: maxWords,
    fileCounts,
    errors: []
  };

  if (totalWords < minWords) {
    result.errors.push(`Word count too low: ${totalWords} words, minimum required is ${minWords}`);
  } else if (totalWords > maxWords) {
    result.errors.push(`Word count too high: ${totalWords} words, maximum allowed is ${maxWords}`);
  } else {
    console.log(`✅ Word count is within the required range (${minWords}-${maxWords} words)`);
  }

  return result;
}

// Run verification if this script is executed directly
if (require.main === module) {
  const result = verifyWordCount();

  if (!result.valid) {
    console.error('❌ Word count verification failed:');
    result.errors.forEach(error => console.error(`  - ${error}`));
    process.exit(1);
  } else {
    console.log('✅ Word count verification passed!');
  }
}

module.exports = { verifyWordCount, countWords, countWordsInFile };