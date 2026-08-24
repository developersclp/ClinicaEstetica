const fs = require('fs');

function processFile(path) {
  let c = fs.readFileSync(path, 'utf8');
  // Add import
  if (!c.includes('Portal')) {
    c = c.replace(/import \{.*?\} from 'react';/, match => match + '\r\nimport Portal from \'../../components/Portal\';');
  }

  // Split into lines
  const lines = c.split(/\r?\n/);
  const outLines = [];
  let inModal = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.includes('return (') && lines[i+1] && lines[i+1].includes('className="fixed inset-0')) {
      inModal = true;
      outLines.push(line);
      outLines.push('    <Portal>');
      outLines.push('  ' + lines[i+1]); // indent original line
      i++; // skip next line
      continue;
    }

    if (inModal) {
      if (line.trim() === '};' || line.trim() === '}') {
        // Look back to the previous line, if it's `  );`, we insert </Portal>
        let prev = outLines.pop();
        if (prev && prev.trim() === ');') {
           outLines.push('    </Portal>');
           outLines.push(prev);
           outLines.push(line);
           inModal = false;
        } else {
           outLines.push(prev);
           outLines.push(line);
        }
      } else {
        outLines.push(line);
      }
    } else {
      outLines.push(line);
    }
  }

  fs.writeFileSync(path, outLines.join('\r\n'), 'utf8');
  console.log(path + ' modified.');
}

processFile('src/pages/financeiro/FinanceiroComponents.jsx');
processFile('src/pages/estoque/EstoqueComponents.jsx');
