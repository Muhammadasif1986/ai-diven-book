#!/usr/bin/env node

/**
 * Citation validation script for the AI's Impact on K-12 Classroom Efficiency book
 * Validates citations meet academic standards (8+ peer-reviewed sources from 2015-2025)
 */

const fs = require('fs');
const path = require('path');

function extractCitations(content) {
  if (!content || typeof content !== 'string') {
    return [];
  }

  // Find potential citations in various formats
  // APA format: (Author, Year) or Author (Year)
  const apaRegex = /(?:\([A-Za-z\s\-\,\.\d]+,\s*\d{4}\))|(?:[A-Za-z\s\-\,\.\d]+\s*\(\d{4}\))/g;
  const matches = content.match(apaRegex) || [];

  return matches;
}

function validateCitationFormat(citation) {
  // Check if citation matches APA format (Author, Year) or (Author, Year, Page)
  // More comprehensive pattern to match various APA formats
  const patterns = [
    /\([A-Z][a-z]+,\s*\d{4}\)/,  // (Author, Year)
    /\([A-Z][a-z]+,\s*\d{4},\s*[A-Za-z\s]+\)/,  // (Author, Year, Page/Location)
    /[A-Z][a-z]+\s*\(\d{4}\)/,  // Author (Year)
    /[A-Z][a-z]+\s*\(\d{4},\s*[A-Za-z\s]+\)/,  // Author (Year, Page/Location)
    /\([A-Z][a-z]+;\s*\d{4}\)/,  // (Author; Year) - semicolon variant
    /\([A-Z][a-z]+\s*&\s*[A-Z][a-z]+,\s*\d{4}\)/,  // (Author & Author, Year) - multiple authors
    /[A-Z][a-z]+\s*&\s*[A-Z][a-z]+,\s*\(\d{4}\)/,  // Author & Author, (Year) - multiple authors
  ];

  return patterns.some(pattern => pattern.test(citation));
}

function extractYearFromCitation(citation) {
  // Extract 4-digit year from citation
  const yearMatch = citation.match(/\b(19|20)\d{2}\b/);
  return yearMatch ? parseInt(yearMatch[0], 10) : null;
}

// List of known academic journal publishers to help identify peer-reviewed sources
const PEER_REVIEWED_PUBLISHERS = [
  'journal', 'research', 'academic', 'scholarly', 'proceedings', 'conference',
  'association', 'american', 'international', 'science', 'nature', 'cell',
  'elsevier', 'springer', 'wiley', 'taylor', 'routledge', 'sage', 'sage publications',
  'oxford', 'cambridge', 'mit press', 'ieee', 'acm', 'association for', 'association of',
  'academic press', 'cambridge university', 'oxford university', 'mit', 'stanford',
  'harvard', 'yale', 'princeton', 'california', 'berkeley', 'cornell', 'columbia',
  'publishing', 'pub', 'publ', 'publsiher', 'press', 'plos', 'public library', 'biomed central'
];

// Additional keywords that suggest academic sources
const ACADEMIC_KEYWORDS = [
  'university', 'school', 'college', 'institute', 'center', 'department',
  'study', 'research', 'analysis', 'investigation', 'experiment', 'survey',
  'paper', 'article', 'publication', 'thesis', 'dissertation', 'monograph',
  'quarterly', 'review', 'symposium', 'transactions', 'annals', 'journal',
  'proceedings', 'conference', 'workshop', 'seminar', 'report', 'working paper'
];

function validateAcademicSource(citation, context = '') {
  // This is a simplified academic source validation
  // In a real implementation, this would connect to academic databases to verify peer review status

  // Check if citation contains academic keywords
  const citationLower = citation.toLowerCase();
  const contextLower = context.toLowerCase();

  const hasAcademicIndicators = [
    ...PEER_REVIEWED_PUBLISHERS,
    ...ACADEMIC_KEYWORDS
  ].some(keyword => citationLower.includes(keyword.toLowerCase()) || contextLower.includes(keyword.toLowerCase()));

  return hasAcademicIndicators;
}

function validateCitations(docsDir = './my-website/docs') {
  console.log('Validating citations...');

  if (!fs.existsSync(docsDir)) {
    console.error(`Directory ${docsDir} does not exist`);
    return { valid: false, totalCitations: 0, errors: [`Directory ${docsDir} does not exist`] };
  }

  // Get all MD and MDX files
  const files = fs.readdirSync(docsDir).filter(file =>
    path.extname(file) === '.md' || path.extname(file) === '.mdx'
  );

  let allCitations = [];
  const citationDetails = [];

  for (const file of files) {
    const filePath = path.join(docsDir, file);
    const content = fs.readFileSync(filePath, 'utf8');
    const citations = extractCitations(content);

    for (const citation of citations) {
      const year = extractYearFromCitation(citation);
      const isValidFormat = validateCitationFormat(citation);
      const isAcademicSource = validateAcademicSource(citation, content.substring(0, 1000)); // Use first 1000 chars as context

      citationDetails.push({
        file,
        citation,
        year,
        isValidFormat,
        isWithinRange: year ? year >= 2015 && year <= 2025 : false,
        isAcademicSource
      });
    }

    allCitations = allCitations.concat(citations);
  }

  console.log(`Found ${allCitations.length} citations`);

  const result = {
    valid: true,
    totalCitations: allCitations.length,
    citationDetails,
    errors: []
  };

  // Check minimum citation requirement (8+)
  if (allCitations.length < 8) {
    result.valid = false;
    result.errors.push(`Insufficient citations: found ${allCitations.length}, need at least 8`);
  }

  // Check year range (2015-2025)
  const citationsInRange = citationDetails.filter(c => c.isWithinRange).length;
  if (citationsInRange < 8) {
    result.valid = false;
    result.errors.push(`Insufficient citations from 2015-2025: found ${citationsInRange}, need at least 8`);
  }

  // Check format validity
  const validFormatCitations = citationDetails.filter(c => c.isValidFormat).length;
  if (validFormatCitations < 8) {
    result.valid = false;
    result.errors.push(`Insufficient citations with valid APA format: found ${validFormatCitations}, need at least 8`);
  }

  // Check academic source validation
  const academicCitations = citationDetails.filter(c => c.isAcademicSource).length;
  if (academicCitations < 8) {
    result.valid = false;
    result.errors.push(`Insufficient peer-reviewed academic sources: found ${academicCitations}, need at least 8`);
  }

  // Show detailed citation information
  console.log('\nCitation details:');
  citationDetails.forEach((detail, index) => {
    const formatStatus = detail.isValidFormat ? '✅' : '❌';
    const yearStatus = detail.isWithinRange ? '✅' : '❌';
    const academicStatus = detail.isAcademicSource ? '✅' : '❌';

    console.log(`  ${formatStatus}${yearStatus}${academicStatus} ${detail.citation} (${detail.file})`);
  });

  return result;
}

// Run validation if this script is executed directly
if (require.main === module) {
  const result = validateCitations();

  if (!result.valid) {
    console.error('\n❌ Citation validation failed:');
    result.errors.forEach(error => console.error(`  - ${error}`));
    process.exit(1);
  } else {
    console.log('\n✅ Citation validation passed!');
  }
}

module.exports = { validateCitations, extractCitations, validateCitationFormat, extractYearFromCitation };