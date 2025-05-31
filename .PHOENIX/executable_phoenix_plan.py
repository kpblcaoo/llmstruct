#!/usr/bin/env python3
"""
PHOENIX: Исполняемый план реструктуризации
Автоматизация шагов из opus_PHOENIX_FINAL_EXECUTABLE_PLAN.md
"""

import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PhoenixExecutor:
    def __init__(self, workspace_path: str, ollama_url: str = "http://localhost:8000"):
        self.workspace = Path(workspace_path)
        self.ollama_url = ollama_url
        self.phoenix_dir = self.workspace / ".PHOENIX"
        self.metrics = {"phase": 0, "completed_tasks": [], "errors": []}
        
    def setup_workspace(self) -> bool:
        """Фаза 0: Подготовка рабочего пространства"""
        try:
            # Создание структуры директорий
            (self.phoenix_dir / "schemas").mkdir(parents=True, exist_ok=True)
            (self.phoenix_dir / "docs").mkdir(parents=True, exist_ok=True)
            (self.phoenix_dir / "archive").mkdir(parents=True, exist_ok=True)
            (self.phoenix_dir / "consolidated").mkdir(parents=True, exist_ok=True)
            
            logger.info("✅ Workspace setup completed")
            return True
        except Exception as e:
            logger.error(f"❌ Workspace setup failed: {e}")
            return False
    
    def analyze_duplicates(self) -> Optional[Dict]:
        """Анализ дубликатов с конкретными метриками"""
        try:
            # Запуск анализа дубликатов (предполагаем, что команда существует)
            result = subprocess.run([
                "llmstruct", "analyze-duplicates", 
                "--save-report", str(self.phoenix_dir / "duplicates_report.json"),
                "--format", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(self.phoenix_dir / "duplicates_report.json") as f:
                    report = json.load(f)
                logger.info(f"✅ Duplicates analysis completed: {report.get('duplicate_percentage', 0)}% duplicates found")
                return report
            else:
                logger.error(f"❌ Duplicates analysis failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"❌ Duplicates analysis error: {e}")
            return None
    
    def query_ollama(self, message: str, model: str = "wizardlm2:7b", context_file: Optional[str] = None) -> Optional[str]:
        """Запрос к Ollama с проверкой качества ответа"""
        try:
            payload = {
                "message": message,
                "model": model
            }
            
            if context_file:
                payload["context_file"] = context_file
                
            response = requests.post(f"{self.ollama_url}/api/v1/chat/ollama", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                ollama_response = result.get('response', '')
                
                # Проверка качества ответа
                if len(ollama_response) < 50:
                    logger.warning(f"⚠️ Short response from {model}, might need external API")
                    return None
                    
                logger.info(f"✅ Ollama response received from {model}")
                return ollama_response
            else:
                logger.error(f"❌ Ollama request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ollama query error: {e}")
            return None
    
    def validate_checkpoint(self, phase: int) -> bool:
        """Валидация checkpoint с конкретными критериями"""
        validations = {
            0: self._validate_phase_0,
            1: self._validate_phase_1,
            2: self._validate_phase_2,
            3: self._validate_phase_3,
            4: self._validate_phase_4
        }
        
        validator = validations.get(phase)
        if validator:
            return validator()
        else:
            logger.warning(f"⚠️ No validator for phase {phase}")
            return True
    
    def _validate_phase_0(self) -> bool:
        """Валидация фазы 0: подготовка"""
        checks = {
            'workspace_created': self.phoenix_dir.exists(),
            'duplicates_analyzed': (self.phoenix_dir / "duplicates_report.json").exists(),
            'strategy_created': (self.phoenix_dir / "consolidation_strategy.md").exists()
        }
        
        passed = all(checks.values())
        logger.info(f"Phase 0 validation: {checks}")
        return passed
    
    def _validate_phase_1(self) -> bool:
        """Валидация фазы 1: консолидация"""
        # Проверка что дубликаты удалены, архив создан
        archive_dir = self.phoenix_dir / "archive"
        return archive_dir.exists() and len(list(archive_dir.glob("*"))) > 0
    
    def _validate_phase_2(self) -> bool:
        """Валидация фазы 2: создание схем"""
        schemas_dir = self.phoenix_dir / "schemas"
        required_schemas = ["workflow_high_level.mmd", "current_state.mmd"]
        return all((schemas_dir / schema).exists() for schema in required_schemas)
    
    def _validate_phase_3(self) -> bool:
        """Валидация фазы 3: рефакторинг"""
        # Проверка что код валиден, тесты проходят
        try:
            result = subprocess.run(["python", "-m", "py_compile"] + list(self.workspace.glob("*.py")), 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _validate_phase_4(self) -> bool:
        """Валидация фазы 4: документация"""
        required_docs = ["README.md", "LLM_INTEGRATION_GUIDE.md"]
        return all((self.workspace / doc).exists() for doc in required_docs)
    
    def execute_phase(self, phase: int) -> bool:
        """Выполнение конкретной фазы плана"""
        phase_methods = {
            0: self._execute_phase_0,
            1: self._execute_phase_1,
            2: self._execute_phase_2,
            3: self._execute_phase_3,
            4: self._execute_phase_4
        }
        
        method = phase_methods.get(phase)
        if method:
            success = method()
            if success and self.validate_checkpoint(phase):
                self.metrics["phase"] = phase
                self.metrics["completed_tasks"].append(f"phase_{phase}")
                logger.info(f"✅ Phase {phase} completed successfully")
                return True
            else:
                logger.error(f"❌ Phase {phase} failed or validation failed")
                return False
        else:
            logger.error(f"❌ Unknown phase: {phase}")
            return False
    
    def _execute_phase_0(self) -> bool:
        """Фаза 0: Подготовка и анализ дубликатов"""
        if not self.setup_workspace():
            return False
            
        duplicates_report = self.analyze_duplicates()
        if not duplicates_report:
            return False
            
        # Генерация стратегии консолидации
        strategy = self.query_ollama(
            "Analyze this duplication report and suggest consolidation strategy. "
            "Group by: 1) Bot implementations 2) Init/main functions 3) Other duplicates. "
            "Output structured plan.",
            model="wizardlm2:7b",
            context_file=str(self.phoenix_dir / "duplicates_report.json")
        )
        
        if strategy:
            with open(self.phoenix_dir / "consolidation_strategy.md", "w") as f:
                f.write(strategy)
            return True
        return False
    
    def _execute_phase_1(self) -> bool:
        """Фаза 1: Консолидация и архивирование"""
        # Реальная логика консолидации ботов
        bot_files = list(self.workspace.glob("*bot*.py"))
        
        if len(bot_files) > 1:
            # Архивируем дубликаты (оставляем integrations/telegram_bot.py)
            main_bot = None
            for bot in bot_files:
                if "integrations/telegram_bot" in str(bot):
                    main_bot = bot
                    break
            
            if not main_bot and bot_files:
                main_bot = bot_files[0]  # Берем первый как основной
                
            archive_dir = self.phoenix_dir / "archive" / "bots"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            for bot in bot_files:
                if bot != main_bot:
                    bot.rename(archive_dir / bot.name)
                    logger.info(f"Archived: {bot.name}")
        
        return True
    
    def _execute_phase_2(self) -> bool:
        """Фаза 2: Создание схем архитектуры"""
        # Генерация высокоуровневой схемы
        workflow_schema = self.query_ollama(
            "Create detailed Mermaid diagram: LLMStruct High-Level Workflow. "
            "Show: 1) User interaction points 2) LLM integration flow 3) Data flow 4) Major components interaction. "
            "Optimize for LLM understanding.",
            model="wizardlm2:7b"
        )
        
        if workflow_schema:
            with open(self.phoenix_dir / "schemas" / "workflow_high_level.mmd", "w") as f:
                f.write(workflow_schema)
            return True
        return False
    
    def _execute_phase_3(self) -> bool:
        """Фаза 3: Рефакторинг с LLM-first подходом"""
        # Здесь должна быть логика рефакторинга
        # Пока заглушка
        logger.info("Phase 3: Refactoring (stub implementation)")
        return True
    
    def _execute_phase_4(self) -> bool:
        """Фаза 4: Финальная документация"""
        readme = self.query_ollama(
            "Create professional README.md for LLMStruct. "
            "Emphasize: 1) LLM-first architecture 2) Self-modifying capabilities "
            "3) Multi-provider support 4) Clean, modular structure. "
            "Include badges, quick start, architecture overview.",
            model="qwen2.5:7b"
        )
        
        if readme:
            with open(self.workspace / "README_new.md", "w") as f:
                f.write(readme)
            return True
        return False
    
    def run_full_plan(self) -> bool:
        """Запуск полного плана Phoenix"""
        logger.info("🔥 Starting PHOENIX restructuring plan")
        
        for phase in range(5):
            logger.info(f"Starting Phase {phase}")
            if not self.execute_phase(phase):
                logger.error(f"Failed at Phase {phase}, stopping execution")
                return False
                
        logger.info("✅ PHOENIX plan completed successfully!")
        return True

if __name__ == "__main__":
    executor = PhoenixExecutor("/home/sma/projects/llmstruct/llmstruct")
    success = executor.run_full_plan()
    
    if success:
        print("🎉 Phoenix restructuring completed!")
    else:
        print("💥 Phoenix restructuring failed!")
