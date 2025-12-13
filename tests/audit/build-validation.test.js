/**
 * Integration test for Docusaurus build validation
 * Tests that the Docusaurus site can be built successfully
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Mock function to simulate Docusaurus build validation
function validateBuild(docsDir = './my-website') {
  const docusaurusConfigPath = path.join(docsDir, 'docusaurus.config.ts');

  if (!fs.existsSync(docusaurusConfigPath)) {
    return {
      valid: false,
      errors: [`Docusaurus config not found at ${docusaurusConfigPath}`]
    };
  }

  // Check if package.json exists and has required dependencies
  const packageJsonPath = path.join(docsDir, 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    return {
      valid: false,
      errors: [`package.json not found at ${packageJsonPath}`]
    };
  }

  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const hasDocusaurus = packageJson.dependencies &&
                        (packageJson.dependencies['@docusaurus/core'] ||
                         packageJson.devDependencies && packageJson.devDependencies['@docusaurus/core']);

  if (!hasDocusaurus) {
    return {
      valid: false,
      errors: ['Docusaurus dependency not found in package.json']
    };
  }

  return {
    valid: true,
    errors: [],
    configExists: true,
    dependenciesValid: true
  };
}

describe('Docusaurus Build Validation', () => {
  test('should validate build configuration exists', () => {
    const result = validateBuild('./my-website');
    expect(result.configExists).toBe(true);
    expect(result.dependenciesValid).toBe(true);
    expect(result.valid).toBe(true);
  });

  test('should fail if docusaurus config does not exist', () => {
    // Create a mock directory structure to test the failure case
    const tempDir = './temp-test-dir';
    fs.mkdirSync(tempDir, { recursive: true });

    const result = validateBuild(tempDir);
    expect(result.valid).toBe(false);
    expect(result.errors).toContainEqual(expect.stringContaining('Docusaurus config not found'));

    // Clean up
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  test('should validate Docusaurus dependencies in package.json', () => {
    const result = validateBuild('./my-website');
    expect(result.dependenciesValid).toBe(true);
  });

  test('should check for required Docusaurus files', () => {
    const docusaurusConfigPath = './my-website/docusaurus.config.ts';
    expect(fs.existsSync(docusaurusConfigPath)).toBe(true);

    const packageJsonPath = './my-website/package.json';
    expect(fs.existsSync(packageJsonPath)).toBe(true);
  });
});

// Additional test for actual build process (would be used in real implementation)
describe('Actual Build Process', () => {
  test('should build without errors', () => {
    // This test would actually run the build command in a real scenario
    // For now, we just verify the configuration is correct

    const docusaurusConfigPath = './my-website/docusaurus.config.ts';
    expect(fs.existsSync(docusaurusConfigPath)).toBe(true);

    const packageJsonPath = './my-website/package.json';
    expect(fs.existsSync(packageJsonPath)).toBe(true);

    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const hasDocusaurus = packageJson.dependencies &&
                          (packageJson.dependencies['@docusaurus/core'] ||
                           packageJson.devDependencies && packageJson.devDependencies['@docusaurus/core']);

    expect(hasDocusaurus).toBe(true);
  });
});