#!/usr/bin/env python3
"""
Team Management Module
Модуль для управления командой, оценки сотрудников и HR-процессов.
Доступен только руководителю проекта.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class TeamManagementSystem:
    """Система управления командой и HR-процессами."""
    
    def __init__(self, boss_data_dir: str = ".personal/boss/data"):
        """Инициализация системы управления командой."""
        self.data_dir = Path(boss_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.team_strategy_file = self.data_dir / "team_strategy.json"
        self.team_evaluations_file = self.data_dir / "team_evaluations.json"
        self.hiring_plans_file = self.data_dir / "hiring_plans.json"
        
    def create_team_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание стратегии управления командой."""
        try:
            strategy = {
                "id": f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "strategy_data": strategy_data,
                "version": "1.0",
                "confidentiality": "boss_only"
            }
            
            self._save_data(self.team_strategy_file, strategy)
            logger.info(f"Team strategy created: {strategy['id']}")
            
            return {
                "status": "success",
                "strategy_id": strategy["id"],
                "message": "Team strategy created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create team strategy: {e}")
            return {
                "status": "error",
                "message": f"Failed to create team strategy: {e}"
            }
    
    def record_team_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Запись оценки члена команды."""
        try:
            evaluation = {
                "id": f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "evaluation_data": evaluation_data,
                "confidentiality": "boss_only",
                "sensitive": True
            }
            
            # Загружаем существующие оценки
            evaluations = self._load_data(self.team_evaluations_file, default=[])
            if not isinstance(evaluations, list):
                evaluations = []
            
            evaluations.append(evaluation)
            
            self._save_data(self.team_evaluations_file, evaluations)
            logger.info(f"Team evaluation recorded: {evaluation['id']}")
            
            return {
                "status": "success",
                "evaluation_id": evaluation["id"],
                "message": "Team evaluation recorded successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to record team evaluation: {e}")
            return {
                "status": "error",
                "message": f"Failed to record team evaluation: {e}"
            }
    
    def create_hiring_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание плана найма."""
        try:
            hiring_plan = {
                "id": f"hiring_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "plan_data": plan_data,
                "confidentiality": "boss_only",
                "status": "draft"
            }
            
            self._save_data(self.hiring_plans_file, hiring_plan)
            logger.info(f"Hiring plan created: {hiring_plan['id']}")
            
            return {
                "status": "success",
                "plan_id": hiring_plan["id"],
                "message": "Hiring plan created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create hiring plan: {e}")
            return {
                "status": "error",
                "message": f"Failed to create hiring plan: {e}"
            }
    
    def analyze_team_performance(self) -> Dict[str, Any]:
        """Анализ производительности команды."""
        try:
            evaluations = self._load_data(self.team_evaluations_file, default=[])
            strategy = self._load_data(self.team_strategy_file, default={})
            hiring_plans = self._load_data(self.hiring_plans_file, default={})
            
            analysis = {
                "analysis_timestamp": datetime.now().isoformat(),
                "team_evaluations_count": len(evaluations) if isinstance(evaluations, list) else 0,
                "strategy_exists": bool(strategy),
                "hiring_plan_exists": bool(hiring_plans),
                "confidentiality": "boss_only",
                "insights": []
            }
            
            # Добавляем инсайты
            if len(evaluations) == 0:
                analysis["insights"].append("No team evaluations recorded yet")
            elif len(evaluations) < 3:
                analysis["insights"].append("Consider more frequent team evaluations")
            
            if not strategy:
                analysis["insights"].append("Develop comprehensive team strategy")
            
            if not hiring_plans:
                analysis["insights"].append("Create hiring plans for team expansion")
            
            return {
                "status": "success",
                "analysis": analysis,
                "message": "Team performance analysis completed"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze team performance: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze team performance: {e}"
            }
    
    def get_team_summary(self) -> Dict[str, Any]:
        """Получение сводки по команде."""
        try:
            evaluations = self._load_data(self.team_evaluations_file, default=[])
            strategy = self._load_data(self.team_strategy_file, default={})
            hiring_plans = self._load_data(self.hiring_plans_file, default={})
            
            summary = {
                "summary_timestamp": datetime.now().isoformat(),
                "team_strategy": {
                    "exists": bool(strategy),
                    "id": strategy.get("id", "N/A"),
                    "version": strategy.get("version", "N/A")
                },
                "team_evaluations": {
                    "count": len(evaluations) if isinstance(evaluations, list) else 0,
                    "latest_evaluation": evaluations[-1] if isinstance(evaluations, list) and evaluations else None
                },
                "hiring_plans": {
                    "exists": bool(hiring_plans),
                    "id": hiring_plans.get("id", "N/A"),
                    "status": hiring_plans.get("status", "N/A")
                },
                "confidentiality": "boss_only"
            }
            
            return {
                "status": "success",
                "summary": summary,
                "message": "Team summary generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get team summary: {e}")
            return {
                "status": "error",
                "message": f"Failed to get team summary: {e}"
            }
    
    def generate_team_report(self) -> Dict[str, Any]:
        """Генерация отчёта по команде."""
        try:
            evaluations = self._load_data(self.team_evaluations_file, default=[])
            strategy = self._load_data(self.team_strategy_file, default={})
            
            report = {
                "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "report_type": "team_management",
                "confidentiality": "boss_only",
                "sections": {
                    "strategy_overview": self._summarize_strategy(strategy),
                    "evaluation_summary": self._summarize_evaluations(evaluations),
                    "recommendations": self._generate_recommendations(strategy, evaluations)
                }
            }
            
            return {
                "status": "success",
                "report": report,
                "message": "Team report generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate team report: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate team report: {e}"
            }
    
    def _summarize_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Краткое изложение стратегии."""
        if not strategy:
            return {"status": "no_strategy", "message": "No team strategy defined"}
        
        return {
            "status": "strategy_exists",
            "id": strategy.get("id", "N/A"),
            "created": strategy.get("created_at", "N/A"),
            "version": strategy.get("version", "N/A")
        }
    
    def _summarize_evaluations(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Краткое изложение оценок."""
        if not evaluations or not isinstance(evaluations, list):
            return {"status": "no_evaluations", "count": 0}
        
        return {
            "status": "evaluations_exist",
            "count": len(evaluations),
            "latest": evaluations[-1].get("timestamp", "N/A") if evaluations else "N/A",
            "frequency": "regular" if len(evaluations) > 5 else "occasional"
        }
    
    def _generate_recommendations(self, strategy: Dict[str, Any], evaluations: List[Dict[str, Any]]) -> List[str]:
        """Генерация рекомендаций."""
        recommendations = []
        
        if not strategy:
            recommendations.append("Develop comprehensive team strategy")
        
        if not evaluations or len(evaluations) < 3:
            recommendations.append("Increase frequency of team evaluations")
        
        if strategy and evaluations:
            recommendations.append("Review strategy alignment with evaluation results")
        
        recommendations.append("Consider team development initiatives")
        recommendations.append("Plan regular one-on-one meetings")
        
        return recommendations
    
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


