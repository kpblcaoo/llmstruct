def analyze_duplicates(args):
    """Analyze function duplication using struct.json deep analysis."""
    try:
        from llmstruct.workflow_orchestrator import WorkflowOrchestrator
        debug = getattr(args, 'debug', False)
        deep_mode = getattr(args, 'deep_duplicates', 'same-name')
        if debug:
            print(f"🔧 [DEBUG] Starting analyze_duplicates with debug mode (deep_mode={deep_mode})")
        if deep_mode == 'any-name':
            print("⚠️  'any-name' mode: comparing all function bodies regardless of name. This may be slow on large codebases!")
        print("🔍 Analyzing Function Duplication...")
        orchestrator = WorkflowOrchestrator(".", debug=debug)
        if debug:
            print("🔧 [DEBUG] Calling analyze_codebase_for_duplicates...")
        no_prod_filter = getattr(args, 'no_prod_filter', False)
        analysis = orchestrator.analyze_codebase_for_duplicates(deep_duplicates=deep_mode, no_prod_filter=no_prod_filter)
        if 'error' in analysis:
            print(f"❌ Error: {analysis['error']}")
            return
        if hasattr(args, 'format') and args.format == 'json':
            import json
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            return
        duplication_data = analysis.get('analysis', {})
        recommendations = analysis.get('recommendations', [])
        if debug:
            print(f"🔧 [DEBUG] Processing {len(recommendations)} recommendations")
        print(f"\n📊 Duplication Analysis Summary:")
        print(f"  Total Functions: {duplication_data.get('total_unique_functions', 0)}")
        print(f"  Duplicated: {duplication_data.get('duplicated_functions', 0)}")
        print(f"  Percentage: {duplication_data.get('duplication_percentage', 0):.1f}%")
        if hasattr(args, 'priority') and args.priority != 'all':
            recommendations = [r for r in recommendations if r.get('priority') == args.priority]
            if debug:
                print(f"🔧 [DEBUG] Filtered to {len(recommendations)} {args.priority} priority recommendations")
        threshold = getattr(args, 'threshold', 2)
        duplicates = duplication_data.get('duplication_details', {})
        filtered_duplicates = {k: v for k, v in duplicates.items() if len(v) >= threshold}
        if debug:
            print(f"🔧 [DEBUG] Filtered duplicates by threshold {threshold}: {len(filtered_duplicates)} functions")
        if filtered_duplicates:
            print(f"\n🚨 Duplicated Functions (≥{threshold} copies):")
            sorted_duplicates = sorted(filtered_duplicates.items(), key=lambda x: len(x[1]), reverse=True)
            for func_name, paths in sorted_duplicates[:10]:
                priority_emoji = "🔴" if len(paths) > 3 else "🟡"
                print(f"  {priority_emoji} {func_name} ({len(paths)} copies)")
                for path in paths[:3]:
                    print(f"     - {path}")
                if len(paths) > 3:
                    print(f"     ... and {len(paths) - 3} more")
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations[:10]:
                priority_emoji = "🔴" if rec.get('priority') == 'high' else "🟡"
                print(f"  {priority_emoji} {rec['function']}")
                print(f"     {rec['recommendation']}")
        if hasattr(args, 'save_report') and args.save_report:
            if debug:
                print(f"🔧 [DEBUG] Saving report to {args.save_report}")
            import json
            with open(args.save_report, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\n💾 Detailed report saved to: {args.save_report}")
        next_steps = analysis.get('next_steps', [])
        if next_steps:
            print(f"\n🎯 Recommended Actions:")
            for i, step in enumerate(next_steps, 1):
                print(f"  {i}. {step}")
        print(f"\n✅ Analysis uses existing llmstruct architecture:")
        print(f"   - struct.json for deep codebase analysis")
        print(f"   - CopilotContextManager for context loading")
        print(f"   - No duplication of existing functions")
        print(f"\nℹ️  Production filter: {'OFF (все дубликаты, включая архив/тесты)' if no_prod_filter else 'ON (только production-код)'}")
        if debug:
            print("🔧 [DEBUG] analyze_duplicates completed successfully")
    except Exception as e:
        print(f"❌ Failed to analyze duplicates: {e}")
        if getattr(args, 'debug', False):
            import traceback
            print(f"🔧 [DEBUG] Full traceback:")
            traceback.print_exc() 