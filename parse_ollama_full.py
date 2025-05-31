#!/usr/bin/env python3
"""
Full Ollama List Parser + Context Merger for Grok Consultation
Parses ollama_list.txt (2103 lines) and merges with existing context
"""

import json
import re
from pathlib import Path

def parse_ollama_list(file_path):
    """Parse ollama_list.txt and return structured data"""
    models = []
    current_model = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
            
        # Check if this is a model name (first line of model block)
        if i == 0 or (i > 0 and lines[i-1].strip() == ""):
            # Save previous model if exists
            if current_model:
                models.append(current_model)
            
            # Start new model
            current_model = {
                "name": line,
                "description": "",
                "capabilities": [],
                "sizes": [],
                "pulls": "",
                "tags": "",
                "updated": ""
            }
            i += 1
            continue
        
        # Check for description (usually comes after model name)
        if not current_model.get("description") and line and not line.endswith("b") and not line.endswith("M") and not line.endswith("K") and line not in ["tools", "vision", "thinking", "embedding"]:
            current_model["description"] = line
            i += 1
            continue
        
        # Check for capabilities
        if line in ["tools", "vision", "thinking", "embedding"]:
            current_model["capabilities"].append(line)
            i += 1
            continue
            
        # Check for sizes (lines ending with 'b')
        if line.endswith("b") and any(c.isdigit() for c in line):
            current_model["sizes"].append(line)
            i += 1
            continue
            
        # Check for pulls (lines ending with 'M' or 'K' followed by 'Pulls')
        if (line.endswith("M") or line.endswith("K")) and i+2 < len(lines) and "Pulls" in lines[i+1]:
            current_model["pulls"] = line
            i += 3  # Skip "Pulls" and next line
            continue
            
        # Check for tags
        if line.isdigit() and i+2 < len(lines) and "Tags" in lines[i+1]:
            current_model["tags"] = line
            i += 3  # Skip "Tags" and next line
            continue
            
        # Check for updated info
        if "Updated" in line:
            if i+1 < len(lines):
                current_model["updated"] = lines[i+1].strip()
                i += 2
            else:
                i += 1
            continue
            
        i += 1
    
    # Don't forget the last model
    if current_model:
        models.append(current_model)
    
    return models

def convert_md_to_json(md_content):
    """Convert markdown content to structured JSON"""
    # Split into sections
    sections = {}
    current_section = None
    current_content = []
    
    lines = md_content.split('\n')
    
    for line in lines:
        if line.startswith('#'):
            # Save previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line.strip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return {
        "document_type": "comprehensive_context",
        "version": "2.0",
        "sections": sections,
        "raw_content": md_content
    }

def create_flattened_models_structure(models):
    """Create a flattened structure that's more LLM-friendly"""
    flattened = {
        "total_models": len(models),
        "categories": {
            "code_analysis": [],
            "reasoning": [],
            "vision": [],
            "embedding": [],
            "tools": [],
            "thinking": [],
            "general": []
        },
        "by_size": {
            "small_1b_3b": [],
            "medium_7b_14b": [],
            "large_27b_70b": [],
            "xlarge_405b_plus": []
        },
        "top_by_pulls": [],
        "all_models_flat": []
    }
    
    # Sort by pulls for top models
    def parse_pulls(pulls_str):
        if not pulls_str:
            return 0
        if pulls_str.endswith('M'):
            return float(pulls_str[:-1]) * 1000000
        elif pulls_str.endswith('K'):
            return float(pulls_str[:-1]) * 1000
        return 0
    
    sorted_models = sorted(models, key=lambda x: parse_pulls(x.get('pulls', '0')), reverse=True)
    flattened["top_by_pulls"] = sorted_models[:20]  # Top 20
    
    for model in models:
        # Flatten model info
        flat_model = {
            "name": model.get("name", ""),
            "desc": model.get("description", ""),
            "caps": model.get("capabilities", []),
            "sizes": model.get("sizes", []),
            "pulls": model.get("pulls", ""),
            "tags": model.get("tags", ""),
            "updated": model.get("updated", "")
        }
        
        flattened["all_models_flat"].append(flat_model)
        
        # Categorize
        caps = model.get("capabilities", [])
        if "tools" in caps:
            flattened["categories"]["tools"].append(flat_model)
        if "vision" in caps:
            flattened["categories"]["vision"].append(flat_model)
        if "thinking" in caps:
            flattened["categories"]["thinking"].append(flat_model)
        if "embedding" in caps:
            flattened["categories"]["embedding"].append(flat_model)
        
        # Check for code-related models
        name_lower = model.get("name", "").lower()
        desc_lower = model.get("description", "").lower()
        if any(word in name_lower or word in desc_lower for word in ["code", "coder", "starcoder", "deepseek-coder"]):
            flattened["categories"]["code_analysis"].append(flat_model)
        
        # Check for reasoning models
        if any(word in name_lower or word in desc_lower for word in ["reasoning", "think", "wizard", "reflection"]):
            flattened["categories"]["reasoning"].append(flat_model)
        
        # If no specific category, add to general
        if not any(cap in ["tools", "vision", "thinking", "embedding"] for cap in caps) and \
           not any(word in name_lower or word in desc_lower for word in ["code", "coder", "reasoning", "think", "wizard", "reflection"]):
            flattened["categories"]["general"].append(flat_model)
        
        # Categorize by size
        sizes = model.get("sizes", [])
        max_size = 0
        for size in sizes:
            if size.endswith('b'):
                try:
                    num = float(size[:-1])
                    max_size = max(max_size, num)
                except:
                    pass
        
        if max_size <= 3:
            flattened["by_size"]["small_1b_3b"].append(flat_model)
        elif max_size <= 14:
            flattened["by_size"]["medium_7b_14b"].append(flat_model)
        elif max_size <= 70:
            flattened["by_size"]["large_27b_70b"].append(flat_model)
        else:
            flattened["by_size"]["xlarge_405b_plus"].append(flat_model)
    
    return flattened

