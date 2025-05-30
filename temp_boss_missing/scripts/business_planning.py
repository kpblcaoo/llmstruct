#!/usr/bin/env python3
"""
Business Planning Module
Модуль для стратегического бизнес-планирования и коммерческого анализа.
Доступен только руководителю проекта.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class BusinessPlanningManager:
    """Управление бизнес-планированием и коммерческой стратегией."""
    
    def __init__(self, boss_data_dir: str = ".personal/boss/data"):
        """Инициализация менеджера бизнес-планирования."""
        self.data_dir = Path(boss_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.business_roadmap_file = self.data_dir / "business_roadmap.json"
        self.financial_planning_file = self.data_dir / "financial_planning.json"
        self.strategic_decisions_file = self.data_dir / "strategic_decisions.json"
        
    def create_business_roadmap(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание бизнес-роадмапа."""
        try:
            roadmap = {
                "id": f"roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "roadmap_data": roadmap_data,
                "status": "draft",
                "confidentiality": "boss_only"
            }
            
            self._save_data(self.business_roadmap_file, roadmap)
            logger.info(f"Business roadmap created: {roadmap['id']}")
            
            return {
                "status": "success",
                "roadmap_id": roadmap["id"],
                "message": "Business roadmap created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create business roadmap: {e}")
            return {
                "status": "error",
                "message": f"Failed to create business roadmap: {e}"
            }
    
    def create_financial_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание финансового плана."""
        try:
            financial_plan = {
                "id": f"finplan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "plan_data": plan_data,
                "confidentiality": "boss_only",
                "categories": ["revenue", "expenses", "investments", "projections"]
            }
            
            self._save_data(self.financial_planning_file, financial_plan)
            logger.info(f"Financial plan created: {financial_plan['id']}")
            
            return {
                "status": "success",
                "plan_id": financial_plan["id"],
                "message": "Financial plan created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create financial plan: {e}")
            return {
                "status": "error",
                "message": f"Failed to create financial plan: {e}"
            }
    
    def record_strategic_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Запись стратегического решения."""
        try:
            decision = {
                "id": f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "decision_data": decision_data,
                "impact_level": decision_data.get("impact_level", "medium"),
                "confidentiality": "boss_only"
            }
            
            # Загружаем существующие решения
            decisions = self._load_data(self.strategic_decisions_file, default=[])
            if not isinstance(decisions, list):
                decisions = []
            
            decisions.append(decision)
            
            self._save_data(self.strategic_decisions_file, decisions)
            logger.info(f"Strategic decision recorded: {decision['id']}")
            
            return {
                "status": "success",
                "decision_id": decision["id"],
                "message": "Strategic decision recorded successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to record strategic decision: {e}")
            return {
                "status": "error",
                "message": f"Failed to record strategic decision: {e}"
            }
    
    def analyze_business_metrics(self) -> Dict[str, Any]:
        """Анализ бизнес-метрик."""
        try:
            # Загружаем все бизнес-данные
            roadmap = self._load_data(self.business_roadmap_file, default={})
            financial = self._load_data(self.financial_planning_file, default={})
            decisions = self._load_data(self.strategic_decisions_file, default=[])
            
            analysis = {
                "analysis_timestamp": datetime.now().isoformat(),
                "business_roadmap_status": "present" if roadmap else "missing",
                "financial_plan_status": "present" if financial else "missing",
                "strategic_decisions_count": len(decisions) if isinstance(decisions, list) else 0,
                "recommendations": [],
                "confidentiality": "boss_only"
            }
            
            # Добавляем рекомендации
            if not roadmap:
                analysis["recommendations"].append("Create business roadmap")
            if not financial:
                analysis["recommendations"].append("Develop financial planning")
            if len(decisions) < 5:
                analysis["recommendations"].append("Document more strategic decisions")
            
            return {
                "status": "success",
                "analysis": analysis,
                "message": "Business metrics analysis completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze business metrics: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze business metrics: {e}"
            }
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Получение сводки по бизнес-планированию."""
        try:
            roadmap = self._load_data(self.business_roadmap_file, default={})
            financial = self._load_data(self.financial_planning_file, default={})
            decisions = self._load_data(self.strategic_decisions_file, default=[])
            
            summary = {
                "summary_timestamp": datetime.now().isoformat(),
                "business_roadmap": {
                    "exists": bool(roadmap),
                    "id": roadmap.get("id", "N/A"),
                    "status": roadmap.get("status", "N/A")
                },
                "financial_planning": {
                    "exists": bool(financial),
                    "id": financial.get("id", "N/A"),
                    "categories": financial.get("categories", [])
                },
                "strategic_decisions": {
                    "count": len(decisions) if isinstance(decisions, list) else 0,
                    "recent_decisions": decisions[-3:] if isinstance(decisions, list) and decisions else []
                },
                "confidentiality": "boss_only"
            }
            
            return {
                "status": "success",
                "summary": summary,
                "message": "Business summary generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get business summary: {e}")
            return {
                "status": "error",
                "message": f"Failed to get business summary: {e}"
            }
    
    def _load_data(self, file_path: Path, default: Any = None) -> Any:
        """Загрузка данных из JSON файла."""
        try:
            if file_path.exists():
                with file_path.open('r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Failed to load data from {file_path}: {e}")
            return default
    
    def _save_data(self, file_path: Path, data: Any) -> None:
        """Сохранение данных в JSON файл."""
        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save data to {file_path}: {e}")
            raise


def create_business_planning_manager(data_dir: str = ".personal/boss/data") -> BusinessPlanningManager:
    """Создание менеджера бизнес-планирования."""
    return BusinessPlanningManager(data_dir)


if __name__ == "__main__":
    # Тестирование модуля
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python business_planning.py <command> [args]")
        print("Commands: create_roadmap, create_financial, record_decision, analyze, summary")
        sys.exit(1)
    
    manager = create_business_planning_manager()
    command = sys.argv[1]
    
    if command == "create_roadmap":
        result = manager.create_business_roadmap({
            "title": "Sample Business Roadmap",
            "objectives": ["Objective 1", "Objective 2"],
            "timeline": "Q1-Q4 2025"
        })
        print(json.dumps(result, indent=2))
        
    elif command == "create_financial":
        result = manager.create_financial_plan({
            "budget": {"development": 100000, "marketing": 50000},
            "projections": {"q1": 25000, "q2": 50000}
        })
        print(json.dumps(result, indent=2))
        
    elif command == "record_decision":
        result = manager.record_strategic_decision({
            "decision": "Sample strategic decision",
            "rationale": "Business reasons",
            "impact_level": "high"
        })
        print(json.dumps(result, indent=2))
        
    elif command == "analyze":
        result = manager.analyze_business_metrics()
        print(json.dumps(result, indent=2))
        
    elif command == "summary":
        result = manager.get_business_summary()
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 