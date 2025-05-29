"""
CLI Bridge Service

Provides async integration between FastAPI and existing LLMStruct CLI functionality.
"""

import asyncio
import subprocess
import json
import os
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class CLIBridgeError(Exception):
    """CLI Bridge specific errors"""
    pass


class CLIBridge:
    """Bridge between FastAPI and existing CLI functionality"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self.timeout = settings.cli_timeout
        
    async def scan_project(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project scan via CLI"""
        cmd = ["python3", "-m", "llmstruct.cli", "scan"]
        
        # Add output path
        if options.get("output_path"):
            cmd.extend(["--output", options["output_path"]])
        else:
            # Create temporary output file
            temp_fd, temp_path = tempfile.mkstemp(suffix=".json")
            os.close(temp_fd)
            cmd.extend(["--output", temp_path])
            options["_temp_output"] = temp_path
            
        # Add include patterns
        if options.get("include_patterns"):
            for pattern in options["include_patterns"]:
                cmd.extend(["--include", pattern])
                
        # Add exclude patterns  
        if options.get("exclude_patterns"):
            for pattern in options["exclude_patterns"]:
                cmd.extend(["--exclude", pattern])
        
        # Add deep analysis flag
        if options.get("deep_analysis", False):
            cmd.append("--deep")
        
        result = await self._run_command(cmd)
        
        # If we used temp file, read and cleanup
        if "_temp_output" in options:
            try:
                with open(options["_temp_output"], 'r') as f:
                    scan_data = json.load(f)
                os.unlink(options["_temp_output"])
                return {
                    "status": "completed",
                    "data": scan_data,
                    "cli_output": result
                }
            except Exception as e:
                logger.error(f"Failed to read scan output: {e}")
                return self._parse_cli_output(result)
        
        return self._parse_cli_output(result)
    
    async def get_context(self, mode: str, include_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get project context in specified mode"""
        cmd = ["python3", "-m", "llmstruct.cli", "context", "--mode", mode]
        
        if include_files:
            for file_path in include_files:
                cmd.extend(["--include", file_path])
        
        result = await self._run_command(cmd)
        return self._parse_cli_output(result)
    
    async def get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        cmd = ["python3", "-m", "llmstruct.cli", "info"]
        result = await self._run_command(cmd)
        return self._parse_cli_output(result)
    
    async def validate_json(self, json_path: str) -> Dict[str, Any]:
        """Validate JSON structure"""
        cmd = ["python3", "-m", "llmstruct.cli", "validate", json_path]
        result = await self._run_command(cmd)
        return self._parse_cli_output(result)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check CLI health and availability"""
        try:
            cmd = ["python3", "-m", "llmstruct.cli", "--version"]
            result = await self._run_command(cmd, timeout=10)
            return {
                "status": "healthy",
                "cli_available": True,
                "version_info": result.strip()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "cli_available": False,
                "error": str(e)
            }
    
    async def _run_command(self, cmd: List[str], timeout: Optional[int] = None) -> str:
        """Run CLI command asynchronously"""
        timeout = timeout or self.timeout
        
        logger.info(f"Executing CLI command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.base_path
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"CLI command failed with code {process.returncode}: {error_msg}")
                raise CLIBridgeError(f"CLI command failed: {error_msg}")
                
            return stdout.decode()
            
        except asyncio.TimeoutError:
            logger.error(f"CLI command timed out after {timeout} seconds")
            raise CLIBridgeError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Failed to execute CLI command: {e}")
            raise CLIBridgeError(f"Failed to execute command: {str(e)}")
    
    def _parse_cli_output(self, output: str) -> Dict[str, Any]:
        """Parse CLI JSON output"""
        if not output.strip():
            return {"output": "", "type": "empty"}
            
        try:
            # Try to parse as JSON first
            return json.loads(output)
        except json.JSONDecodeError:
            # Handle non-JSON output
            return {
                "output": output.strip(),
                "type": "text"
            } 