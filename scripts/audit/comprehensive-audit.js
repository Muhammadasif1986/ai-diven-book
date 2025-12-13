/**
 * Comprehensive audit script that integrates all user story components
 * This script runs all audit checks in sequence and produces a combined report
 */

const fs = require('fs').promises;
const path = require('path');
const { identifyAIApplications } = require('./ai-applications');
const { verifyROIClarity } = require('./roi-verification');
const { validateK12Focus } = require('./content-structure-validation');
const { verifyTeacherWorkloadReduction } = require('./teacher-workload-reduction');
const { verifyStudentOutcomeImprovement } = require('./student-outcome-improvement');

/**
 * Runs a comprehensive audit combining all user story components
 * @param {string} bookPath - Path to the book content directory or file
 * @returns {object} - Combined audit results
 */
async function runComprehensiveAudit(bookPath) {
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

    console.log('Starting comprehensive audit...');

    // Run all audit components
    const aiApplicationsResult = identifyAIApplications(content);
    const roiClarityResult = verifyROIClarity(content);
    const k12FocusResult = validateK12Focus(content);
    const teacherWorkloadResult = verifyTeacherWorkloadReduction(content);
    const studentOutcomeResult = verifyStudentOutcomeImprovement(content);

    // Combine all results
    const comprehensiveResult = {
      timestamp: new Date().toISOString(),
      bookPath,
      aiApplications: aiApplicationsResult,
      roiClarity: roiClarityResult,
      k12Focus: k12FocusResult,
      teacherWorkloadReduction: teacherWorkloadResult,
      studentOutcomeImprovement: studentOutcomeResult,
      overallStatus: determineOverallStatus([
        aiApplicationsResult.status,
        roiClarityResult.status,
        k12FocusResult.status,
        teacherWorkloadResult.status,
        studentOutcomeResult.status
      ]),
      summary: {
        totalApplications: aiApplicationsResult.totalApplications,
        roiElements: roiClarityResult.totalElements,
        k12Indicators: k12FocusResult.totalK12Indicators,
        workloadReductionIndicators: teacherWorkloadResult.totalIndicators,
        outcomeImprovementIndicators: studentOutcomeResult.totalIndicators
      }
    };

    // Write comprehensive results to a file
    const resultsDir = path.join(process.cwd(), 'audit-results');
    await fs.mkdir(resultsDir, { recursive: true });

    const resultsPath = path.join(resultsDir, 'comprehensive-audit-results.json');
    await fs.writeFile(resultsPath, JSON.stringify(comprehensiveResult, null, 2));

    console.log(`Comprehensive audit completed. Results saved to ${resultsPath}`);
    console.log('Overall status:', comprehensiveResult.overallStatus);

    return comprehensiveResult;
  } catch (error) {
    console.error('Error running comprehensive audit:', error);
    throw error;
  }
}

/**
 * Determines the overall status based on individual component statuses
 * @param {string[]} statuses - Array of individual statuses
 * @returns {string} - Overall status
 */
function determineOverallStatus(statuses) {
  // If any component fails, the overall status is fail
  if (statuses.includes('fail')) {
    return 'fail';
  }
  // If all components pass, the overall status is pass
  if (statuses.every(status => status === 'pass')) {
    return 'pass';
  }
  // Otherwise, it's a partial pass or warning
  return 'warning';
}

/**
 * Main function to run the comprehensive audit
 */
async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node comprehensive-audit.js <book-path>');
    process.exit(1);
  }

  try {
    const result = await runComprehensiveAudit(args[0]);
    console.log('\nAudit Summary:');
    console.log(`- AI Applications Found: ${result.summary.totalApplications}`);
    console.log(`- ROI Elements Identified: ${result.summary.roiElements}`);
    console.log(`- K-12 Focus Indicators: ${result.summary.k12Indicators}`);
    console.log(`- Workload Reduction Indicators: ${result.summary.workloadReductionIndicators}`);
    console.log(`- Outcome Improvement Indicators: ${result.summary.outcomeImprovementIndicators}`);
    console.log(`- Overall Status: ${result.overallStatus}`);

    // Exit with appropriate code based on overall status
    process.exit(result.overallStatus === 'pass' ? 0 : 1);
  } catch (error) {
    console.error('Comprehensive audit failed:', error);
    process.exit(1);
  }
}

// Export functions for testing
module.exports = {
  runComprehensiveAudit,
  determineOverallStatus
};

// If this script is run directly, execute the main function
if (require.main === module) {
  main();
}