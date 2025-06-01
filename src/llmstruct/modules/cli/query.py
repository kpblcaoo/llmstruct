import json
import logging
from pathlib import Path
from llmstruct.cache import JSONCache
from llmstruct import LLMClient
import os

def query(args):
    """Query LLMs with prompt and context."""
    if not Path(args.context).exists():
        logging.error(f"Context file {args.context} does not exist")
        return
    
    cache = JSONCache() if args.use_cache else None
    client = LLMClient()
    
    # Use context orchestrator if available and context mode is specified
    context_data = None
    if hasattr(args, 'context_mode') and args.context_mode:
        try:
            from llmstruct.context_orchestrator import create_context_orchestrator
            
            # Determine scenario based on mode and usage
            scenario = "cli_query" if args.context_mode == "FOCUSED" else "cli_interactive"
            
            # Get optimized context
            orchestrator = create_context_orchestrator(os.path.dirname(args.context))
            optimized_context = orchestrator.get_context_for_scenario(scenario)
            
            # Use optimized context instead of raw file
            if optimized_context:
                logging.info(f"Using optimized context with mode {args.context_mode}")
                context_data = optimized_context
        except ImportError:
            logging.warning("Context orchestrator not available, using raw context file")
        except Exception as e:
            logging.warning(f"Failed to use context orchestrator: {e}")
    
    # Query with optimized or raw context
    if context_data:
        result = client.query_with_context(
            prompt=args.prompt,
            context_data=context_data,
            mode=args.mode,
            model=args.model,
            artifact_ids=args.artifact_ids,
        )
    else:
        result = client.query(
            prompt=args.prompt,
            context_path=args.context,
            mode=args.mode,
            model=args.model,
            artifact_ids=args.artifact_ids,
        )
    
    if result:
        with Path(args.output).open("w", encoding="utf-8") as f:
            json.dump({"prompt": args.prompt, "response": result}, f, indent=2)
        logging.info(f"Generated {args.output}")
    else:
        logging.error("Query failed")
    if cache:
        cache.close() 