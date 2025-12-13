/**
 * Unit test for AI application identification
 * Tests that the system can identify specific AI applications with evidence in the content
 */

const fs = require('fs');
const path = require('path');

// Mock function to simulate AI application identification
function identifyAIApplications(content) {
  if (!content || typeof content !== 'string') {
    return {
      count: 0,
      applications: [],
      evidence: []
    };
  }

  // Keywords that indicate AI applications in education
  const aiKeywords = [
    'artificial intelligence',
    'AI-powered',
    'machine learning',
    'automated',
    'intelligent tutoring',
    'adaptive learning',
    'personalized learning',
    'smart classroom',
    'educational AI',
    'AI assistant',
    'virtual tutor',
    'automated grading',
    'intelligent assessment',
    'natural language processing',
    'computer vision',
    'neural network',
    'deep learning'
  ];

  const applicationPatterns = [
    /AI(?:-| |powered)?assisted/,
    /automated .* grading/,
    /intelligent .* system/,
    /adaptive .* platform/,
    /personalized .* learning/,
    /AI .* tool/,
    /smart .* technology/,
    /virtual .* assistant/,
    /intelligent .* tutor/,
    /automated .* feedback/
  ];

  const evidencePhrases = [
    'evidence shows',
    'research indicates',
    'studies demonstrate',
    'results show',
    'data indicates',
    'reported improvement',
    'measurable gains',
    'effectiveness',
    'efficiency',
    'time saved',
    'performance improved',
    'engagement increased',
    'accuracy improved',
    'learning outcomes',
    'student achievement',
    'academic performance'
  ];

  // Find matches in content
  const applications = [];
  const evidences = [];

  for (const keyword of aiKeywords) {
    if (content.toLowerCase().includes(keyword.toLowerCase())) {
      applications.push(keyword);
    }
  }

  for (const pattern of applicationPatterns) {
    const matches = content.match(new RegExp(pattern, 'gi'));
    if (matches) {
      applications.push(...matches);
    }
  }

  for (const evidencePhrase of evidencePhrases) {
    if (content.toLowerCase().includes(evidencePhrase.toLowerCase())) {
      evidences.push(evidencePhrase);
    }
  }

  // Remove duplicates
  const uniqueApplications = [...new Set(applications)];
  const uniqueEvidences = [...new Set(evidences)];

  return {
    count: uniqueApplications.length,
    applications: uniqueApplications,
    evidence: uniqueEvidences,
    hasEnoughApplications: uniqueApplications.length >= 3,
    hasEvidence: uniqueEvidences.length > 0
  };
}

describe('AI Application Identification', () => {
  test('should return empty for empty content', () => {
    const result = identifyAIApplications('');
    expect(result.count).toBe(0);
    expect(result.applications).toEqual([]);
    expect(result.evidence).toEqual([]);
    expect(result.hasEnoughApplications).toBe(false);
  });

  test('should identify basic AI application terms', () => {
    const content = 'This discusses artificial intelligence and machine learning in education.';
    const result = identifyAIApplications(content);
    expect(result.count).toBeGreaterThan(0);
    expect(result.hasEnoughApplications).toBe(false); // Only 2 terms
  });

  test('should recognize 3+ AI applications to meet requirements', () => {
    const content = `
      Artificial intelligence powers intelligent tutoring systems that adapt to student needs.
      Machine learning algorithms analyze student performance data.
      Natural language processing enables automated essay scoring.
      Studies demonstrate significant improvements in student engagement.
    `;

    const result = identifyAIApplications(content);
    expect(result.count).toBeGreaterThanOrEqual(3);
    expect(result.hasEnoughApplications).toBe(true);
    expect(result.hasEvidence).toBe(true);
  });

  test('should detect evidence of effectiveness', () => {
    const content = `
      Research indicates that adaptive learning systems improve student outcomes.
      Evidence shows measurable gains in math performance.
      Data indicates higher engagement rates with personalized content.
    `;

    const result = identifyAIApplications(content);
    expect(result.evidence.length).toBeGreaterThan(0);
    expect(result.hasEvidence).toBe(true);
  });

  test('should match application patterns', () => {
    const content = `
      The AI-assisted learning platform provides personalized recommendations.
      Automated grading systems save teachers time.
      Intelligent assessment tools provide instant feedback.
    `;

    const result = identifyAIApplications(content);
    expect(result.count).toBeGreaterThanOrEqual(3);
    expect(result.hasEnoughApplications).toBe(true);
  });
});