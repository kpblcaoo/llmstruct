package main

import (
    "encoding/json"
    "fmt"
    "go/ast"
    "go/token"
    "log"
    "os"
    "path/filepath"
    "sort"
    "strings"
    
    "golang.org/x/tools/go/packages"
)

type Function struct {
    Name         string   `json:"name"`
    Params       []string `json:"params"`
    Returns      []string `json:"returns"`
    Line         int      `json:"line"`
    EndLine      int      `json:"end_line"`
    Docstring    string   `json:"docstring"`
    Receiver     string   `json:"receiver,omitempty"`
    IsExported   bool     `json:"is_exported"`
    IsMethod     bool     `json:"is_method"`
}

type Struct struct {
    Name         string   `json:"name"`
    Fields       []string `json:"fields"`
    Line         int      `json:"line"`
    EndLine      int      `json:"end_line"`
    Docstring    string   `json:"docstring"`
    IsExported   bool     `json:"is_exported"`
    Methods      []Function `json:"methods"`
}

type Variable struct {
    Name         string   `json:"name"`
    Type         string   `json:"type"`
    Line         int      `json:"line"`
    IsExported   bool     `json:"is_exported"`
    IsConstant   bool     `json:"is_constant"`
}

type Import struct {
    Path         string   `json:"path"`
    Alias        string   `json:"alias"`
    Line         int      `json:"line"`
}

type FileAnalysis struct {
    Path         string     `json:"path"`
    Package      string     `json:"package"`
    Imports      []Import   `json:"imports"`
    Functions    []Function `json:"functions"`
    Structs      []Struct   `json:"structs"`
    Variables    []Variable `json:"variables"`
    Constants    []Variable `json:"constants"`
    Interfaces   []Struct   `json:"interfaces"`
    LineCount    int        `json:"line_count"`
    HasTests     bool       `json:"has_tests"`
}

type ProjectAnalysis struct {
    ModuleName     string         `json:"module_name"`
    GoVersion      string         `json:"go_version"`
    Files          []FileAnalysis `json:"files"`
    Dependencies   []string       `json:"dependencies"`
    AllPackages    []string       `json:"all_packages"`
    TestFiles      []string       `json:"test_files"`
    TotalLines     int            `json:"total_lines"`
    HasGoMod       bool           `json:"has_go_mod"`
    Errors         []string       `json:"errors"`
}

func extractTypeString(expr ast.Expr) string {
    if expr == nil {
        return ""
    }
    
    switch t := expr.(type) {
    case *ast.Ident:
        return t.Name
    case *ast.StarExpr:
        return "*" + extractTypeString(t.X)
    case *ast.ArrayType:
        return "[]" + extractTypeString(t.Elt)
    case *ast.SelectorExpr:
        return extractTypeString(t.X) + "." + t.Sel.Name
    case *ast.MapType:
        return "map[" + extractTypeString(t.Key) + "]" + extractTypeString(t.Value)
    case *ast.ChanType:
        dir := ""
        if t.Dir == ast.SEND {
            dir = "chan<- "
        } else if t.Dir == ast.RECV {
            dir = "<-chan "
        } else {
            dir = "chan "
        }
        return dir + extractTypeString(t.Value)
    case *ast.InterfaceType:
        return "interface{}"
    case *ast.StructType:
        return "struct{}"
    case *ast.FuncType:
        return "func"
    case *ast.Ellipsis:
        return "..." + extractTypeString(t.Elt)
    default:
        return fmt.Sprintf("%T", t)
    }
}

func extractDocstring(doc *ast.CommentGroup) string {
    if doc == nil {
        return ""
    }
    
    var lines []string
    for _, comment := range doc.List {
        text := comment.Text
        if strings.HasPrefix(text, "//") {
            text = strings.TrimPrefix(text, "//")
        } else if strings.HasPrefix(text, "/*") && strings.HasSuffix(text, "*/") {
            text = strings.TrimSuffix(strings.TrimPrefix(text, "/*"), "*/")
        }
        text = strings.TrimSpace(text)
        if text != "" {
            lines = append(lines, text)
        }
    }
    return strings.Join(lines, " ")
}

func countLines(filename string) int {
    content, err := os.ReadFile(filename)
    if err != nil {
        return 0
    }
    return strings.Count(string(content), "\n") + 1
}

