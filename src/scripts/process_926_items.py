#!/usr/bin/env python3
"""
926 Items Processing Script - Updated Implementation
Processes items according to GitHub roadmap + personal management vision
Implements all decisions from 926_items_processing_execution_plan.md
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re

class TaskProcessor926:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.results_path = self.base_path / "processing_results"
        self.results_path.mkdir(exist_ok=True)
        
        # Date suffix for all files
        self.date_suffix = datetime.now().strftime("%Y-%m-%d")
        
        # Updated output file structure per execution plan
        self.output_files = {
            "github_issues": f"github_issues_{self.date_suffix}.json",
            "github_epics": f"github_epics_{self.date_suffix}.json", 
            "github_discussions": f"github_discussions_{self.date_suffix}.json",
            "personal_management": f"personal_management_{self.date_suffix}.json",
            "personal_tools": f"personal_tools_{self.date_suffix}.json",
            "personal_learning": f"personal_learning_{self.date_suffix}.json",
            "t_pot_revenue": f"t_pot_revenue_{self.date_suffix}.json",
            "future_backlog": f"future_backlog_{self.date_suffix}.json",
            "duplicates_review": f"duplicates_review_{self.date_suffix}.json",
            "conflicts_manual": f"conflicts_manual_{self.date_suffix}.json"
        }
        
        # Initialize categories
        self.categories = {key: [] for key in self.output_files.keys()}
        self.stats = {
            "total_items": 0,
            "processed": 0,
            "categories": {key: 0 for key in self.output_files.keys()},
            "confidence_scores": {"high": 0, "medium": 0, "low": 0},
            "t_pot_duplicates": 0,
            "processing_time": None
        }
        
        # Processing parameters from execution plan
        self.confidence_threshold = 90  # 90% for auto-categorization
        self.similarity_threshold = 0.8  # 80% for duplicates
        
    def load_comprehensive_index(self) -> List[Dict]:
        """Load the 926 items from comprehensive index"""
        index_path = self.base_path / "docs" / "COMPREHENSIVE_INDEX.json"
        
        if not index_path.exists():
            print(f"❌ COMPREHENSIVE_INDEX.json not found at {index_path}")
            return []
            
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract items from the comprehensive index structure
        items = []
        seen_items = set()  # Track duplicates by content hash
        
        if isinstance(data, dict):
            # Handle different possible structures
            if "revolutionary_innovations" in data:
                items.extend(data["revolutionary_innovations"])
            
            # Look for other item lists in the structure
            for key, value in data.items():
                if key in ["items", "tasks", "ideas", "concepts"] and isinstance(value, list):
                    items.extend(value)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    # Check if this looks like an item list
                    if any(field in value[0] for field in ["id", "title", "description"]):
                        for item in value:
                            if isinstance(item, dict):
                                item['source_category'] = key
                                items.append(item)
                elif isinstance(value, dict):
                    # Handle nested structure
                    for subkey, subitems in value.items():
                        if isinstance(subitems, list) and subitems:
                            for item in subitems:
                                if isinstance(item, dict):
                                    item['source_category'] = f"{key}/{subkey}"
                                    items.append(item)
        elif isinstance(data, list):
            items = data
        
        # Deduplicate items by content similarity
        unique_items = []
        for item in items:
            # Create content hash for deduplication
            item_content = str(item.get('title', '')) + str(item.get('description', ''))
            content_hash = hash(item_content.lower().strip())
            
            if content_hash not in seen_items:
                seen_items.add(content_hash)
                unique_items.append(item)
        
        duplicates_removed = len(items) - len(unique_items)
        if duplicates_removed > 0:
            print(f"🔄 Removed {duplicates_removed} duplicate items during loading")
            
        print(f"📊 Loaded {len(unique_items)} unique items from comprehensive index")
        return unique_items

    def calculate_confidence_score(self, item: Dict, category: str) -> float:
        """Calculate confidence score for categorization decision"""
        confidence = 50.0  # Base confidence
        content = str(item).lower()
        
        # T-Pot related items have high confidence
        if self.check_t_pot_related(item):
            confidence += 40
            
        # Clear indicators boost confidence
        category_keywords = {
            "github_issues": ["implement", "fix", "add", "create", "task", "issue"],
            "github_epics": ["epic", "feature", "milestone", "large", "complex"],
            "github_discussions": ["discuss", "decision", "architecture", "consensus"],
            "personal_management": ["manage", "strategy", "planning", "coordinate"],
            "personal_tools": ["tool", "automation", "productivity", "dashboard"],
            "personal_learning": ["learning", "skill", "study", "research"],
            "future_backlog": ["future", "someday", "later", "backlog"]
        }
        
        if category in category_keywords:
            keyword_matches = sum(1 for keyword in category_keywords[category] if keyword in content)
            confidence += keyword_matches * 10
            
        # Status and priority influence confidence
        status = item.get('status', '').lower()
        if status in ['planned', 'in_progress', 'ready']:
            confidence += 15
            
        priority = item.get('priority', '').lower()
        if priority in ['high', 'critical']:
            confidence += 10
            
        return min(confidence, 100.0)

    def check_t_pot_related(self, item: Dict) -> bool:
        """Enhanced T-Pot detection"""
        content = str(item).lower()
        t_pot_keywords = [
            't-pot', 'tpot', 'honeypot', 'deployment', 'security monitoring',
            'elk stack', 'docker-compose', 'security', 'monitoring', 'threat'
        ]
        return any(keyword in content for keyword in t_pot_keywords)

    def check_team_implementable(self, item: Dict) -> bool:
        """Check if team can implement without architecture review"""
        content = str(item).lower()
        
        # Autonomous implementable indicators
        autonomous_keywords = [
            'fix bug', 'add validation', 'update ui', 'format code',
            'add tests', 'documentation', 'refactor', 'optimize'
        ]
        
        # Requires architecture review
        architecture_keywords = [
            'api design', 'architecture', 'core module', 'system design',
            'database schema', 'security model', 'integration'
        ]
        
        autonomous_score = sum(1 for kw in autonomous_keywords if kw in content)
        architecture_score = sum(1 for kw in architecture_keywords if kw in content)
        
        return autonomous_score > architecture_score

    def check_personal_vs_team_vs_business(self, item: Dict) -> str:
        """Classify as personal/team/business"""
        content = str(item).lower()
        file_path = item.get('file_path', '').lower()
        
        # Personal indicators
        personal_keywords = [
            'personal', 'learning', 'skill development', 'education',
            'private', 'individual', 'self-improvement'
        ]
        
        # Business indicators  
        business_keywords = [
            'revenue', 'monetization', 'business', 'strategy', 'commercial',
            'partnership', 'investment', 'market', 'customer'
        ]
        
        # Team indicators
        team_keywords = [
            'team', 'collaboration', 'workflow', 'development',
            'implementation', 'coding', 'feature', 'technical'
        ]
        
        personal_score = sum(1 for kw in personal_keywords if kw in content)
        business_score = sum(1 for kw in business_keywords if kw in content)  
        team_score = sum(1 for kw in team_keywords if kw in content)
        
        # File path indicators
        if '.personal/' in file_path:
            personal_score += 2
            
        if personal_score > max(business_score, team_score):
            return 'personal'
        elif business_score > team_score:
            return 'business'
        else:
            return 'team'

    def identify_epic_candidates(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify items that should be grouped into epics"""
        epic_groups = {}
        
        for item in items:
            content = str(item).lower()
            title = item.get('title', '').lower()
            
            # Look for epic indicators
            if any(word in content for word in ['epic', 'feature', 'milestone', 'large']):
                # Extract potential epic name
                epic_name = self.extract_epic_name(item)
                if epic_name not in epic_groups:
                    epic_groups[epic_name] = []
                epic_groups[epic_name].append(item)
                
        # Filter groups with 3+ items (per execution plan)
        return {name: items for name, items in epic_groups.items() if len(items) >= 3}

    def extract_epic_name(self, item: Dict) -> str:
        """Extract epic name from item"""
        title = item.get('title', '')
        
        # Simple extraction - use first meaningful words
        words = title.split()[:3]
        return '_'.join(words).lower().replace(':', '').replace('-', '_')

    def categorize_item(self, item: Dict) -> Tuple[str, float]:
        """Main categorization logic with confidence scoring"""
        
        # T-Pot priority override (завтрашний deadline)
        if self.check_t_pot_related(item):
            confidence = self.calculate_confidence_score(item, "t_pot_revenue")
            return "t_pot_revenue", confidence
            
        # Personal vs Team vs Business classification
        scope = self.check_personal_vs_team_vs_business(item)
        
        if scope == 'personal':
            # Further classify personal items
            content = str(item).lower()
            if any(word in content for word in ['manage', 'strategy', 'coordinate']):
                category = "personal_management"
            elif any(word in content for word in ['tool', 'automation', 'productivity']):
                category = "personal_tools"  
            else:
                category = "personal_learning"
        else:
            # Team/Business items go to GitHub categories
            content = str(item).lower()
            
            if any(word in content for word in ['discuss', 'decision', 'architecture']):
                category = "github_discussions"
            elif any(word in content for word in ['epic', 'milestone', 'large feature']):
                category = "github_epics"
            elif self.check_team_implementable(item):
                category = "github_issues"
            else:
                # Default for unclear items
                category = "future_backlog"
                
        confidence = self.calculate_confidence_score(item, category)
        return category, confidence

    def find_duplicates(self, items: List[Dict]) -> List[Dict]:
        """Enhanced duplicate detection with T-Pot special handling"""
        duplicates = []
        seen_items = {}
        
        for item in items:
            title = item.get('title', '').strip().lower()
            if not title:
                continue
                
            # Check for similar titles
            for seen_title, seen_item in seen_items.items():
                similarity = self.calculate_similarity(title, seen_title)
                if similarity > self.similarity_threshold:
                    
                    # Special handling for T-Pot items
                    is_t_pot_duplicate = (
                        self.check_t_pot_related(item) and 
                        self.check_t_pot_related(seen_item)
                    )
                    
                    duplicate_entry = {
                        'item1': seen_item,
                        'item2': item,
                        'similarity': similarity,
                        'merge_strategy': self.suggest_merge_strategy(seen_item, item),
                        't_pot_duplicate': is_t_pot_duplicate,
                        'requires_manual_review': similarity < 0.95
                    }
                    
                    duplicates.append(duplicate_entry)
                    
                    if is_t_pot_duplicate:
                        self.stats["t_pot_duplicates"] += 1
                    
                    break
            else:
                seen_items[title] = item
                
        return duplicates

    def calculate_similarity(self, title1: str, title2: str) -> float:
        """Enhanced similarity calculation"""
        # Word overlap similarity
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard = len(intersection) / len(union)
        
        # Boost for identical key terms
        key_terms = ['t-pot', 'epic', 'feature', 'ai', 'self-awareness']
        key_term_boost = 0
        for term in key_terms:
            if term in title1 and term in title2:
                key_term_boost += 0.1
                
        return min(jaccard + key_term_boost, 1.0)

    def suggest_merge_strategy(self, item1: Dict, item2: Dict) -> str:
        """Enhanced merge strategy with T-Pot consideration"""
        # For T-Pot items, always prefer more detailed version
        if self.check_t_pot_related(item1) and self.check_t_pot_related(item2):
            content1_len = len(str(item1.get('description', '')))
            content2_len = len(str(item2.get('description', '')))
            return "keep_detailed_t_pot" if content2_len > content1_len else "keep_simple_t_pot"
            
        # Date-based strategy
        date1 = item1.get('created_date', item1.get('modified_date', ''))
        date2 = item2.get('created_date', item2.get('modified_date', ''))
        
        if date1 and date2:
            return "keep_newer" if date2 > date1 else "keep_older"
            
        return "manual_review"

    def process_items(self, items: List[Dict]) -> Dict:
        """Main processing workflow implementing execution plan"""
        self.stats["total_items"] = len(items)
        start_time = datetime.now()
        
        print("🔄 Phase 1: Load & Parse - Complete")
        
        print("🔄 Phase 2: Categorization...")
        
        # Find duplicates first (Phase 3)
        print("🔄 Phase 3: Duplication Processing...")
        duplicates = self.find_duplicates(items)
        duplicate_item_ids = set()
        
        # Process duplicates
        for dup in duplicates:
            self.categories["duplicates_review"].append(dup)
            duplicate_item_ids.add(id(dup['item1']))
            duplicate_item_ids.add(id(dup['item2']))
        
        print(f"   Found {len(duplicates)} duplicate pairs")
        
        # Process unique items
        epic_candidates = {}
        low_confidence_items = []
        
        for item in items:
            if id(item) in duplicate_item_ids:
                continue  # Skip items that are duplicates
                
            category, confidence = self.categorize_item(item)
            
            # Enhanced item with new fields per execution plan
            processed_item = {
                **item,
                "processing_metadata": {
                    "category_assigned": category,
                    "processed_at": datetime.now().isoformat(),
                    "confidence_score": confidence,
                    "changelog_entry": f"{self.date_suffix}: Categorized for GitHub roadmap",
                    
                    # GitHub integration fields
                    "github_ready": category.startswith('github_'),
                    "team_implementable": self.check_team_implementable(item),
                    "requires_architecture_review": not self.check_team_implementable(item),
                    
                    # T-Pot duplication tracking
                    "t_pot_related": self.check_t_pot_related(item),
                    "duplicate_in_categories": [],
                    
                    # Sessions integration fields
                    "session_format_ready": category in ['github_epics', 'github_discussions'],
                    "epic_candidate": any(word in str(item).lower() for word in ['epic', 'feature', 'milestone']),
                    "epic_group": self.extract_epic_name(item) if category == 'github_epics' else None
                }
            }
            
            # Handle T-Pot duplication strategy
            if self.check_t_pot_related(item):
                # Add to t_pot_revenue (main)
                self.categories["t_pot_revenue"].append(processed_item)
                self.stats["categories"]["t_pot_revenue"] += 1
                
                # Also add cross-reference to relevant category if not t_pot_revenue
                if category != "t_pot_revenue":
                    cross_ref_item = processed_item.copy()
                    cross_ref_item["processing_metadata"]["duplicate_in_categories"] = ["t_pot_revenue"]
                    cross_ref_item["processing_metadata"]["is_cross_reference"] = True
                    
                    self.categories[category].append(cross_ref_item)
                    self.stats["categories"][category] += 1
            else:
                # Regular categorization
                if confidence >= self.confidence_threshold:
                    self.categories[category].append(processed_item)
                    self.stats["categories"][category] += 1
                else:
                    # Low confidence items go to manual review
                    low_confidence_items.append({
                        "item": processed_item,
                        "suggested_category": category,
                        "confidence": confidence,
                        "reason": "Below confidence threshold"
                    })
            
            # Track confidence distribution
            if confidence >= 90:
                self.stats["confidence_scores"]["high"] += 1
            elif confidence >= 70:
                self.stats["confidence_scores"]["medium"] += 1
            else:
                self.stats["confidence_scores"]["low"] += 1
                
            self.stats["processed"] += 1
        
        # Add low confidence items to manual review
        self.categories["conflicts_manual"].extend(low_confidence_items)
        self.stats["categories"]["conflicts_manual"] += len(low_confidence_items)
        
        print("🔄 Phase 4: GitHub Integration Prep...")
        # Epic grouping (implement epic candidate logic)
        
        print("🔄 Phase 5: Output Generation...")
        
        end_time = datetime.now()
        self.stats["processing_time"] = (end_time - start_time).total_seconds()
        
        return self.stats

    def save_results(self):
        """Save categorized results with enhanced metadata"""
        timestamp = datetime.now().isoformat()
        
        # Save each category file
        for category, filename in self.output_files.items():
            output_path = self.results_path / filename
            
            # Enhanced metadata per execution plan
            result_data = {
                "metadata": {
                    "category": category,
                    "processed_at": timestamp,
                    "total_items": len(self.categories[category]),
                    "confidence_level": self.confidence_threshold,
                    "description": self.get_category_description(category),
                    
                    # Cross-references for T-Pot duplication strategy
                    "cross_references": {
                        "t_pot_duplicates": [item.get("id") for item in self.categories[category] 
                                           if item.get("processing_metadata", {}).get("t_pot_related")],
                        "dependencies": [],  # Future use
                        "related_categories": []  # Future use
                    },
                    
                    # Processing statistics
                    "processing_stats": {
                        "auto_categorized": sum(1 for item in self.categories[category] 
                                              if item.get("processing_metadata", {}).get("confidence_score", 0) >= 90),
                        "manual_reviewed": sum(1 for item in self.categories[category] 
                                             if item.get("processing_metadata", {}).get("confidence_score", 0) < 90),
                        "github_ready_items": sum(1 for item in self.categories[category] 
                                          if item.get("processing_metadata", {}).get("github_ready", False))
                    }
                },
                "items": self.categories[category]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Saved {len(self.categories[category])} items to {filename}")

        # Enhanced processing summary
        summary_path = self.results_path / f"processing_summary_{self.date_suffix}.json"
        summary = {
            "processing_metadata": {
                "timestamp": timestamp,
                "execution_plan": "926_items_processing_execution_plan.md",
                "total_items_processed": self.stats["total_items"],
                "categories_created": len(self.output_files),
                "processing_script": __file__,
                "confidence_threshold": self.confidence_threshold,
                "similarity_threshold": self.similarity_threshold
            },
            "statistics": self.stats,
            "success_metrics": {
                "processing_speed_seconds": self.stats["processing_time"],
                "categorization_accuracy": f"{(self.stats['confidence_scores']['high'] / self.stats['processed'] * 100):.1f}%",
                "auto_decisions_percent": f"{(self.stats['confidence_scores']['high'] / self.stats['processed'] * 100):.1f}%",
                "github_ready_items": sum(self.stats["categories"][cat] for cat in 
                                        ["github_issues", "github_epics", "github_discussions"])
            },
            "file_structure": {
                category: {
                    "filename": filename,
                    "count": self.stats["categories"][category],
                    "description": self.get_category_description(category)
                }
                for category, filename in self.output_files.items()
            }
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        print(f"📊 Processing summary saved to processing_summary_{self.date_suffix}.json")

    def get_category_description(self, category: str) -> str:
        """Category descriptions per execution plan"""
        descriptions = {
            "github_issues": "Tasks для команды - 100% автономная реализация",
            "github_epics": "Major features/milestones - 3+ связанных issues",
            "github_discussions": "Технические обсуждения, consensus required",
            "personal_management": "Управленческие задачи (приватно)",
            "personal_tools": "Инструменты управления проектом",
            "personal_learning": "Личное развитие",
            "t_pot_revenue": "T-Pot отдельный revenue track (приоритет)",
            "future_backlog": "Хорошие идеи на потом",
            "duplicates_review": "Дубликаты для ручного разбора",
            "conflicts_manual": "Manual review required (<90% confidence)"
        }
        return descriptions.get(category, "Unknown category")

    def run(self):
        """Main execution workflow per execution plan"""
        print("🚀 Starting 926 items processing - Execution Plan Implementation")
        print(f"📅 Date: {self.date_suffix}")
        print(f"🎯 Confidence threshold: {self.confidence_threshold}%")
        print(f"🔍 Similarity threshold: {self.similarity_threshold * 100}%")
        
        # Load items
        items = self.load_comprehensive_index()
        if not items:
            print("❌ No items to process")
            return
            
        # Process items through decision framework
        print("🔄 Processing items through decision framework...")
        stats = self.process_items(items)
        
        # Save results
        print("💾 Saving categorized results...")
        self.save_results()
        
        # Report results per execution plan success metrics
        print("\n✅ PROCESSING COMPLETE!")
        print(f"⏱️  Processing time: {stats['processing_time']:.1f} seconds")
        print(f"📊 Processed: {stats['processed']}/{stats['total_items']} items")
        print(f"🎯 T-Pot duplicates handled: {stats['t_pot_duplicates']}")
        
        print(f"\n📁 File distribution:")
        for category, count in stats['categories'].items():
            filename = self.output_files[category]
            print(f"   {filename}: {count} items")
            
        print(f"\n📈 Confidence distribution:")
        print(f"   High (≥90%): {stats['confidence_scores']['high']} items")
        print(f"   Medium (70-89%): {stats['confidence_scores']['medium']} items") 
        print(f"   Low (<70%): {stats['confidence_scores']['low']} items")
            
        print(f"\n📂 Results saved to: {self.results_path}")
        print("\n🎯 Next steps (per execution plan):")
        print("   1. Review categorized files for roadmap vision")
        print("   2. Process T-Pot items for tomorrow's deadline")
        print("   3. Resolve conflicts_manual.json")
        print("   4. Plan GitHub posting for team items")

if __name__ == "__main__":
    processor = TaskProcessor926()
    processor.run() 