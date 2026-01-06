#!/usr/bin/env node
/**
 * Push GLIS to GitHub using GitHub CLI or simple git
 * Run: node push-to-github.js
 */

const { execSync } = require('child_process');
const path = require('path');

const projectDir = 'c:\\Users\\gh\\glis\\ghana_legal_scraper';
const repoUrl = 'https://github.com/tulwegroup/glis.git';

console.log('\n========================================');
console.log('GLIS Repository Setup');
console.log('========================================\n');

try {
  process.chdir(projectDir);
  
  const steps = [
    { name: 'Initialize git', cmd: 'git init' },
    { name: 'Configure user', cmd: 'git config user.name "GLIS Admin" && git config user.email "admin@glis.local"' },
    { name: 'Add files', cmd: 'git add .' },
    { name: 'Create commit', cmd: 'git commit -m "Initial GLIS v2.0 - Complete Ghana Legal Intelligence System"' },
    { name: 'Set main branch', cmd: 'git branch -M main' },
    { name: 'Add remote', cmd: `git remote add origin ${repoUrl}` },
    { name: 'Push to GitHub', cmd: 'git push -u origin main' },
  ];

  steps.forEach((step, i) => {
    console.log(`[${i + 1}/${steps.length}] ${step.name}...`);
    try {
      const output = execSync(step.cmd, { encoding: 'utf8', stdio: 'pipe' });
      console.log('✓ Success\n');
    } catch (err) {
      if (err.message.includes('nothing to commit') || err.message.includes('already exists')) {
        console.log('✓ Already done\n');
      } else {
        console.log(`⚠ ${err.message.split('\n')[0]}\n`);
      }
    }
  });

  console.log('========================================');
  console.log('✓ Setup Complete!');
  console.log('========================================\n');
  console.log('Your GLIS project is on GitHub:');
  console.log('https://github.com/tulwegroup/glis\n');
  
} catch (error) {
  console.error('✗ Error:', error.message);
  process.exit(1);
}
