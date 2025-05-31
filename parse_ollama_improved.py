#!/usr/bin/env python3
"""
Improved Ollama List Parser + Context Merger for Grok Consultation
Better parsing algorithm for ollama_list.txt structure
"""

import json
import re
from pathlib import Path

def parse_ollama_list_improved(file_path):
    """Parse ollama_list.txt with improved algorithm"""
    models = []
    current_model = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to separate model blocks
    blocks = content.split('\n\n')
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
        
        # First line is model name
        model_name = lines[0]
        
        # Skip if it's just metadata without model name
        if model_name.lower() in ['pulls', 'tags', 'updated'] or model_name.isdigit():
            continue
        
        model = {
            "name": model_name,
            "description": "",
            "capabilities": [],
            "sizes": [],
            "pulls": "",
            "tags": "",
            "updated": ""
        }
        
        # Process remaining lines
        i = 1
        while i < len(lines):
            line = lines[i]
            
            # Check for description (usually second line if it's not a capability/size)
            if i == 1 and line not in ["tools", "vision", "thinking", "embedding"] and not line.endswith("b") and not line.endswith("M") and not line.endswith("K"):
                model["description"] = line
                i += 1
                continue
            
            # Check for capabilities
            if line in ["tools", "vision", "thinking", "embedding"]:
                model["capabilities"].append(line)
                i += 1
                continue
            
            # Check for sizes (lines ending with 'b' and containing numbers/x)
            if line.endswith("b") and (any(c.isdigit() for c in line) or 'x' in line):
                model["sizes"].append(line)
                i += 1
                continue
            
            # Check for pulls count
            if (line.endswith("M") or line.endswith("K")) and any(c.isdigit() for c in line):
                model["pulls"] = line
                i += 1
                # Skip "Pulls" line if it exists
                if i < len(lines) and lines[i] == "Pulls":
                    i += 1
                continue
            
            # Check for tags count
            if line.isdigit() and i+1 < len(lines) and lines[i+1] == "Tags":
                model["tags"] = line
                i += 2  # Skip "Tags" line
                continue
            
            # Check for updated info
            if line == "Updated" and i+1 < len(lines):
                model["updated"] = lines[i+1]
                i += 2
                continue
            
            i += 1
        
        models.append(model)
    
    return models

