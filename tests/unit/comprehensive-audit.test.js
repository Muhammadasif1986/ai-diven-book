const { runComprehensiveAudit, determineOverallStatus } = require('../../scripts/audit/comprehensive-audit');

// Mock data for testing
const mockBookContent = `
# AI Applications in K-12 Education

This book discusses several AI applications in K-12 education:

## Application 1: Intelligent Tutoring Systems
Intelligent tutoring systems provide personalized learning experiences. Studies show 25% improvement in student outcomes.

## Application 2: Automated Grading
Automated grading systems can reduce teacher workload by 30% while maintaining assessment quality.

## Application 3: Learning Analytics
Learning analytics help educators identify struggling students early and provide targeted interventions, resulting in 18% improvement in retention.

## Cost Analysis
Implementing AI tools in K-12 education requires an initial investment of $50,000 for software licenses and training but schools report saving approximately $20,000 annually.

Citations:
- Smith, J. (2023). AI in Education. Educational Tech Journal.
- Johnson, A. (2022). Learning Analytics. Journal of Educational Data Mining.
- Williams, K. (2024). Teacher Workload Reduction. Educational Efficiency Quarterly.
`;

describe('Comprehensive Audit Tests', () => {
  test('should determine overall status as pass when all components pass', () => {
    const statuses = ['pass', 'pass', 'pass', 'pass', 'pass'];
    const result = determineOverallStatus(statuses);
    expect(result).toBe('pass');
  });

  test('should determine overall status as fail when any component fails', () => {
    const statuses = ['pass', 'fail', 'pass', 'pass', 'pass'];
    const result = determineOverallStatus(statuses);
    expect(result).toBe('fail');
  });

  test('should determine overall status as warning for mixed results', () => {
    const statuses = ['pass', 'warning', 'pass', 'pass', 'pass'];
    const result = determineOverallStatus(statuses);
    expect(result).toBe('warning');
  });

  test('should run comprehensive audit and return structured results', async () => {
    // Mock the file system operations for testing
    jest.spyOn(require('fs').promises, 'readdir').mockResolvedValue(['intro.mdx']);
    jest.spyOn(require('fs').promises, 'readFile').mockResolvedValue(mockBookContent);
    jest.spyOn(require('fs').promises, 'mkdir').mockResolvedValue(undefined);
    jest.spyOn(require('fs').promises, 'writeFile').mockResolvedValue(undefined);
    jest.spyOn(require('fs'), 'statSync').mockReturnValue({ isDirectory: () => true });

    const result = await runComprehensiveAudit('mock/path');

    expect(result).toHaveProperty('timestamp');
    expect(result).toHaveProperty('bookPath');
    expect(result).toHaveProperty('aiApplications');
    expect(result).toHaveProperty('roiClarity');
    expect(result).toHaveProperty('k12Focus');
    expect(result).toHaveProperty('teacherWorkloadReduction');
    expect(result).toHaveProperty('studentOutcomeImprovement');
    expect(result).toHaveProperty('overallStatus');
    expect(result).toHaveProperty('summary');

    // Verify that each audit component returned appropriate results
    expect(result.aiApplications).toHaveProperty('totalApplications');
    expect(result.roiClarity).toHaveProperty('totalElements');
    expect(result.k12Focus).toHaveProperty('totalK12Indicators');
    expect(result.teacherWorkloadReduction).toHaveProperty('totalIndicators');
    expect(result.studentOutcomeImprovement).toHaveProperty('totalIndicators');
  });

  test('should handle file system errors gracefully', async () => {
    // Mock file system error
    jest.spyOn(require('fs'), 'statSync').mockImplementation(() => {
      throw new Error('File not found');
    });

    await expect(runComprehensiveAudit('invalid/path')).rejects.toThrow('File not found');
  });
});