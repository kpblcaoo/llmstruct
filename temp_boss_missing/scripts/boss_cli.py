#!/usr/bin/env python3
"""
Boss CLI - Полнофункциональный CLI для руководителя
Включает все технические возможности + бизнес-модули
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Добавляем пути для импорта
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    # Импорты из основной системы
    from llmstruct.ai_cli_integration import AISelfAwarenessCLIIntegration
    from llmstruct.cli_commands import CommandProcessor
    from llmstruct.cli_config import CLIConfig
    from llmstruct.cli_utils import CLIUtils
    
    # Импорты boss модулей
    from business_planning import BusinessPlanningManager
    from team_management import TeamManagementSystem
    
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Some imports failed: {e}")
    IMPORTS_AVAILABLE = False


class BossCLI:
    """
    Boss CLI - полнофункциональный интерфейс для руководителя.
    Включает все технические возможности + бизнес-функции.
    """
    
    def __init__(self, project_root: str = None):
        """Инициализация Boss CLI."""
        # Исправляем путь - поднимаемся на 3 уровня выше от .personal/boss/scripts/
        if project_root is None:
            boss_cli_file = Path(__file__).resolve()
            # .personal/boss/scripts/boss_cli.py -> .personal/boss/scripts -> .personal/boss -> .personal -> project_root
            self.project_root = str(boss_cli_file.parent.parent.parent)
        else:
            self.project_root = project_root
        
        # Инициализация технических систем
        if IMPORTS_AVAILABLE:
            self.ai_integration = AISelfAwarenessCLIIntegration(self.project_root)
            
            config = CLIConfig(self.project_root)
            utils = CLIUtils()
            self.command_processor = CommandProcessor(self.project_root, config, utils)
            
            # Инициализация бизнес-систем
            self.business_manager = BusinessPlanningManager()
            self.team_manager = TeamManagementSystem()
        else:
            self.ai_integration = None
            self.command_processor = None
            self.business_manager = None
            self.team_manager = None
        
        # Команды Boss CLI
        self.boss_commands = {
            # AI Enhancement Commands
            "ai-status": self.cmd_ai_status,
            "ai-audit": self.cmd_ai_audit,
            "ai-context": self.cmd_ai_context,
            "ai-queue": self.cmd_ai_queue,
            "ai-summary": self.cmd_ai_summary,
            
            # Business Management Commands
            "business-roadmap": self.cmd_business_roadmap,
            "financial-plan": self.cmd_financial_plan,
            "strategic-decision": self.cmd_strategic_decision,
            "business-analysis": self.cmd_business_analysis,
            "business-summary": self.cmd_business_summary,
            
            # Team Management Commands
            "team-strategy": self.cmd_team_strategy,
            "team-evaluation": self.cmd_team_evaluation,
            "hiring-plan": self.cmd_hiring_plan,
            "team-analysis": self.cmd_team_analysis,
            "team-report": self.cmd_team_report,
            
            # Technical Commands (полный доступ)
            "technical": self.cmd_technical,
            "context-full": self.cmd_context_full,
            "workspace-override": self.cmd_workspace_override,
            
            # Meta Commands
            "help": self.cmd_help,
            "status": self.cmd_boss_status,
            "capabilities": self.cmd_capabilities
        }
    
    def run_interactive(self):
        """Запуск интерактивного режима Boss CLI."""
        print("🚀 Boss CLI - Полнофункциональный интерфейс руководителя")
        print("Доступны все технические возможности + бизнес-модули")
        print("Введите 'help' для списка команд или 'exit' для выхода\n")
        
        while True:
            try:
                user_input = input("Boss> ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 До свидания!")
                    break
                
                if not user_input:
                    continue
                
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    def process_command(self, command_line: str):
        """Обработка команды."""
        parts = command_line.split()
        if not parts:
            return
        
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.boss_commands:
            self.boss_commands[cmd](args)
        elif cmd.startswith('/') and self.command_processor:
            # Проксируем технические команды в основной command processor
            self.command_processor.process_command(command_line[1:])
        else:
            # Проксируем как промпт в основной command processor
            if self.command_processor:
                self.command_processor.process_prompt(command_line)
            else:
                print(f"❌ Неизвестная команда: {cmd}")
    
    # AI Enhancement Commands
    def cmd_ai_status(self, args):
        """AI система статус."""
        if not self.ai_integration:
            print("❌ AI Integration недоступна")
            return
        
        result = self.ai_integration.integrate_ai_status_command()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_ai_audit(self, args):
        """AI система аудит."""
        if not self.ai_integration:
            print("❌ AI Integration недоступна")
            return
        
        result = self.ai_integration.integrate_ai_audit_command()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_ai_context(self, args):
        """AI контекст управление."""
        if not self.ai_integration:
            print("❌ AI Integration недоступна")
            return
        
        result = self.ai_integration.integrate_ai_context_command()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_ai_queue(self, args):
        """AI очередь мониторинг."""
        if not self.ai_integration:
            print("❌ AI Integration недоступна")
            return
        
        result = self.ai_integration.integrate_ai_queue_command()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_ai_summary(self, args):
        """AI система summary."""
        if not self.ai_integration:
            print("❌ AI Integration недоступна")
            return
        
        result = self.ai_integration.get_integration_summary()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Business Management Commands
    def cmd_business_roadmap(self, args):
        """Управление бизнес-роадмапом."""
        if not self.business_manager:
            print("❌ Business Manager недоступен")
            return
        
        if not args:
            print("Использование: business-roadmap <create|summary>")
            return
        
        action = args[0]
        if action == "create":
            roadmap_data = {
                "title": "Strategic Business Roadmap",
                "objectives": ["Market expansion", "Product development", "Team growth"],
                "timeline": "2025 Q1-Q4",
                "key_metrics": ["Revenue", "User base", "Market share"]
            }
            result = self.business_manager.create_business_roadmap(roadmap_data)
        elif action == "summary":
            result = self.business_manager.get_business_summary()
        else:
            print("❌ Неизвестное действие")
            return
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_financial_plan(self, args):
        """Управление финансовым планированием."""
        if not self.business_manager:
            print("❌ Business Manager недоступен")
            return
        
        if not args:
            print("Использование: financial-plan <create|analyze>")
            return
        
        action = args[0]
        if action == "create":
            plan_data = {
                "budget_categories": {
                    "development": 200000,
                    "marketing": 100000,
                    "operations": 50000
                },
                "revenue_projections": {
                    "q1": 50000,
                    "q2": 100000,
                    "q3": 150000,
                    "q4": 200000
                },
                "investment_areas": ["R&D", "Marketing", "Infrastructure"]
            }
            result = self.business_manager.create_financial_plan(plan_data)
        elif action == "analyze":
            result = self.business_manager.analyze_business_metrics()
        else:
            print("❌ Неизвестное действие")
            return
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_strategic_decision(self, args):
        """Запись стратегических решений."""
        if not self.business_manager:
            print("❌ Business Manager недоступен")
            return
        
        decision_data = {
            "decision": "Strategic technology pivot",
            "rationale": "Market demand and competitive advantage",
            "impact_level": "high",
            "stakeholders": ["Development team", "Product management"],
            "timeline": "Q2 2025"
        }
        
        result = self.business_manager.record_strategic_decision(decision_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_business_analysis(self, args):
        """Анализ бизнес-метрик."""
        if not self.business_manager:
            print("❌ Business Manager недоступен")
            return
        
        result = self.business_manager.analyze_business_metrics()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_business_summary(self, args):
        """Сводка по бизнесу."""
        if not self.business_manager:
            print("❌ Business Manager недоступен")
            return
        
        result = self.business_manager.get_business_summary()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Team Management Commands
    def cmd_team_strategy(self, args):
        """Управление стратегией команды."""
        if not self.team_manager:
            print("❌ Team Manager недоступен")
            return
        
        strategy_data = {
            "title": "Team Development Strategy",
            "objectives": ["Improve collaboration", "Increase productivity", "Enhance skills"],
            "methods": ["Regular training", "Team building", "Performance reviews"],
            "timeline": "2025"
        }
        
        result = self.team_manager.create_team_strategy(strategy_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_team_evaluation(self, args):
        """Запись оценки команды."""
        if not self.team_manager:
            print("❌ Team Manager недоступен")
            return
        
        evaluation_data = {
            "evaluation_type": "quarterly_review",
            "period": "Q4 2024",
            "team_performance": "excellent",
            "key_achievements": ["Project delivery", "Process improvement"],
            "areas_for_improvement": ["Documentation", "Testing coverage"],
            "action_items": ["Training sessions", "Process updates"]
        }
        
        result = self.team_manager.record_team_evaluation(evaluation_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_hiring_plan(self, args):
        """Планирование найма."""
        if not self.team_manager:
            print("❌ Team Manager недоступен")
            return
        
        plan_data = {
            "positions": [
                {"role": "Senior Backend Developer", "priority": "high"},
                {"role": "DevOps Engineer", "priority": "medium"},
                {"role": "UI/UX Designer", "priority": "low"}
            ],
            "timeline": "Q1-Q2 2025",
            "budget": 300000,
            "requirements": ["Remote work", "Competitive salary", "Growth opportunities"]
        }
        
        result = self.team_manager.create_hiring_plan(plan_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_team_analysis(self, args):
        """Анализ производительности команды."""
        if not self.team_manager:
            print("❌ Team Manager недоступен")
            return
        
        result = self.team_manager.analyze_team_performance()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def cmd_team_report(self, args):
        """Отчёт по команде."""
        if not self.team_manager:
            print("❌ Team Manager недоступен")
            return
        
        result = self.team_manager.generate_team_report()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Technical Commands
    def cmd_technical(self, args):
        """Технические команды (полный доступ)."""
        if not args:
            print("Доступные технические команды:")
            print("- github-sync-enhanced")
            print("- epic-management-full")
            print("- deploy-operations")
            print("- comprehensive-indexing")
            return
        
        tech_cmd = args[0]
        print(f"🔧 Выполнение технической команды: {tech_cmd}")
        print("(Здесь будет интеграция с полными техническими возможностями)")
    
    def cmd_context_full(self, args):
        """Неограниченный доступ к контексту."""
        print("🧠 Context FULL mode активирован")
        print("Доступны все режимы: FULL/FOCUSED/MINIMAL")
        # Здесь интеграция с context orchestrator
    
    def cmd_workspace_override(self, args):
        """Emergency workspace overrides."""
        if not args:
            print("Использование: workspace-override <level>")
            print("Уровни: emergency, admin, override")
            return
        
        level = args[0]
        print(f"⚠️ Workspace override активирован: {level}")
        print("(Здесь будет интеграция с workspace management)")
    
    # Meta Commands
    def cmd_capabilities(self, args):
        """Анализ возможностей системы."""
        capabilities = {
            "ai_integration": {
                "available": bool(self.ai_integration),
                "commands": ["ai-status", "ai-audit", "ai-context", "ai-queue", "ai-summary"]
            },
            "business_management": {
                "available": bool(self.business_manager),
                "commands": ["business-roadmap", "financial-plan", "strategic-decision", "business-analysis"]
            },
            "team_management": {
                "available": bool(self.team_manager),
                "commands": ["team-strategy", "team-evaluation", "hiring-plan", "team-analysis", "team-report"]
            },
            "technical_access": {
                "available": bool(self.command_processor),
                "full_system_access": True,
                "context_modes": ["FULL", "FOCUSED", "MINIMAL"],
                "emergency_overrides": True
            }
        }
        
        print(json.dumps(capabilities, indent=2, ensure_ascii=False))
    
    def cmd_boss_status(self, args):
        """Общий статус Boss CLI."""
        status = {
            "boss_cli_version": "1.0",
            "project_root": self.project_root,
            "imports_available": IMPORTS_AVAILABLE,
            "systems_status": {
                "ai_integration": "✅" if self.ai_integration else "❌",
                "command_processor": "✅" if self.command_processor else "❌",
                "business_manager": "✅" if self.business_manager else "❌",
                "team_manager": "✅" if self.team_manager else "❌"
            },
            "access_level": "BOSS - Full Access",
            "confidentiality": "boss_only"
        }
        
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    def cmd_help(self, args):
        """Справка по командам Boss CLI."""
        help_text = """
