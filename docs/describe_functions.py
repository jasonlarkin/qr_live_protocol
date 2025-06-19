import os
import ast
import sys


def find_py_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                yield os.path.join(dirpath, filename)

def describe_functions_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=filepath)
    except Exception as e:
        return [f"  [Error parsing file: {e}]"]
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            doc = ast.get_docstring(node)
            brief = doc.split('\n')[0] if doc else '[No docstring]'
            results.append(f"    - {func_name}(): {brief}")
    return results

def main():
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.getcwd()
    target_dir = os.path.abspath(target_dir)
    
    # Generate output content
    output_lines = []
    for pyfile in sorted(find_py_files(target_dir)):
        rel_path = os.path.relpath(pyfile, target_dir)
        output_lines.append(f"{rel_path}:")
        for desc in describe_functions_in_file(pyfile):
            output_lines.append(desc)
        output_lines.append("")
    
    # Create output filename
    dir_name = os.path.basename(target_dir)
    output_filename = f"describe_functions_{dir_name}.md"
    
    # Write to file with bash code block wrapper
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("```bash\n")
        f.write("\n".join(output_lines))
        f.write("```\n")
    
    print(f"Output written to: {output_filename}")

if __name__ == '__main__':
    main() 