def main():
    # Parse ollama list
    print("🔄 Parsing ollama_list.txt...")
    models = parse_ollama_list("tmp/ollama_list.txt")
    print(f"✅ Parsed {len(models)} models")
    
    # Read existing context
    print("🔄 Reading existing context...")
    with open("grok_consultations_series_2/updated_comprehensive_context.md", 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to JSON
    print("🔄 Converting context to JSON...")
    context_json = convert_md_to_json(md_content)
    
    # Create flattened models structure
    print("🔄 Creating flattened models structure...")
    flattened_models = create_flattened_models_structure(models)
    
    # Combine everything
    comprehensive_json = {
        "consultation_context": context_json,
        "ollama_models": {
            "raw_models": models,
            "flattened": flattened_models,
            "parsing_stats": {
                "total_parsed": len(models),
                "source_file": "tmp/ollama_list.txt",
                "source_lines": 2103,
                "parsing_timestamp": "2025-01-27"
            }
        },
        "project_context": {
            "name": "LLMStruct",
            "scale": "272 modules, 1857 functions, 183 classes",
            "hardware": "RTX 3060 Ti (8GB VRAM)",
            "budget_remaining": "$21.685",
            "goal": "Architectural analysis with Ollama model recommendations"
        },
        "request_summary": {
            "primary_goal": "Get Grok consultation on optimal Ollama model selection strategy",
            "alternatives": [
                "Original GPT-4.1 plan ($22, 1M context)",
                "Continued Grok series ($21.685, proven effective)",
                "Hybrid approach combining multiple models",
                "Self-analysis enhanced approach with LLMStruct AI"
            ],
            "key_question": "Which Ollama models are best for RTX 3060 Ti 8GB for LLMStruct architectural analysis?"
        }
    }
    
    # Save comprehensive JSON
    output_file = "grok_consultations_series_2/comprehensive_ollama_context.json"
    print(f"🔄 Saving comprehensive JSON to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_json, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully created comprehensive context JSON!")
    print(f"📊 Stats:")
    print(f"   - Context sections: {len(context_json['sections'])}")
    print(f"   - Total models: {len(models)}")
    print(f"   - Categories: {len(flattened_models['categories'])}")
    print(f"   - Top models by pulls: {len(flattened_models['top_by_pulls'])}")
    print(f"   - Output file: {output_file}")
    
    # Show some quick stats
    print("\n🎯 Quick Model Categories:")
    for cat, models_list in flattened_models["categories"].items():
        print(f"   - {cat}: {len(models_list)} models")
    
    print("\n📏 Size Distribution:")
    for size_cat, models_list in flattened_models["by_size"].items():
        print(f"   - {size_cat}: {len(models_list)} models")
    
    print(f"\n🏆 Top 5 Models by Pulls:")
    for i, model in enumerate(flattened_models["top_by_pulls"][:5]):
        print(f"   {i+1}. {model['name']}: {model['pulls']} pulls")

if __name__ == "__main__":
    main() 