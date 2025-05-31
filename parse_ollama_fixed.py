#!/usr/bin/env python3
"""
Fixed Ollama List Parser + Context Merger for Grok Consultation
Correctly parses the specific structure of ollama_list.txt
"""

import json
import re
from pathlib import Path

def parse_ollama_list_fixed(file_path):
    """Parse ollama_list.txt with correct understanding of structure"""
    models = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to get model blocks
    blocks = re.split(r'\n\s*\n', content)
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 2:  # Need at least name and description
            continue
        
        # Parse each block
        model = {
            "name": "",
            "description": "",
            "capabilities": [],
            "sizes": [],
            "pulls": "",
            "tags": "",
            "updated": ""
        }
        
        # First line is always the model name
        model["name"] = lines[0]
        
        # Skip if the "name" is actually a size or metadata
        if (model["name"].endswith('b') and any(c.isdigit() for c in model["name"])) or \
           model["name"].isdigit() or \
           model["name"].lower() in ['pulls', 'tags', 'updated']:
            continue
        
        i = 1
        
        # Second line is usually description (if it's not a capability)
        if i < len(lines) and lines[i] not in ["tools", "vision", "thinking", "embedding"] and \
           not lines[i].endswith('b') and not lines[i].endswith('M') and not lines[i].endswith('K'):
            model["description"] = lines[i]
            i += 1
        
        # Parse remaining lines
        while i < len(lines):
            line = lines[i]
            
            # Capabilities
            if line in ["tools", "vision", "thinking", "embedding"]:
                model["capabilities"].append(line)
                i += 1
                continue
            
            # Sizes (end with 'b' and contain digits or 'x')
            if line.endswith('b') and (any(c.isdigit() for c in line) or 'x' in line):
                model["sizes"].append(line)
                i += 1
                continue
            
            # Pulls count (ends with M or K and contains digits)
            if (line.endswith('M') or line.endswith('K')) and any(c.isdigit() for c in line):
                model["pulls"] = line
                i += 1
                # Skip "Pulls" if it's the next line
                if i < len(lines) and lines[i] == "Pulls":
                    i += 1
                continue
            
            # Tags count (pure number followed by "Tags")
            if line.isdigit() and i+1 < len(lines) and lines[i+1] == "Tags":
                model["tags"] = line
                i += 2  # Skip both number and "Tags"
                continue
            
            # Updated timestamp
            if line == "Updated" and i+1 < len(lines):
                model["updated"] = lines[i+1]
                i += 2
                continue
            
            # Skip any other lines
            i += 1
        
        # Only add models with proper names and some content
        if model["name"] and model["name"] not in ["Pulls", "Tags", "Updated"]:
            models.append(model)
    
    return models

