// Reads formulas.json ({key: {tex, display}}), writes formulas_html.json ({key: html}).
// strict: 'error' makes any Cyrillic/unicode text inside math fail loudly.
const fs = require('fs');
const path = require('path');
const katex = require('katex');

const src = JSON.parse(fs.readFileSync(path.join(__dirname, 'formulas.json'), 'utf8'));
const out = {};
const errors = [];
for (const [key, {tex, display}] of Object.entries(src)) {
  try {
    out[key] = katex.renderToString(tex, {
      displayMode: !!display,
      throwOnError: true,
      strict: 'error',
      output: 'html',
      trust: false,
    });
  } catch (e) {
    errors.push(`${key}: ${e.message}\n   TeX: ${tex}`);
  }
}
fs.writeFileSync(path.join(__dirname, 'formulas_html.json'), JSON.stringify(out));
if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`rendered ${Object.keys(out).length} formulas`);
