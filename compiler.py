import re
import sys

def tokenize(ts_code):
    """ Tokenizes a simple TypeScript snippet. """
    token_spec = [
        ("NUMBER", r"\d+"),
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("EQUAL", r"="),
        ("LET", r"let"),
        ("CONST", r"const"),
        ("COLON", r":"),
        ("SEMICOLON", r";"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("COMMA", r","),
        ("STRING", r'"[^"]*"'),
        ("WHITESPACE", r"\s+"),
        ("DOT", r"\."),  # Added dot token for console.log
    ]
    token_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in token_spec)
    tokens = []
    for match in re.finditer(token_regex, ts_code):
        kind = match.lastgroup
        value = match.group()
        if kind != "WHITESPACE":  # Ignore whitespace
            # Prioritize specific keywords over generic identifiers
            if kind == "IDENTIFIER" and value in ["let", "const"]:
                kind = value.upper()
            tokens.append((kind, value))
    return tokens

def parse(tokens):
    """ Parses tokens into AST. """
    ast = []
    i = 0
    while i < len(tokens):
        if tokens[i][0] in ("LET", "CONST"):  # let/const variable declaration
            var_type = tokens[i][1]
            i += 1
            if i < len(tokens) and tokens[i][0] == "IDENTIFIER":
                var_name = tokens[i][1]
                i += 1
                type_annotation = None
                if i < len(tokens) and tokens[i][0] == "COLON":  # Type annotation
                    i += 1
                    if i < len(tokens) and tokens[i][0] == "IDENTIFIER":
                        type_annotation = tokens[i][1]
                        i += 1
                value = None
                if i < len(tokens) and tokens[i][0] == "EQUAL":
                    i += 1
                    if i < len(tokens) and tokens[i][0] in ("STRING", "NUMBER", "IDENTIFIER"):
                        value = tokens[i][1]
                        i += 1
                if i < len(tokens) and tokens[i][0] == "SEMICOLON":
                    i += 1
                ast.append({
                    "type": "VariableDeclaration",
                    "kind": var_type,
                    "name": var_name,
                    "typeAnnotation": type_annotation,
                    "value": value
                })
        elif i+2 < len(tokens) and tokens[i][0] == "IDENTIFIER" and tokens[i][1] == "console" and tokens[i+1][0] == "DOT" and tokens[i+2][0] == "IDENTIFIER" and tokens[i+2][1] == "log":
            i += 3  # Skip console.log
            if i < len(tokens) and tokens[i][0] == "LPAREN":
                i += 1  # Consume (
                args = []
                while i < len(tokens) and tokens[i][0] != "RPAREN":
                    if tokens[i][0] in ("IDENTIFIER", "STRING", "NUMBER"):
                        args.append(tokens[i][1])
                        i += 1
                        if i < len(tokens) and tokens[i][0] == "COMMA":
                            i += 1
                    else:
                        i += 1  # Skip unknown tokens
                if i < len(tokens) and tokens[i][0] == "RPAREN":
                    i += 1  # Consume RPAREN
                    if i < len(tokens) and tokens[i][0] == "SEMICOLON":
                        i += 1  # Consume semicolon
                        ast.append({
                            "type": "ConsoleLog",
                            "arguments": args
                        })
                    else:
                        i += 1  # Skip if no semicolon (more forgiving)
                else:
                    i += 1  # Skip if no closing parenthesis (more forgiving)
            else:
                i += 1  # Skip if no opening parenthesis
        else:
            i += 1  # Move to next token
    return ast

def transpile(ast):
    """ Converts AST to JavaScript. """
    js_code = ""
    for node in ast:
        if node["type"] == "VariableDeclaration":
            # No need for type annotation in JavaScript
            js_code += f"{node['kind']} {node['name']} = {node['value']};\n"
        elif node["type"] == "ConsoleLog":
            args = ", ".join(node["arguments"])
            js_code += f"console.log({args});\n"
    return js_code

def compile_ts_file(input_file):
    """Compiles a TypeScript file to JavaScript."""
    try:
        # Read the input TypeScript file
        with open(input_file) as f:
            ts_code = f.read()
            
        print(f"TypeScript Code from {input_file}:\n{ts_code}")
        
        # Generate output JavaScript file name
        output_file = input_file.replace('.ts', '.js')
        
        # Process TypeScript code
        tokens = tokenize(ts_code)
        
        ast = parse(tokens)
        
        js_code = transpile(ast)
        print(f"Generated JavaScript:\n{js_code}")
        
        # Write JavaScript code to output file
        with open(output_file, 'w') as f:
            f.write(js_code)
            
        print(f"Successfully compiled {input_file} to {output_file}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error during compilation: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compiler.py example.ts")
    else:
        input_file = sys.argv[1]
        compile_ts_file(input_file)