🚀 Boss CLI - Полнофункциональный интерфейс руководителя

AI ENHANCEMENT COMMANDS:
  ai-status          - Статус AI системы
  ai-audit           - Аудит AI возможностей
  ai-context         - Управление AI контекстом
  ai-queue           - Мониторинг AI очереди
  ai-summary         - Сводка AI интеграции

BUSINESS MANAGEMENT COMMANDS:
  business-roadmap   - Управление бизнес-роадмапом
  financial-plan     - Финансовое планирование
  strategic-decision - Запись стратегических решений
  business-analysis  - Анализ бизнес-метрик
  business-summary   - Сводка по бизнесу

TEAM MANAGEMENT COMMANDS:
  team-strategy      - Стратегия команды
  team-evaluation    - Оценка команды
  hiring-plan        - Планирование найма
  team-analysis      - Анализ производительности
  team-report        - Отчёт по команде

TECHNICAL COMMANDS (полный доступ):
  technical          - Технические операции
  context-full       - Полный доступ к контексту
  workspace-override - Emergency overrides
  /<command>         - Любые технические команды с /

META COMMANDS:
  capabilities       - Анализ возможностей
  status            - Статус Boss CLI
  help              - Эта справка
  exit              - Выход

ПРИМЕРЫ:
  business-roadmap create
  team-evaluation
  ai-status
  /context FULL
  /workspace override emergency
        """
        print(help_text)


def main():
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Boss CLI - Полнофункциональный интерфейс руководителя")
    parser.add_argument("--project-root", help="Путь к корню проекта")
    parser.add_argument("--command", help="Команда для выполнения")
    
    args = parser.parse_args()
    
    boss_cli = BossCLI(args.project_root)
    
    if args.command:
        boss_cli.process_command(args.command)
    else:
        boss_cli.run_interactive()


if __name__ == "__main__":
    main() 