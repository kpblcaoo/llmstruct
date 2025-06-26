import os
import logging
from llmstruct.modules.cli.handlers_legacy import interactive_legacy

async def interactive(args):
    """Run interactive CLI with modular structure if available, fallback to legacy."""
    try:
        await interactive_modular(args)
        return
    except Exception as e:
        logging.warning(f"Modular CLI failed, falling back to legacy: {e}")
    await interactive_legacy(args)

async def interactive_modular(args):
    """Run interactive CLI with modular structure."""
    from llmstruct.cli_core import create_cli_core
    root_dir = os.path.abspath(args.root_dir)
    cli_core = create_cli_core(root_dir)
    if hasattr(args, 'context_mode') and args.context_mode:
        if hasattr(cli_core, 'command_processor') and cli_core.command_processor:
            cli_core.command_processor.default_context_mode = args.context_mode
            logging.info(f"Set default context mode to {args.context_mode}")
    cli_core.run_interactive_mode()

# Удаляю определение функции interactive_legacy из этого файла 