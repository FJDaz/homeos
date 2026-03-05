const fs = require('fs');
const acorn = require('acorn');

const filePath = process.argv[2];

if (!filePath) {
    console.error(JSON.stringify({ error: "File path missing." }));
    process.exit(1);
}

try {
    const code = fs.readFileSync(filePath, 'utf-8');
    const ast = acorn.parse(code, {
        ecmaVersion: 'latest',
        sourceType: 'module',
        locations: true
    });

    const nodes = [];

    function processNode(node, currentClass = null) {
        if (!node || typeof node !== 'object') return;

        let passClass = currentClass;

        if (node.type === 'ClassDeclaration' || node.type === 'ClassExpression') {
            const name = node.id ? node.id.name : '<anonymous>';
            nodes.push({
                name: name,
                node_type: 'class',
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: null
            });
            passClass = name;
        }
        else if (node.type === 'MethodDefinition') {
            let name = '<anonymous>';
            if (node.key && node.key.type === 'Identifier') name = node.key.name;
            else if (node.key && node.key.type === 'PrivateIdentifier') name = '#' + node.key.name;

            nodes.push({
                name: name,
                node_type: 'method',
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: currentClass
            });
        }
        else if (node.type === 'FunctionDeclaration') {
            const name = node.id ? node.id.name : '<anonymous>';
            nodes.push({
                name: name,
                node_type: 'function',
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: currentClass
            });
        }
        else if (node.type === 'VariableDeclarator' && node.init &&
            (node.init.type === 'ArrowFunctionExpression' || node.init.type === 'FunctionExpression')) {
            const name = node.id && node.id.type === 'Identifier' ? node.id.name : '<anonymous>';
            nodes.push({
                name: name,
                node_type: !!currentClass ? 'method' : 'function',
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: currentClass
            });
        }
        else if (node.type === 'Property' && node.value &&
            (node.value.type === 'FunctionExpression' || node.value.type === 'ArrowFunctionExpression')) {
            // Object methods mapping
            let name = '<anonymous>';
            if (node.key && node.key.type === 'Identifier') name = node.key.name;

            // To consider objects as simple collections of functions/methods
            nodes.push({
                name: name,
                node_type: !!currentClass ? 'method' : 'function',
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: currentClass
            });
        }
        else if (node.type === 'VariableDeclarator' && node.init &&
            (node.init.type === 'ObjectExpression') && node.id && node.id.type === 'Identifier') {
            // Named object literal could act like a pseudo-class container for methods
            nodes.push({
                name: node.id.name,
                node_type: 'class', // We treat object containers holding functions somewhat like classes
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: null
            });
            passClass = node.id.name;
        }
        else if (node.type === 'ImportDeclaration') {
            nodes.push({
                name: `import ... from '${node.source.value}'`,
                node_type: 'import',
                line_start: node.loc.start.line,
                line_end: node.loc.end.line,
                start_char: node.start,
                end_char: node.end,
                parent: null
            });
        }

        // Recursion
        for (const key in node) {
            if (key === 'loc' || key === 'range' || key === 'type') continue;
            const child = node[key];
            if (Array.isArray(child)) {
                child.forEach(c => processNode(c, passClass));
            } else if (child && typeof child === 'object') {
                processNode(child, passClass);
            }
        }
    }

    processNode(ast);
    console.log(JSON.stringify({ nodes: nodes }));

} catch (err) {
    console.error(JSON.stringify({ error: err.message, stack: err.stack }));
    process.exit(1);
}
