import js from '@eslint/js';
import nextPlugin from '@next/eslint-plugin-next';

export default [
  js.configs.recommended,
  {
    plugins: {
      '@next/next': nextPlugin,
    },
    rules: {
      ...nextPlugin.configs.recommended.rules,
      ...nextPlugin.configs['core-web-vitals'].rules,
      'no-unused-vars': 'off',
      'no-undef': 'off', // TypeScript handles variable definition checking
    },
  },
  {
    ignores: ['.next/*', 'node_modules/*', 'dist/*', 'coverage/*', 'playwright-report/*'],
  },
];
