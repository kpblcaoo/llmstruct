#!/usr/bin/env python3
"""
Minimal Ollama Parser - Clean JSON without extra analytics
Just structure original data properly, remove irrelevant entries
"""

import json
import re

def parse_ollama_minimal(file_path):
    """Minimal parser - just clean structure"""
    models = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if not line or line in ['Pulls', 'Tags', 'Updated'] or line.isdigit() or \
           (line.endswith('M') and any(c.isdigit() for c in line)) or \
           (line.endswith('K') and any(c.isdigit() for c in line)):
            i += 1
            continue
        
        # Check if this is a real model name (not capability or size)
        if line not in ['tools', 'vision', 'thinking', 'embedding'] and \
           not (line.endswith('b') and any(c.isdigit() for c in line)) and \
           not line.endswith('m') and len(line) > 2:
            
            model = {"name": line, "description": "", "capabilities": [], "sizes": [], "pulls": "", "updated": ""}
            i += 1
            
            # Get description if next line is description
            if i < len(lines) and lines[i] and \
               lines[i] not in ['tools', 'vision', 'thinking', 'embedding'] and \
               not lines[i].endswith('b') and not lines[i].endswith('M') and \
               not lines[i].endswith('K') and not lines[i].endswith('m') and \
               not lines[i].isdigit():
                model["description"] = lines[i]
                i += 1
            
            if i < len(lines) and not lines[i]:
                i += 1  # Skip empty line
            
            # Parse model data
            while i < len(lines):
                line = lines[i]
                
                if not line:
                    i += 1
                    continue
                
                if line in ['tools', 'vision', 'thinking', 'embedding']:
                    model["capabilities"].append(line)
                elif (line.endswith('b') or line.endswith('m')) and (any(c.isdigit() for c in line) or 'x' in line):
                    model["sizes"].append(line)
                elif (line.endswith('M') or line.endswith('K')) and any(c.isdigit() for c in line):
                    model["pulls"] = line
                    i += 1
                    if i < len(lines) and lines[i] == 'Pulls':
                        i += 1
                    continue
                elif line.isdigit():
                    i += 1
                    if i < len(lines) and lines[i] == 'Tags':
                        i += 1
                    continue
                elif line == 'Updated':
                    i += 1
                    if i < len(lines):
                        model["updated"] = lines[i]
                        i += 1
                    break
                elif line not in ['tools', 'vision', 'thinking', 'embedding'] and \
                     not (line.endswith('b') and any(c.isdigit() for c in line)) and \
                     not line.endswith('m') and len(line) > 2 and \
                     line not in ['Pulls', 'Tags'] and not line.isdigit() and \
                     not line.endswith('M') and not line.endswith('K'):
                    break  # Hit next model
                
                i += 1
            
            if model["name"]:
                models.append(model)
        else:
            i += 1
    
    return models

def create_compact_json(models, md_content):
    """Create compact JSON structure"""
    
    # Convert MD to simple structure
    md_sections = {}
    current_section = None
    current_content = []
    
    for line in md_content.split('\n'):
        if line.startswith('#'):
            if current_section:
                md_sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.strip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        md_sections[current_section] = '\n'.join(current_content).strip()
    
    # Create minimal structure
    return {
        "context": md_sections,
        "ollama_models": {
            "total_count": len(models),
            "models": [
                {
                    "name": m["name"],
                    "desc": m["description"][:100] + "..." if len(m["description"]) > 100 else m["description"],
                    "caps": m["capabilities"],
                    "sizes": m["sizes"],
                    "pulls": m["pulls"],
                    "updated": m["updated"]
                }
                for m in models
                if m["name"] and m["name"] not in ['tools', 'vision', 'thinking', 'embedding']
            ]
        },
        "project": {
            "name": "LLMStruct",
            "scale": "272 modules, 1857 functions, 183 classes",
            "hardware": "RTX 3060 Ti (8GB VRAM)",
            "budget": "$21.685 remaining"
        },
        "question": "Which Ollama models should we use for LLMStruct architectural analysis on RTX 3060 Ti 8GB? Consider: original GPT-4.1 plan vs Grok series vs hybrid approach vs enhanced self-analysis with local models."
    }

def main():
    print("🔄 Minimal parsing...")
    models = parse_ollama_minimal("tmp/ollama_list.txt")
    print(f"✅ {len(models)} models parsed")
    
    # Filter out any remaining junk
    clean_models = [m for m in models if m["name"] and len(m["name"]) > 1 and 
                   m["name"] not in ['tools', 'vision', 'thinking', 'embedding']]
    print(f"✅ {len(clean_models)} clean models")
    
    print(f"\n📝 Sample models:")
    for i, m in enumerate(clean_models[:10]):
        print(f"   {i+1}. {m['name']}")
    
    # Read context
    with open("grok_consultations_series_2/updated_comprehensive_context.md", 'r') as f:
        md_content = f.read()
    
    # Create compact JSON
    compact_json = create_compact_json(clean_models, md_content)
    
    # Save minimal file
    output_file = "grok_consultations_series_2/minimal_ollama_context.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compact_json, f, indent=1, ensure_ascii=False)  # indent=1 for compactness
    
    print(f"\n✅ Minimal context saved!")
    print(f"📄 File: {output_file}")
    
    # Show file size comparison
    import os
    size_kb = os.path.getsize(output_file) / 1024
    print(f"📊 Size: {size_kb:.1f}KB")
    
    with open(output_file, 'r') as f:
        lines = len(f.readlines())
    print(f"📏 Lines: {lines}")
    
    print(f"🎯 Models: {len(compact_json['ollama_models']['models'])}")

if __name__ == "__main__":
    main() 