def create_better_flattened_structure(models):
    """Create an improved flattened structure for LLM consumption"""
    
    # Filter out models with proper names (not just metadata)
    valid_models = [m for m in models if m['name'] and m['name'] not in ['tools', 'vision', 'thinking', 'embedding'] and not m['name'].isdigit()]
    
    flattened = {
        "summary": {
            "total_models": len(valid_models),
            "rtx3060ti_compatible": 0,  # Will calculate
            "top_categories": ["code_analysis", "reasoning", "vision", "embedding", "general"]
        },
        "categories": {
            "code_analysis": {
                "description": "Models specifically designed for code analysis, generation, and debugging",
                "models": []
            },
            "reasoning": {
                "description": "Models with enhanced reasoning and thinking capabilities",
                "models": []
            },
            "vision": {
                "description": "Multimodal models capable of processing images and diagrams",
                "models": []
            },
            "embedding": {
                "description": "Specialized models for text embeddings and semantic search",
                "models": []
            },
            "general": {
                "description": "General-purpose language models for various tasks",
                "models": []
            }
        },
        "by_hardware_compatibility": {
            "rtx3060ti_8gb": [],
            "rtx3060ti_8gb_quantized": [],
            "requires_more_vram": []
        },
        "top_models_by_popularity": [],
        "recommended_for_llmstruct": {
            "primary_code_analysis": [],
            "secondary_reasoning": [],
            "embedding_search": [],
            "vision_diagrams": []
        }
    }
    
    # Parse pulls for sorting
    def parse_pulls(pulls_str):
        if not pulls_str:
            return 0
        try:
            if pulls_str.endswith('M'):
                return float(pulls_str[:-1]) * 1000000
            elif pulls_str.endswith('K'):
                return float(pulls_str[:-1]) * 1000
            return float(pulls_str)
        except:
            return 0
    
    # Sort by popularity
    sorted_models = sorted(valid_models, key=lambda x: parse_pulls(x.get('pulls', '0')), reverse=True)
    flattened["top_models_by_popularity"] = sorted_models[:15]
    
    for model in valid_models:
        # Create compact model representation
        compact_model = {
            "name": model["name"],
            "desc": model["description"][:100] + "..." if len(model["description"]) > 100 else model["description"],
            "caps": model["capabilities"],
            "sizes": model["sizes"],
            "pulls": model["pulls"],
            "updated": model["updated"]
        }
        
        # Determine max size for hardware compatibility
        max_size_gb = 0
        for size in model["sizes"]:
            if size.endswith('b'):
                try:
                    if 'x' in size:  # Handle MoE models like 16x17b
                        parts = size[:-1].split('x')
                        max_size_gb = max(max_size_gb, float(parts[-1]))
                    else:
                        max_size_gb = max(max_size_gb, float(size[:-1]))
                except:
                    pass
        
        # Hardware compatibility (rough estimates for 8GB VRAM)
        if max_size_gb <= 7:  # Can run comfortably
            flattened["by_hardware_compatibility"]["rtx3060ti_8gb"].append(compact_model)
            flattened["summary"]["rtx3060ti_compatible"] += 1
        elif max_size_gb <= 13:  # Can run with quantization
            flattened["by_hardware_compatibility"]["rtx3060ti_8gb_quantized"].append(compact_model)
            flattened["summary"]["rtx3060ti_compatible"] += 1
        else:
            flattened["by_hardware_compatibility"]["requires_more_vram"].append(compact_model)
        
        # Categorize by purpose
        name_lower = model["name"].lower()
        desc_lower = model["description"].lower()
        caps = model["capabilities"]
        
        # Code analysis models
        if any(word in name_lower + " " + desc_lower for word in [
            "code", "coder", "deepseek-coder", "starcoder", "codellama", 
            "qwen2.5-coder", "devstral", "programming"
        ]):
            flattened["categories"]["code_analysis"]["models"].append(compact_model)
            if max_size_gb <= 13:  # RTX 3060 Ti compatible
                flattened["recommended_for_llmstruct"]["primary_code_analysis"].append(compact_model)
        
        # Reasoning models
        elif any(word in name_lower + " " + desc_lower for word in [
            "reasoning", "think", "wizard", "reflection", "openthinker", "deepseek-r1"
        ]) or "thinking" in caps:
            flattened["categories"]["reasoning"]["models"].append(compact_model)
            if max_size_gb <= 13:
                flattened["recommended_for_llmstruct"]["secondary_reasoning"].append(compact_model)
        
        # Vision models
        elif "vision" in caps or any(word in name_lower + " " + desc_lower for word in [
            "vision", "llava", "visual", "multimodal", "image"
        ]):
            flattened["categories"]["vision"]["models"].append(compact_model)
            if max_size_gb <= 13:
                flattened["recommended_for_llmstruct"]["vision_diagrams"].append(compact_model)
        
        # Embedding models
        elif "embedding" in caps or any(word in name_lower + " " + desc_lower for word in [
            "embed", "embedding", "semantic", "nomic-embed"
        ]):
            flattened["categories"]["embedding"]["models"].append(compact_model)
            flattened["recommended_for_llmstruct"]["embedding_search"].append(compact_model)
        
        # General models
        else:
            flattened["categories"]["general"]["models"].append(compact_model)
    
    # Sort recommendations by popularity within each category
    for category in flattened["recommended_for_llmstruct"]:
        flattened["recommended_for_llmstruct"][category].sort(
            key=lambda x: parse_pulls(x.get('pulls', '0')), reverse=True
        )
        # Keep top 5 in each category
        flattened["recommended_for_llmstruct"][category] = flattened["recommended_for_llmstruct"][category][:5]
    
    return flattened

def convert_md_to_json(md_content):
    """Convert markdown content to structured JSON"""
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
        "version": "2.1",
        "sections": sections,
        "raw_content": md_content
    }

