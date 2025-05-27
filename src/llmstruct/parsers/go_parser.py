import hashlib
import logging
import os
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Set, List

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def infer_category(file_path: str) -> str:
    """Infer module category based on its path."""
    path = Path(file_path)
    if "test" in path.name or "tests" in path.parts:
        return "test"
    if path.name == "main.go" or "cmd" in path.parts:
        return "cli"
    if "internal" in path.parts:
        return "internal"
    return "core"


def compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of file content."""
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logging.error(f"Failed to compute hash for {file_path}: {e}")
        return ""


def parse_go_ast(source_code: str) -> Dict[str, Any]:
    """Parse Go source using go/ast via go command line tool."""
    try:
        # Create temporary file with Go source
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        # Use go/ast parser to extract structure
        go_ast_script = f"""
package main

import (
    "encoding/json"
    "fmt"
    "go/ast"
    "go/parser"
    "go/token"
    "os"
)

type Function struct {{
    Name       string   `json:"name"`
    Receiver   string   `json:"receiver,omitempty"`
    Parameters []string `json:"parameters"`
    Returns    []string `json:"returns"`
    Comments   []string `json:"comments"`
    StartLine  int      `json:"start_line"`
    EndLine    int      `json:"end_line"`
}}

type Struct struct {{
    Name      string   `json:"name"`
    Fields    []string `json:"fields"`
    Comments  []string `json:"comments"`
    StartLine int      `json:"start_line"`
    EndLine   int      `json:"end_line"`
}}

type Import struct {{
    Path  string `json:"path"`
    Alias string `json:"alias,omitempty"`
}}

type ParseResult struct {{
    Package     string     `json:"package"`
    Imports     []Import   `json:"imports"`
    Functions   []Function `json:"functions"`
    Structs     []Struct   `json:"structs"`
    Comments    []string   `json:"comments"`
}}

