#!/usr/bin/env node

/**
 * Readability analysis script for the AI's Impact on K-12 Classroom Efficiency book
 * Calculates Flesch-Kincaid Grade Level to ensure content is appropriate for education administrators (Grade 10-12)
 */

const fs = require('fs');
const path = require('path');

// Helper functions for readability calculation
function countSentences(text) {
  // Count sentences by looking for sentence-ending punctuation
  const sentences = text.match(/[.!?]+/g);
  return sentences ? sentences.length : 0;
}

function countWords(text) {
  // Split text by whitespace and filter out empty strings
  const words = text.trim().split(/\s+/).filter(word => word.length > 0);
  return words.length;
}

function countSyllables(word) {
  // Count syllables in a word using a basic algorithm
  word = word.toLowerCase();

  // Special cases
  if (word.length <= 3) return 1;
  if (word.endsWith('e')) word = word.slice(0, -1);

  // Count vowel groups
  const vowels = word.match(/[aeiouy]+/g);
  let count = vowels ? vowels.length : 1;

  // Adjust for silent 'e' at the end
  if (word.endsWith('e') && count > 1) count--;

  // Ensure at least 1 syllable
  return Math.max(1, count);
}

function countTotalSyllables(text) {
  const words = text.trim().split(/\s+/).filter(word => word.length > 0);
  let total = 0;

  for (const word of words) {
    // Remove punctuation attached to the word
    const cleanWord = word.replace(/[^\w\s]|_/g, '');
    total += countSyllables(cleanWord);
  }

  return total;
}

function calculateFleschKincaidGradeLevel(text) {
  const sentences = countSentences(text);
  const words = countWords(text);
  const syllables = countTotalSyllables(text);

  // Avoid division by zero
  if (sentences === 0 || words === 0) {
    return 0;
  }

  // Calculate Flesch-Kincaid Grade Level
  // Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
  const avgWordsPerSentence = words / sentences;
  const avgSyllablesPerWord = syllables / words;

  const gradeLevel = (0.39 * avgWordsPerSentence) + (11.8 * avgSyllablesPerWord) - 15.59;

  return Math.round(gradeLevel * 10) / 10; // Round to 1 decimal place
}

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

function runReadabilityAnalysis(docsDir = './my-website/docs') {
  console.log('Running readability analysis...');

  const content = getTextFromFiles(docsDir);

  if (!content) {
    console.error('No content found to analyze for readability');
    return {
      valid: false,
      gradeLevel: 0,
      errors: ['No content found to analyze']
    };
  }

  const gradeLevel = calculateFleschKincaidGradeLevel(content);
  const sentences = countSentences(content);
  const words = countWords(content);
  const syllables = countTotalSyllables(content);

  const result = {
    valid: gradeLevel >= 10 && gradeLevel <= 12, // Target grade level is 10-12
    gradeLevel,
    sentences,
    words,
    syllables,
    errors: []
  };

  if (!result.valid) {
    result.errors.push(
      `Readability score (${gradeLevel}) is outside target range (10-12). ` +
      `Content is appropriate for grade level ${gradeLevel}.`
    );
  }

  console.log(`\nReadability Analysis Results:`);
  console.log(`- Grade Level: ${gradeLevel}`);
  console.log(`- Total Words: ${words}`);
  console.log(`- Total Sentences: ${sentences}`);
  console.log(`- Total Syllables: ${syllables}`);
  console.log(`- Average Words per Sentence: ${(words / Math.max(1, sentences)).toFixed(1)}`);
  console.log(`- Average Syllables per Word: ${(syllables / Math.max(1, words)).toFixed(1)}`);

  return result;
}

// Run readability analysis if this script is executed directly
if (require.main === module) {
  const result = runReadabilityAnalysis();

  if (!result.valid) {
    console.error('\n❌ Readability analysis failed:');
    result.errors.forEach(error => console.error(`  - ${error}`));
    console.log(`\nRecommendation: Adjust content complexity to target grades 10-12 (currently at grade ${result.gradeLevel})`);
    process.exit(1);
  } else {
    console.log('\n✅ Readability analysis passed!');
    console.log(`Content is at grade level ${result.gradeLevel}, which is within the target range (10-12).`);
  }
}

module.exports = {
  runReadabilityAnalysis,
  calculateFleschKincaidGradeLevel,
  countSentences,
  countWords,
  countSyllables,
  countTotalSyllables,
  getTextFromFiles,
  removeFrontmatter
};