def create_smart_categorization(models):
    """Create intelligent categorization with RTX 3060 Ti focus"""
    
    # Filter valid models
    valid_models = [m for m in models if m['name'] and len(m['name']) > 1]
    
    result = {
        "summary": {
            "total_valid_models": len(valid_models),
            "rtx3060ti_native": 0,
            "rtx3060ti_quantized": 0, 
            "requires_more_vram": 0
        },
        "categories": {
            "code_specialists": {
                "description": "Models specifically designed for code analysis, generation, and debugging",
                "models": [],
                "rtx3060ti_ready": []
            },
            "reasoning_experts": {
                "description": "Models with enhanced reasoning, thinking, and problem-solving capabilities", 
                "models": [],
                "rtx3060ti_ready": []
            },
            "vision_capable": {
                "description": "Multimodal models for diagrams, images, and visual content analysis",
                "models": [],
                "rtx3060ti_ready": []
            },
            "embedding_specialists": {
                "description": "Specialized models for text embeddings, semantic search, and RAG",
                "models": [],
                "rtx3060ti_ready": []
            },
            "general_purpose": {
                "description": "Versatile models for general tasks and conversations",
                "models": [],
                "rtx3060ti_ready": []
            }
        },
        "hardware_compatibility": {
            "rtx3060ti_native_8gb": [],     # ≤7B models
            "rtx3060ti_quantized_8gb": [],  # 8B-13B models (with quantization)
            "needs_more_vram": []           # >13B models
        },
        "top_recommendations": {
            "primary_code_analysis": [],
            "architectural_reasoning": [], 
            "documentation_vision": [],
            "semantic_search": []
        }
    }
    
    def parse_pulls_number(pulls_str):
        """Convert pulls string to number for sorting"""
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
    
    def get_max_size_gb(sizes):
        """Get maximum model size in GB"""
        max_size = 0
        for size in sizes:
            if size.endswith('b'):
                try:
                    if 'x' in size:  # MoE models like 8x7b
                        parts = size[:-1].split('x')
                        max_size = max(max_size, float(parts[-1]))
                    else:
                        max_size = max(max_size, float(size[:-1]))
                except:
                    pass
        return max_size
    
    # Process each model
    for model in valid_models:
        # Create compact representation
        compact = {
            "name": model["name"],
            "description": model["description"][:120] + "..." if len(model["description"]) > 120 else model["description"],
            "capabilities": model["capabilities"],
            "sizes": model["sizes"],
            "pulls": model["pulls"],
            "pulls_count": parse_pulls_number(model["pulls"]),
            "updated": model["updated"],
            "max_size_gb": get_max_size_gb(model["sizes"])
        }
        
        max_size = compact["max_size_gb"]
        
        # Hardware compatibility classification
        if max_size <= 7:
            result["hardware_compatibility"]["rtx3060ti_native_8gb"].append(compact)
            result["summary"]["rtx3060ti_native"] += 1
            rtx_compatible = True
        elif max_size <= 13:
            result["hardware_compatibility"]["rtx3060ti_quantized_8gb"].append(compact)
            result["summary"]["rtx3060ti_quantized"] += 1
            rtx_compatible = True
        else:
            result["hardware_compatibility"]["needs_more_vram"].append(compact)
            result["summary"]["requires_more_vram"] += 1
            rtx_compatible = False
        
        # Smart categorization
        name_lower = model["name"].lower()
        desc_lower = model["description"].lower()
        caps = model["capabilities"]
        
        # Code specialists
        if any(keyword in name_lower + " " + desc_lower for keyword in [
            "code", "coder", "coding", "deepseek-coder", "starcoder", "codellama", 
            "qwen2.5-coder", "devstral", "codestral", "codegemma", "programming",
            "codeqwen", "codegeex", "wizardcoder", "sqlcoder", "granite-code"
        ]):
            result["categories"]["code_specialists"]["models"].append(compact)
            if rtx_compatible:
                result["categories"]["code_specialists"]["rtx3060ti_ready"].append(compact)
                result["top_recommendations"]["primary_code_analysis"].append(compact)
        
        # Reasoning experts
        elif any(keyword in name_lower + " " + desc_lower for keyword in [
            "reasoning", "think", "thought", "wizard", "reflection", "openthinker", 
            "deepseek-r1", "qwq", "phi", "gemma", "mistral", "reasoning"
        ]) or "thinking" in caps:
            result["categories"]["reasoning_experts"]["models"].append(compact)
            if rtx_compatible:
                result["categories"]["reasoning_experts"]["rtx3060ti_ready"].append(compact)
                result["top_recommendations"]["architectural_reasoning"].append(compact)
        
        # Vision capable
        elif "vision" in caps or any(keyword in name_lower + " " + desc_lower for keyword in [
            "vision", "llava", "visual", "multimodal", "image", "minicpm-v", 
            "qwen2.5vl", "llama3.2-vision", "moondream"
        ]):
            result["categories"]["vision_capable"]["models"].append(compact)
            if rtx_compatible:
                result["categories"]["vision_capable"]["rtx3060ti_ready"].append(compact)
                result["top_recommendations"]["documentation_vision"].append(compact)
        
        # Embedding specialists
        elif "embedding" in caps or any(keyword in name_lower + " " + desc_lower for keyword in [
            "embed", "embedding", "semantic", "nomic-embed", "mxbai-embed", 
            "snowflake-arctic-embed", "all-minilm", "bge-"
        ]):
            result["categories"]["embedding_specialists"]["models"].append(compact)
            if rtx_compatible:
                result["categories"]["embedding_specialists"]["rtx3060ti_ready"].append(compact)
                result["top_recommendations"]["semantic_search"].append(compact)
        
        # General purpose
        else:
            result["categories"]["general_purpose"]["models"].append(compact)
            if rtx_compatible:
                result["categories"]["general_purpose"]["rtx3060ti_ready"].append(compact)
    
    # Sort recommendations by popularity and keep top 5 in each category
    for category in result["top_recommendations"]:
        result["top_recommendations"][category].sort(
            key=lambda x: x["pulls_count"], reverse=True
        )
        result["top_recommendations"][category] = result["top_recommendations"][category][:5]
    
    # Sort hardware compatibility by popularity
    for hw_category in result["hardware_compatibility"]:
        result["hardware_compatibility"][hw_category].sort(
            key=lambda x: x["pulls_count"], reverse=True
        )
    
    return result