func main() {{
    if len(os.Args) < 2 {{
        fmt.Fprintf(os.Stderr, "Usage: %s <go-file>\\n", os.Args[0])
        os.Exit(1)
    }}

    filename := os.Args[1]
    fset := token.NewFileSet()
    
    node, err := parser.ParseFile(fset, filename, nil, parser.ParseComments)
    if err != nil {{
        fmt.Fprintf(os.Stderr, "Error parsing file: %v\\n", err)
        os.Exit(1)
    }}

    result := ParseResult{{
        Package: node.Name.Name,
        Imports: []Import{{}},
        Functions: []Function{{}},
        Structs: []Struct{{}},
        Comments: []string{{}},
    }}

    // Extract imports
    for _, imp := range node.Imports {{
        importSpec := Import{{
            Path: imp.Path.Value[1:len(imp.Path.Value)-1], // Remove quotes
        }}
        if imp.Name != nil {{
            importSpec.Alias = imp.Name.Name
        }}
        result.Imports = append(result.Imports, importSpec)
    }}

    // Extract functions and methods
    for _, decl := range node.Decls {{
        if funcDecl, ok := decl.(*ast.FuncDecl); ok {{
            fn := Function{{
                Name: funcDecl.Name.Name,
                StartLine: fset.Position(funcDecl.Pos()).Line,
                EndLine: fset.Position(funcDecl.End()).Line,
            }}

            // Extract receiver (for methods)
            if funcDecl.Recv != nil && len(funcDecl.Recv.List) > 0 {{
                if field := funcDecl.Recv.List[0]; field.Type != nil {{
                    if ident, ok := field.Type.(*ast.Ident); ok {{
                        fn.Receiver = ident.Name
                    }} else if starExpr, ok := field.Type.(*ast.StarExpr); ok {{
                        if ident, ok := starExpr.X.(*ast.Ident); ok {{
                            fn.Receiver = "*" + ident.Name
                        }}
                    }}
                }}
            }}

            // Extract parameters
            if funcDecl.Type.Params != nil {{
                for _, field := range funcDecl.Type.Params.List {{
                    for _, name := range field.Names {{
                        fn.Parameters = append(fn.Parameters, name.Name)
                    }}
                }}
            }}

            // Extract return types
            if funcDecl.Type.Results != nil {{
                for _, field := range funcDecl.Type.Results.List {{
                    if len(field.Names) > 0 {{
                        for _, name := range field.Names {{
                            fn.Returns = append(fn.Returns, name.Name)
                        }}
                    }} else {{
                        fn.Returns = append(fn.Returns, "unnamed")
                    }}
                }}
            }}

            result.Functions = append(result.Functions, fn)
        }} else if genDecl, ok := decl.(*ast.GenDecl); ok && genDecl.Tok == token.TYPE {{
            // Extract struct types
            for _, spec := range genDecl.Specs {{
                if typeSpec, ok := spec.(*ast.TypeSpec); ok {{
                    if structType, ok := typeSpec.Type.(*ast.StructType); ok {{
                        s := Struct{{
                            Name: typeSpec.Name.Name,
                            StartLine: fset.Position(typeSpec.Pos()).Line,
                            EndLine: fset.Position(typeSpec.End()).Line,
                        }}

                        // Extract fields
                        if structType.Fields != nil {{
                            for _, field := range structType.Fields.List {{
                                for _, name := range field.Names {{
                                    s.Fields = append(s.Fields, name.Name)
                                }}
                            }}
                        }}

                        result.Structs = append(result.Structs, s)
                    }}
                }}
            }}
        }}
    }}

    // Extract package and general comments
    for _, commentGroup := range node.Comments {{
        for _, comment := range commentGroup.List {{
            result.Comments = append(result.Comments, comment.Text)
        }}
    }}

    jsonData, err := json.Marshal(result)
    if err != nil {{
        fmt.Fprintf(os.Stderr, "Error marshaling JSON: %v\\n", err)
        os.Exit(1)
    }}

    fmt.Print(string(jsonData))
}}
"""
        
        # Write the Go AST parser script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
            f.write(go_ast_script)
            parser_file = f.name
        
        # Run the Go parser
        result = subprocess.run(
            ['go', 'run', parser_file, temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up temp files
        os.unlink(temp_file)
        os.unlink(parser_file)
        
        if result.returncode != 0:
            logging.error(f"Go parser failed: {result.stderr}")
            return {}
            
        return json.loads(result.stdout)
        
    except Exception as e:
        logging.error(f"Failed to parse Go AST: {e}")
        return {}


def extract_go_dependencies(source_code: str) -> List[str]:
    """Extract import statements from Go source code using regex."""
    dependencies = []
    
    # Match import statements
    import_patterns = [
        r'import\s+"([^"]+)"',  # import "package"
        r'import\s+\w+\s+"([^"]+)"',  # import alias "package"
        r'import\s*\(\s*([^)]+)\s*\)',  # import ( ... )
    ]
    
    for pattern in import_patterns:
        matches = re.finditer(pattern, source_code, re.MULTILINE | re.DOTALL)
        for match in matches:
            if pattern.endswith(r'\)'):
                # Multi-line import block
                import_block = match.group(1)
                # Extract individual imports from block
                import_lines = re.findall(r'"([^"]+)"', import_block)
                dependencies.extend(import_lines)
            else:
                dependencies.append(match.group(1))
    
    return sorted(list(set(dependencies)))


def analyze_module(
    file_path: str, root_dir: str, include_ranges: bool, include_hashes: bool
) -> Optional[Dict[str, Any]]:
    """Analyze Go module and return structured data."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        logging.error(f"Failed to read {file_path}: {e}")
        return None

    # Parse Go AST
    ast_data = parse_go_ast(source)
    if not ast_data:
        # Fallback to regex-based parsing
        ast_data = {
            "package": "unknown",
            "imports": [],
            "functions": [],
            "structs": [],
            "comments": []
        }

    # Extract module info
    module_id = (
        str(Path(file_path).relative_to(root_dir))
        .replace(os.sep, ".")
        .rsplit(".go", 1)[0]
    )
    
    # Extract package documentation (first comment block)
    module_doc = ""
    if ast_data.get("comments"):
        package_comments = [c for c in ast_data["comments"] if c.startswith("// Package") or c.startswith("/*")]
        if package_comments:
            module_doc = package_comments[0].strip("// /**/")

    # Convert AST data to llmstruct format
    functions = []
    for fn in ast_data.get("functions", []):
        functions.append({
            "name": fn["name"],
            "docstring": "\n".join(fn.get("comments", [])),
            "line_range": [fn["start_line"], fn["end_line"]] if include_ranges else None,
            "parameters": fn.get("parameters", []),
            "returns": fn.get("returns", []),
            "receiver": fn.get("receiver", ""),
        })

    classes = []  # Go doesn't have classes, but structs serve similar purpose
    for struct in ast_data.get("structs", []):
        classes.append({
            "name": struct["name"],
            "docstring": "\n".join(struct.get("comments", [])),
            "line_range": [struct["start_line"], struct["end_line"]] if include_ranges else None,
            "fields": struct.get("fields", []),
            "methods": [],  # Would need to find methods with this struct as receiver
        })

    # Extract dependencies
    dependencies = extract_go_dependencies(source)
    if ast_data.get("imports"):
        ast_imports = [imp["path"] for imp in ast_data["imports"]]
        dependencies.extend(ast_imports)
        dependencies = sorted(list(set(dependencies)))

    # Simple callgraph (function names that appear in source)
    callgraph = {}
    for fn in functions:
        callgraph[fn["name"]] = []
        # Find function calls in source (simple regex approach)
        func_calls = re.findall(r'\b(\w+)\s*\(', source)
        # Filter to only include other functions defined in this module
        defined_functions = {f["name"] for f in functions}
        callgraph[fn["name"]] = [call for call in func_calls if call in defined_functions and call != fn["name"]]

    return {
        "module_id": module_id,
        "path": str(Path(file_path).relative_to(root_dir)),
        "category": infer_category(file_path),
        "package": ast_data.get("package", "unknown"),
        "module_doc": module_doc,
        "functions": functions,
        "classes": classes,  # structs
        "callgraph": callgraph,
        "dependencies": dependencies,
        "hash": compute_file_hash(file_path) if include_hashes else None,
    } 