def main():
    print("🔄 Parsing ollama_list.txt with improved algorithm...")
    models = parse_ollama_list_improved("tmp/ollama_list.txt")
    print(f"✅ Parsed {len(models)} models")
    
    # Filter valid models
    valid_models = [m for m in models if m['name'] and m['name'] not in ['tools', 'vision', 'thinking', 'embedding'] and not m['name'].isdigit()]
    print(f"✅ {len(valid_models)} valid models found")
    
    # Read existing context
    print("🔄 Reading existing context...")
    with open("grok_consultations_series_2/updated_comprehensive_context.md", 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to JSON
    print("🔄 Converting context to JSON...")
    context_json = convert_md_to_json(md_content)
    
    # Create improved flattened structure
    print("🔄 Creating improved flattened structure...")
    flattened_models = create_better_flattened_structure(models)
    
    # Combine everything
    comprehensive_json = {
        "consultation_context": context_json,
        "ollama_analysis": {
            "parsing_info": {
                "total_parsed": len(models),
                "valid_models": len(valid_models),
                "source_file": "tmp/ollama_list.txt",
                "parsing_algorithm": "improved_block_based",
                "timestamp": "2025-01-27"
            },
            "models_data": flattened_models,
            "quick_stats": {
                "rtx3060ti_compatible": flattened_models["summary"]["rtx3060ti_compatible"],
                "code_analysis_models": len(flattened_models["categories"]["code_analysis"]["models"]),
                "reasoning_models": len(flattened_models["categories"]["reasoning"]["models"]),
                "vision_models": len(flattened_models["categories"]["vision"]["models"]),
                "embedding_models": len(flattened_models["categories"]["embedding"]["models"])
            }
        },
        "project_context": {
            "name": "LLMStruct",
            "scale": "272 modules, 1857 functions, 183 classes",
            "hardware": "RTX 3060 Ti (8GB VRAM)",
            "budget_remaining": "$21.685",
            "goal": "Architectural analysis with Ollama model recommendations"
        },
        "grok_consultation_request": {
            "primary_question": "Which specific Ollama models should we use for LLMStruct architectural analysis on RTX 3060 Ti?",
            "strategy_options": [
                "Original GPT-4.1 plan ($22, 1M context)",
                "Continued Grok series ($21.685, proven effective)", 
                "Hybrid approach: Strategic Grok + Local Ollama implementation",
                "Self-analysis enhanced with LLMStruct AI + Ollama support"
            ],
            "specific_needs": [
                "Code analysis for 272 modules",
                "Architectural documentation generation", 
                "Bot consolidation strategy (8 versions)",
                "Implementation roadmap with diagrams"
            ],
            "constraints": [
                "RTX 3060 Ti 8GB VRAM limit",
                "Budget: $21.685 remaining",
                "Need production-ready outputs",
                "Leverage existing LLMStruct AI capabilities"
            ]
        }
    }
    
    # Save improved JSON
    output_file = "grok_consultations_series_2/improved_ollama_context.json"
    print(f"🔄 Saving improved JSON to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_json, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully created improved context JSON!")
    print(f"\n📊 Analysis Results:")
    print(f"   - Valid models parsed: {len(valid_models)}")
    print(f"   - RTX 3060 Ti compatible: {flattened_models['summary']['rtx3060ti_compatible']}")
    print(f"   - Code analysis models: {len(flattened_models['categories']['code_analysis']['models'])}")
    print(f"   - Reasoning models: {len(flattened_models['categories']['reasoning']['models'])}")
    print(f"   - Vision models: {len(flattened_models['categories']['vision']['models'])}")
    print(f"   - Embedding models: {len(flattened_models['categories']['embedding']['models'])}")
    
    print(f"\n🎯 Top RTX 3060 Ti Recommendations:")
    for category, models_list in flattened_models["recommended_for_llmstruct"].items():
        if models_list:
            print(f"   {category}:")
            for model in models_list[:3]:
                print(f"     - {model['name']}: {model['pulls']} pulls")
    
    print(f"\n📄 Output: {output_file}")

if __name__ == "__main__":
    main() 