def create_team_management_system(data_dir: str = ".personal/boss/data") -> TeamManagementSystem:
    """Создание системы управления командой."""
    return TeamManagementSystem(data_dir)


if __name__ == "__main__":
    # Тестирование модуля
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python team_management.py <command> [args]")
        print("Commands: create_strategy, record_evaluation, create_hiring, analyze, summary, report")
        sys.exit(1)
    
    system = create_team_management_system()
    command = sys.argv[1]
    
    if command == "create_strategy":
        result = system.create_team_strategy({
            "title": "Sample Team Strategy",
            "objectives": ["Improve collaboration", "Increase productivity"],
            "methods": ["Regular meetings", "Clear communication"]
        })
        print(json.dumps(result, indent=2))
        
    elif command == "record_evaluation":
        result = system.record_team_evaluation({
            "member": "Sample Member",
            "performance": "Good",
            "areas_for_improvement": ["Time management"],
            "strengths": ["Technical skills", "Communication"]
        })
        print(json.dumps(result, indent=2))
        
    elif command == "create_hiring":
        result = system.create_hiring_plan({
            "positions": ["Frontend Developer", "DevOps Engineer"],
            "timeline": "Q2 2025",
            "budget": 150000
        })
        print(json.dumps(result, indent=2))
        
    elif command == "analyze":
        result = system.analyze_team_performance()
        print(json.dumps(result, indent=2))
        
    elif command == "summary":
        result = system.get_team_summary()
        print(json.dumps(result, indent=2))
        
    elif command == "report":
        result = system.generate_team_report()
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 