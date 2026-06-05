const fs = require('fs');
const path = require('path');

const scriptPath = path.join(__dirname, 'static', 'js', 'script.js');
if (!fs.existsSync(scriptPath)) {
  console.error("script.js not found at " + scriptPath);
  process.exit(1);
}

let content = fs.readFileSync(scriptPath, 'utf8');

const startMarker = 'const REACTIONS = [';
const startIndex = content.indexOf(startMarker);
if (startIndex === -1) {
  console.error("Could not find const REACTIONS in script.js");
  process.exit(1);
}

let slice = content.slice(startIndex);
let bracketCount = 0;
let index = 0;

// Find the start of the array
while (index < slice.length && slice[index] !== '[') {
  index++;
}

if (index >= slice.length) {
  console.error("Could not find [ after const REACTIONS");
  process.exit(1);
}

let arrayStartIndex = index; // start of '['
bracketCount = 1;
index++;

while (index < slice.length && bracketCount > 0) {
  if (slice[index] === '[') {
    bracketCount++;
  } else if (slice[index] === ']') {
    bracketCount--;
  }
  index++;
}

let arrayText = slice.slice(arrayStartIndex, index);

const tempFile = path.join(__dirname, 'temp_reactions.js');
fs.writeFileSync(tempFile, 'module.exports = ' + arrayText + ';');

try {
  const reactions = require('./temp_reactions.js');
  fs.writeFileSync(path.join(__dirname, 'reactions_extracted.json'), JSON.stringify(reactions, null, 2));
  console.log(`Successfully extracted ${reactions.length} reactions!`);
} catch (err) {
  console.error("Failed to parse reactions: ", err);
} finally {
  if (fs.existsSync(tempFile)) {
    fs.unlinkSync(tempFile);
  }
}
