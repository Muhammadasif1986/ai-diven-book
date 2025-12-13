const { verifyROIClarity } = require('../../scripts/audit/roi-verification');

// Mock data for testing
const mockBookContentWithROI = `
# ROI of AI Implementation in K-12 Classrooms

## Cost Analysis
Implementing AI tools in K-12 education requires an initial investment of $50,000 for software licenses and training.

## Benefits
- Reduced teacher workload by 30%
- Improved student outcomes by 15%
- Decreased administrative tasks by 25%
- Enhanced personalized learning leading to better retention

## Financial Impact
Schools report saving approximately $20,000 annually in reduced administrative costs after implementing AI tools.

## Quantitative Measures
- 25% reduction in time spent on grading
- 18% improvement in standardized test scores
- 40% decrease in teacher turnover (retention benefit)
`;

const mockBookContentWithoutROI = `
# AI Applications in K-12 Education

This book discusses several AI applications in K-12 education:

## Application 1: Intelligent Tutoring Systems
Intelligent tutoring systems provide personalized learning experiences.

## Application 2: Automated Grading
Automated grading systems can reduce teacher workload.
`;

describe('ROI Clarity Verification Tests', () => {
  test('should identify ROI elements when present in content', () => {
    const result = verifyROIClarity(mockBookContentWithROI);

    expect(result.roiElements).toBeDefined();
    expect(Array.isArray(result.roiElements)).toBe(true);
    expect(result.roiElements.length).toBeGreaterThan(0);

    // Check for specific ROI elements
    const elementTexts = result.roiElements.map(el => el.text.toLowerCase());
    expect(elementTexts.some(text => text.includes('cost'))).toBe(true);
    expect(elementTexts.some(text => text.includes('benefit'))).toBe(true);
    expect(elementTexts.some(text => text.includes('savings'))).toBe(true);
    expect(elementTexts.some(text => text.includes('investment'))).toBe(true);
  });

  test('should return fail status when ROI elements are insufficient', () => {
    const result = verifyROIClarity(mockBookContentWithoutROI);

    expect(result.status).toBe('fail');
    expect(result.roiElements.length).toBeLessThan(3); // Expect fewer elements
  });

  test('should identify quantitative measures in ROI', () => {
    const result = verifyROIClarity(mockBookContentWithROI);

    expect(result.quantitativeMeasures).toBeDefined();
    expect(Array.isArray(result.quantitativeMeasures)).toBe(true);
    expect(result.quantitativeMeasures.length).toBeGreaterThan(0);

    // Check for specific quantitative measures
    const measures = result.quantitativeMeasures;
    expect(measures.some(measure => measure.includes('30%') && measure.includes('teacher'))).toBe(true);
    expect(measures.some(measure => measure.includes('15%') && measure.includes('student'))).toBe(true);
    expect(measures.some(measure => measure.includes('25%') && measure.includes('administrative'))).toBe(true);
  });

  test('should identify financial impact statements', () => {
    const result = verifyROIClarity(mockBookContentWithROI);

    expect(result.financialImpact).toBeDefined();
    expect(Array.isArray(result.financialImpact)).toBe(true);
    expect(result.financialImpact.length).toBeGreaterThan(0);

    const impactTexts = result.financialImpact.map(imp => imp.toLowerCase());
    expect(impactTexts.some(text => text.includes('$20,000') && text.includes('saving'))).toBe(true);
  });

  test('should return proper structure', () => {
    const result = verifyROIClarity(mockBookContentWithROI);

    expect(result).toHaveProperty('roiElements');
    expect(result).toHaveProperty('quantitativeMeasures');
    expect(result).toHaveProperty('financialImpact');
    expect(result).toHaveProperty('totalElements');
    expect(result).toHaveProperty('status');
    expect(result).toHaveProperty('requirement');

    expect(Array.isArray(result.roiElements)).toBe(true);
    expect(Array.isArray(result.quantitativeMeasures)).toBe(true);
    expect(Array.isArray(result.financialImpact)).toBe(true);
    expect(typeof result.totalElements).toBe('number');
    expect(typeof result.status).toBe('string');
    expect(typeof result.requirement).toBe('string');
  });
});