func analyzeFile(pkg *packages.Package, file *ast.File, fset *token.FileSet) FileAnalysis {
    filename := fset.Position(file.Pos()).Filename
    
    analysis := FileAnalysis{
        Path:      filename,
        Package:   file.Name.Name,
        Imports:   []Import{},
        Functions: []Function{},
        Structs:   []Struct{},
        Variables: []Variable{},
        Constants: []Variable{},
        Interfaces: []Struct{},
        LineCount: countLines(filename),
        HasTests:  strings.HasSuffix(filename, "_test.go"),
    }
    
    // Анализируем импорты
    for _, imp := range file.Imports {
        importPath := strings.Trim(imp.Path.Value, "\"")
        alias := ""
        if imp.Name != nil {
            alias = imp.Name.Name
        }
        
        analysis.Imports = append(analysis.Imports, Import{
            Path:  importPath,
            Alias: alias,
            Line:  fset.Position(imp.Pos()).Line,
        })
    }
    
    // Анализируем декларации
    for _, decl := range file.Decls {
        switch d := decl.(type) {
        case *ast.FuncDecl:
            // Анализируем функции и методы
            fn := Function{
                Name:       d.Name.Name,
                Line:       fset.Position(d.Pos()).Line,
                EndLine:    fset.Position(d.End()).Line,
                IsExported: d.Name.IsExported(),
                IsMethod:   d.Recv != nil,
                Docstring:  extractDocstring(d.Doc),
                Params:     []string{},
                Returns:    []string{},
            }
            
            // Receiver для методов
            if d.Recv != nil && len(d.Recv.List) > 0 {
                fn.Receiver = extractTypeString(d.Recv.List[0].Type)
            }
            
            // Параметры
            if d.Type.Params != nil {
                for _, param := range d.Type.Params.List {
                    paramType := extractTypeString(param.Type)
                    if len(param.Names) > 0 {
                        for _, name := range param.Names {
                            fn.Params = append(fn.Params, name.Name+" "+paramType)
                        }
                    } else {
                        fn.Params = append(fn.Params, paramType)
                    }
                }
            }
            
            // Возвращаемые значения
            if d.Type.Results != nil {
                for _, result := range d.Type.Results.List {
                    returnType := extractTypeString(result.Type)
                    if len(result.Names) > 0 {
                        for _, name := range result.Names {
                            fn.Returns = append(fn.Returns, name.Name+" "+returnType)
                        }
                    } else {
                        fn.Returns = append(fn.Returns, returnType)
                    }
                }
            }
            
            analysis.Functions = append(analysis.Functions, fn)
            
        case *ast.GenDecl:
            // Анализируем типы, переменные, константы
            for _, spec := range d.Specs {
                switch s := spec.(type) {
                case *ast.TypeSpec:
                    switch t := s.Type.(type) {
                    case *ast.StructType:
                        // Структуры
                        st := Struct{
                            Name:       s.Name.Name,
                            Line:       fset.Position(s.Pos()).Line,
                            EndLine:    fset.Position(s.End()).Line,
                            IsExported: s.Name.IsExported(),
                            Docstring:  extractDocstring(s.Doc),
                            Fields:     []string{},
                            Methods:    []Function{},
                        }
                        
                        if t.Fields != nil {
                            for _, field := range t.Fields.List {
                                fieldType := extractTypeString(field.Type)
                                if len(field.Names) > 0 {
                                    for _, name := range field.Names {
                                        st.Fields = append(st.Fields, name.Name+" "+fieldType)
                                    }
                                } else {
                                    // Embedded field
                                    st.Fields = append(st.Fields, fieldType)
                                }
                            }
                        }
                        
                        analysis.Structs = append(analysis.Structs, st)
                        
                    case *ast.InterfaceType:
                        // Интерфейсы
                        iface := Struct{
                            Name:       s.Name.Name,
                            Line:       fset.Position(s.Pos()).Line,
                            EndLine:    fset.Position(s.End()).Line,
                            IsExported: s.Name.IsExported(),
                            Docstring:  extractDocstring(s.Doc),
                            Fields:     []string{},
                            Methods:    []Function{},
                        }
                        
                        if t.Methods != nil {
                            for _, method := range t.Methods.List {
                                if len(method.Names) > 0 {
                                    for _, name := range method.Names {
                                        methodSig := name.Name + extractTypeString(method.Type)
                                        iface.Fields = append(iface.Fields, methodSig)
                                    }
                                }
                            }
                        }
                        
                        analysis.Interfaces = append(analysis.Interfaces, iface)
                    }
                    
                case *ast.ValueSpec:
                    // Переменные и константы
                    for _, name := range s.Names {
                        variable := Variable{
                            Name:       name.Name,
                            Type:       extractTypeString(s.Type),
                            Line:       fset.Position(s.Pos()).Line,
                            IsExported: name.IsExported(),
                            IsConstant: d.Tok == token.CONST,
                        }
                        
                        if d.Tok == token.CONST {
                            analysis.Constants = append(analysis.Constants, variable)
                        } else {
                            analysis.Variables = append(analysis.Variables, variable)
                        }
                    }
                }
            }
        }
    }
    
    return analysis
}

