import json
import re
import logging
import argparse
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load a JSON file and return its contents."""
    if not os.path.exists(file_path):
        logging.error(f"File {file_path} not found")
        return None
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding {file_path}: {e}")
        return None


def verify_response_with_struct(
        response_text: str, struct_data: Dict[str, Any]) -> bool:
    """Verify llm_response.json against struct.json."""
    try:
        # Check metadata
        assert struct_data.get("project_name") == "llmstruct", "Project name mismatch"
        assert struct_data.get("author") == "@kpblcaoo", "Author mismatch"
        assert struct_data.get("license") == "GPL-3.0", "License mismatch"
        assert struct_data.get("date") == "2025-05-20", "Date mismatch"

        # Check goals
        expected_goals = {
            g for g in struct_data.get(
                "goals", []) if g in [
                "G1", "G4", "G5", "G6"]}
        goals_in_response = set(re.findall(r"G\d", response_text))
        if not expected_goals.issubset(goals_in_response):
            logging.error(f"Missing goals: {expected_goals - goals_in_response}")
            return False

        # Check extensions
        expected_extensions = {
            e for e in struct_data.get(
                "extensions",
                []) if e.startswith("EXT-")}
        extensions_in_response = set(re.findall(r"EXT-\d{3}", response_text))
        if not expected_extensions.issubset(extensions_in_response):
            logging.error(
                f"Missing extensions: {expected_extensions - extensions_in_response}")
            return False

        # Check file references
        files_in_response = set(re.findall(r"\w+\.json", response_text))
        expected_files = {"tasks.json", "project_context.json"}
        if not expected_files.issubset(files_in_response):
            logging.error(
                f"Missing file references: {expected_files - files_in_response}")
            return False

        logging.info("Verification successful: Response matches struct.json")
        return True
    except AssertionError as e:
        logging.error(f"Metadata mismatch: {e}")
        return False


def verify_response_without_struct(response_text: str) -> bool:
    """Verify llm_response.json based on LLMstruct principles."""
    # Check for key principles
    principles = [
        "universal JSON format",
        "transparency",
        "LLM optimization",
        "end-to-end"]
    for principle in principles:
        if principle.lower() not in response_text.lower():
            logging.error(f"Principle '{principle}' not mentioned in response")
            return False

    # Check goals and extensions
    goals = set(re.findall(r"G\d", response_text))
    expected_goals = {"G1", "G4", "G5", "G6"}
    if not expected_goals.issubset(goals):
        logging.error(f"Missing goals: {expected_goals - goals}")
        return False

    extensions = set(re.findall(r"EXT-\d{3}", response_text))
    expected_extensions = {"EXT-004", "EXT-005", "EXT-006"}
    if not expected_extensions.issubset(extensions):
        logging.error(f"Missing extensions: {expected_extensions - extensions}")
        return False

    # Check file references
    files = set(re.findall(r"\w+\.json", response_text))
    expected_files = {"tasks.json", "project_context.json"}
    if not expected_files.issubset(files):
        logging.error(f"Missing file references: {expected_files - files}")
        return False

    logging.info("Verification successful: Response aligns with LLMstruct principles")
    return True


def generate_metrics(response_data: Dict[str, Any],
                     server_log: Dict[str, Any]) -> Dict[str, Any]:
    """Generate metrics for the response per EXT-004."""
    response_text = response_data["response"]
    word_count = len(response_text.split())
    char_count = len(response_text)
    goals_mentioned = len(re.findall(r"G\d", response_text))
    extensions_mentioned = len(re.findall(r"EXT-\d{3}", response_text))
    files_mentioned = len(re.findall(r"\w+\.json", response_text))

    # Hard-coded server log metrics (replace with actual parsing if log file
    # is available)
    metrics = {
        "total_duration_s": server_log.get("total_duration_s", 4.35),
        "prompt_eval_duration_s": server_log.get("prompt_eval_duration_s", 0.16),
        "eval_duration_s": server_log.get("eval_duration_s", 0.54),
        "total_request_time_s": server_log.get("total_request_time_s", 148),
        "token_generation_speed": server_log.get("token_generation_speed", 49 / 0.54),
        "prompt_token_count": server_log.get("prompt_token_count", 10),
        "response_token_count": server_log.get("response_token_count", 49),
        "word_count": word_count,
        "char_count": char_count,
        "goals_mentioned": goals_mentioned,
        "extensions_mentioned": extensions_mentioned,
        "files_mentioned": files_mentioned,
        "model_buffer_size_mib": server_log.get("model_buffer_size_mib", 3922.02),
        "kv_cache_size_mib": server_log.get("kv_cache_size_mib", 512.00),
        "compute_buffer_size_mib": server_log.get("compute_buffer_size_mib", 296.01),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return metrics


def update_tasks_json(tasks_file: str, new_task: Dict[str, Any]):
    """Append a new task to tasks.json."""
    tasks = load_json_file(tasks_file) or {"tasks": []}
    tasks["tasks"] = tasks.get("tasks", [])
    tasks["tasks"].append(new_task)
    with open(tasks_file, "w") as f:
        json.dump(tasks, f, indent=2)
    logging.info(f"Added task {new_task['task_id']} to {tasks_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify llm_response.json and manage tasks")
    parser.add_argument(
        "--response",
        default="llm_response.json",
        help="Path to llm_response.json")
    parser.add_argument(
        "--struct",
        default="struct.json",
        help="Path to struct.json (optional)")
    parser.add_argument("--tasks", default="tasks.json", help="Path to tasks.json")
    parser.add_argument(
        "--metrics",
        default="metrics.json",
        help="Path to output metrics.json")
    args = parser.parse_args()

    # Load response
    response_data = load_json_file(args.response)
    if not response_data:
        return

    # Verify response
    struct_data = load_json_file(args.struct)
    if struct_data:
        logging.info("Verifying with struct.json")
        verify_response_with_struct(response_data["response"], struct_data)
    else:
        logging.info("No struct.json found, verifying with LLMstruct principles")
        verify_response_without_struct(response_data["response"])

    # Generate metrics
    server_log = {
        "total_duration_s": 4.35,
        "prompt_eval_duration_s": 0.16,
        "eval_duration_s": 0.54,
        "total_request_time_s": 148,
        "token_generation_speed": 49 / 0.54,
        "prompt_token_count": 10,
        "response_token_count": 49,
        "model_buffer_size_mib": 3922.02,
        "kv_cache_size_mib": 512.00,
        "compute_buffer_size_mib": 296.01
    }
    metrics = generate_metrics(response_data, server_log)
    with open(args.metrics, "w") as f:
        json.dump(metrics, f, indent=2)
    logging.info(f"Metrics saved to {args.metrics}")

    # Add error handling task to tasks.json
    error_task = {
        "task_id": "TASK-001",
        "description": "Improve error handling in _query_ollama to display user-friendly messages for 404 errors, e.g., 'Model not found. Check available models with ollama list'",
        "status": "planned",
        "priority": "high",
        "due_date": "2025-06-03",
        "related_idea": "G5",
        "extension": "EXT-004"
    }
    update_tasks_json(args.tasks, error_task)

    # Add tokenizer warning task
    tokenizer_task = {
        "task_id": "TASK-002",
        "description": "Investigate and resolve tokenizer warning 'special_eos_id is not in special_eog_ids' for Mistral-7B-Instruct-v0.3",
        "status": "planned",
        "priority": "medium",
        "due_date": "2025-06-10",
        "related_idea": "G5",
        "extension": "EXT-005"}
    update_tasks_json(args.tasks, tokenizer_task)


if __name__ == "__main__":
    main()