def convert_md_to_json(md_content):
    """Convert markdown content to structured JSON"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = md_content.split('\n')
    
    for line in lines:
        if line.startswith('#'):
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = line.strip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return {
        "document_type": "comprehensive_context",
        "version": "2.2_fixed",
        "sections": sections,
        "raw_content": md_content
    }

def main():
    print("🔄 Parsing ollama_list.txt with FIXED algorithm...")
    models = parse_ollama_list_fixed("tmp/ollama_list.txt")
    print(f"✅ Parsed {len(models)} valid models")
    
    # Read existing context
    print("🔄 Reading existing context...")
    with open("grok_consultations_series_2/updated_comprehensive_context.md", 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to JSON
    print("🔄 Converting context to JSON...")
    context_json = convert_md_to_json(md_content)
    
    # Create smart categorization
    print("🔄 Creating smart categorization...")
    categorized_models = create_smart_categorization(models)
    
    # Show top model names to verify correctness
    print(f"\n✅ Sample model names (first 10):")
    for i, model in enumerate(models[:10]):
        print(f"   {i+1}. {model['name']}")
    
    # Combine everything
    comprehensive_json = {
        "consultation_context": context_json,
        "ollama_analysis": {
            "parsing_info": {
                "total_parsed": len(models),
                "source_file": "tmp/ollama_list.txt",
                "parsing_algorithm": "fixed_structure_aware",
                "timestamp": "2025-01-27_fixed",
                "validation": "no_size_names_as_models"
            },
            "models_data": categorized_models,
            "quality_metrics": {
                "rtx3060ti_native": categorized_models["summary"]["rtx3060ti_native"],
                "rtx3060ti_quantized": categorized_models["summary"]["rtx3060ti_quantized"],
                "total_rtx_compatible": categorized_models["summary"]["rtx3060ti_native"] + categorized_models["summary"]["rtx3060ti_quantized"],
                "code_specialists": len(categorized_models["categories"]["code_specialists"]["models"]),
                "reasoning_experts": len(categorized_models["categories"]["reasoning_experts"]["models"]),
                "vision_capable": len(categorized_models["categories"]["vision_capable"]["models"]),
                "embedding_specialists": len(categorized_models["categories"]["embedding_specialists"]["models"])
            }
        },
        "project_context": {
            "name": "LLMStruct",
            "scale": "272 modules, 1857 functions, 183 classes",
            "hardware": "RTX 3060 Ti (8GB VRAM)",
            "budget_remaining": "$21.685",
            "goal": "Architectural analysis with optimal Ollama model recommendations"
        },
        "grok_consultation_request": {
            "primary_question": "Which specific Ollama models are optimal for LLMStruct architectural analysis on RTX 3060 Ti 8GB?",
            "strategic_options": [
                "Original GPT-4.1 plan ($22, 1M context) - single high-end model approach",
                "Continued Grok series ($21.685, proven effective) - expert consultation approach", 
                "Hybrid: Strategic Grok + Local Ollama pipeline - best of both worlds",
                "Self-analysis enhanced: LLMStruct AI + Ollama specialists - leverage existing capabilities"
            ],
            "specific_requirements": [
                "Analyze 272 Python modules automatically",
                "Generate architectural documentation with diagrams", 
                "Consolidate 8 different bot versions into coherent system",
                "Create implementation roadmap with concrete next steps",
                "Leverage existing struct.json knowledge base (1.2MB)",
                "Use existing AI self-awareness and context orchestration systems"
            ],
            "constraints_and_assets": [
                "Hardware: RTX 3060 Ti 8GB VRAM limitation",
                "Budget: $21.685 remaining from original $22",
                "Time: Need production-ready outputs, not experiments",
                "Assets: LLMStruct already has SystemCapabilityDiscovery, Context Orchestrator, Metrics tracking",
                "Goal: Maximum architectural insight with optimal resource utilization"
            ]
        }
    }
    
    # Save fixed JSON
    output_file = "grok_consultations_series_2/fixed_ollama_context.json"
    print(f"🔄 Saving FIXED JSON to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_json, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully created FIXED context JSON!")
    print(f"\n📊 Quality Analysis:")
    print(f"   - Total valid models: {len(models)}")
    print(f"   - RTX 3060 Ti native (≤7B): {categorized_models['summary']['rtx3060ti_native']}")
    print(f"   - RTX 3060 Ti quantized (8-13B): {categorized_models['summary']['rtx3060ti_quantized']}")
    print(f"   - Total RTX compatible: {categorized_models['summary']['rtx3060ti_native'] + categorized_models['summary']['rtx3060ti_quantized']}")
    print(f"   - Code specialists: {len(categorized_models['categories']['code_specialists']['models'])}")
    print(f"   - Reasoning experts: {len(categorized_models['categories']['reasoning_experts']['models'])}")
    print(f"   - Vision capable: {len(categorized_models['categories']['vision_capable']['models'])}")
    print(f"   - Embedding specialists: {len(categorized_models['categories']['embedding_specialists']['models'])}")
    
    print(f"\n🎯 Top RTX 3060 Ti Recommendations:")
    for category, models_list in categorized_models["top_recommendations"].items():
        if models_list:
            print(f"   {category}:")
            for model in models_list[:3]:
                print(f"     - {model['name']} ({model['max_size_gb']}GB max, {model['pulls']} pulls)")
    
    print(f"\n📄 Output: {output_file}")
    print(f"🎉 Ready for Grok consultation with properly parsed models!")

if __name__ == "__main__":
    main() 