func main() {
    if len(os.Args) < 2 {
        log.Fatal("Usage: analyzer <project_path>")
    }
    
    projectPath := os.Args[1]
    
    // Конфигурация загрузки пакетов
    cfg := &packages.Config{
        Mode: packages.NeedName |
              packages.NeedFiles |
              packages.NeedCompiledGoFiles |
              packages.NeedImports |
              packages.NeedDeps |
              packages.NeedTypes |
              packages.NeedSyntax |
              packages.NeedTypesInfo,
        Dir: projectPath,
        Env: append(os.Environ(), "CGO_ENABLED=0"),
    }
    
    // Загружаем все пакеты
    pkgs, err := packages.Load(cfg, "./...")
    if err != nil {
        log.Printf("Warning: %v", err)
    }
    
    log.Printf("Loaded %d packages", len(pkgs))
    
    result := ProjectAnalysis{
        Files:        []FileAnalysis{},
        Dependencies: []string{},
        AllPackages:  []string{},
        TestFiles:    []string{},
        Errors:       []string{},
    }
    
    // Получаем информацию о модуле
    if goMod := filepath.Join(projectPath, "go.mod"); fileExists(goMod) {
        result.HasGoMod = true
        if modInfo := parseGoMod(goMod); modInfo != nil {
            result.ModuleName = modInfo.Module
            result.GoVersion = modInfo.Go
        }
    }
    
    allPackages := make(map[string]bool)
    allDeps := make(map[string]bool)
    
    for _, pkg := range pkgs {
        log.Printf("Processing package: %s (path: %s, files: %d)", pkg.Name, pkg.PkgPath, len(pkg.Syntax))
        
        if pkg.Errors != nil {
            for _, err := range pkg.Errors {
                log.Printf("Package error: %s", err.Msg)
                result.Errors = append(result.Errors, fmt.Sprintf("Package %s: %s", pkg.PkgPath, err.Msg))
            }
        }
        
        allPackages[pkg.Name] = true
        
        // Собираем зависимости
        for _, imp := range pkg.Imports {
            allDeps[imp.PkgPath] = true
        }
        
        // Анализируем файлы
        for i, file := range pkg.Syntax {
            if i < len(pkg.CompiledGoFiles) {
                relPath, _ := filepath.Rel(projectPath, pkg.CompiledGoFiles[i])
                analysis := analyzeFile(pkg, file, pkg.Fset)
                analysis.Path = relPath
                
                result.Files = append(result.Files, analysis)
                result.TotalLines += analysis.LineCount
                
                if analysis.HasTests {
                    result.TestFiles = append(result.TestFiles, relPath)
                }
            }
        }
    }
    
    // Преобразуем мапы в слайсы
    for pkg := range allPackages {
        result.AllPackages = append(result.AllPackages, pkg)
    }
    sort.Strings(result.AllPackages)
    
    for dep := range allDeps {
        if !strings.Contains(dep, result.ModuleName) {
            result.Dependencies = append(result.Dependencies, dep)
        }
    }
    sort.Strings(result.Dependencies)
    
    // Выводим результат
    output, err := json.MarshalIndent(result, "", "  ")
    if err != nil {
        log.Fatal("Failed to marshal JSON:", err)
    }
    
    fmt.Println(string(output))
}

type GoModInfo struct {
    Module string
    Go     string
}

func parseGoMod(path string) *GoModInfo {
    content, err := os.ReadFile(path)
    if err != nil {
        return nil
    }
    
    lines := strings.Split(string(content), "\n")
    info := &GoModInfo{}
    
    for _, line := range lines {
        line = strings.TrimSpace(line)
        if strings.HasPrefix(line, "module ") {
            info.Module = strings.TrimSpace(strings.TrimPrefix(line, "module"))
        } else if strings.HasPrefix(line, "go ") {
            info.Go = strings.TrimSpace(strings.TrimPrefix(line, "go"))
        }
    }
    
    return info
}

func fileExists(path string) bool {
    _, err := os.Stat(path)
    return err == nil
} 