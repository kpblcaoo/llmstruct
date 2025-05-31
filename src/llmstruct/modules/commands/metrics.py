def metrics_status():
    """Показать текущий статус метрик"""
    try:
        from llmstruct.metrics_tracker import get_metrics_tracker
        tracker = get_metrics_tracker()
        summary = tracker.get_session_summary()
        print("📊 CURRENT SESSION METRICS")
        print("=" * 40)
        print(f"Session ID: {summary['session_id']}")
        print(f"Duration: {summary['duration']:.0f}s ({summary['duration']/60:.1f}m)")
        print(f"Efficiency Score: {summary['efficiency_score']:.2f}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        print(f"Estimated Cost: ${summary['estimated_cost']:.4f}")
        print(f"Tasks: {summary['tasks_completed']}/{summary['tasks_total']}")
        print(f"False Paths: {summary['false_paths']}")
        print(f"Rollbacks: {summary['rollbacks']}")
        print(f"Retries: {summary['retries']}")
        print(f"Avoidable Errors: {summary['avoidable_errors']}")
    except Exception as e:
        print(f"❌ Error getting metrics status: {e}")

def metrics_summary():
    """Показать детальную сводку метрик"""
    try:
        from llmstruct.metrics_tracker import get_metrics_tracker
        tracker = get_metrics_tracker()
        summary = tracker.get_session_summary()
        metadata = tracker.session_data['metadata']
        workflow = tracker.session_data['workflow_metrics']
        print("📊 DETAILED SESSION SUMMARY")
        print("=" * 50)
        print(f"Session: {summary['session_id']}")
        print(f"Branch: {metadata['branch']}")
        print(f"Commit: {metadata['commit_hash']}")
        print(f"Struct.json Hash: {metadata['struct_json_hash']}")
        print()
        print("🎯 PERFORMANCE:")
        print(f"  Efficiency Score: {summary['efficiency_score']:.2f}/1.0")
        if summary['efficiency_score'] < 0.7:
            print("  ⚠️ Low efficiency detected!")
        print(f"  Duration: {summary['duration']:.0f}s")
        print(f"  Tasks per minute: {summary['tasks_total'] / max(summary['duration']/60, 1):.1f}")
        print()
        print("💰 RESOURCE USAGE:")
        print(f"  Total Tokens: {summary['total_tokens']:,}")
        print(f"  Average per task: {summary['total_tokens'] / max(summary['tasks_total'], 1):.0f}")
        print(f"  Estimated Cost: ${summary['estimated_cost']:.4f}")
        print()
        print("🔄 WORKFLOW EVENTS:")
        print(f"  Struct.json usage: {workflow['struct_json_usage']}")
        print(f"  Context switches: {workflow['context_switches']}")
        print(f"  CLI commands: {workflow['cli_commands_executed']}")
        print(f"  File operations: {workflow['file_operations']}")
        print()
        if summary['false_paths'] > 0 or summary['rollbacks'] > 0:
            print("⚠️ INEFFICIENCIES DETECTED:")
            if summary['false_paths'] > 0:
                print(f"  False paths: {summary['false_paths']}")
            if summary['rollbacks'] > 0:
                print(f"  Rollbacks: {summary['rollbacks']}")
            if summary['avoidable_errors'] > 0:
                print(f"  Avoidable errors: {summary['avoidable_errors']}")
            print("  💡 Consider reviewing workflow patterns")
            print()
    except Exception as e:
        print(f"❌ Error getting metrics summary: {e}")

def metrics_analytics(output_file=None, format='json'):
    """Сгенерировать аналитические данные"""
    try:
        from llmstruct.metrics_tracker import get_metrics_tracker
        import json
        import time
        tracker = get_metrics_tracker()
        analytics = tracker.get_analytics_data()
        if 'error' in analytics:
            print(f"❌ {analytics['error']}")
            return
        output_data = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analytics": analytics,
            "current_session": tracker.get_session_summary()
        }
        if output_file:
            if format == 'csv':
                import csv
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["session", "tokens", "efficiency", "cost", "completion_rate"])
                    for i, session in enumerate(analytics['token_usage_over_time']):
                        efficiency = analytics['efficiency_trends'][i]['efficiency']
                        cost = analytics['cost_analysis'][i]['cost']
                        completion = analytics['task_completion_rates'][i]['completion_rate']
                        writer.writerow([session['session'], session['tokens'], efficiency, cost, completion])
                print(f"📈 Analytics data exported to {output_file} (CSV)")
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                print(f"📈 Analytics data exported to {output_file} (JSON)")
        else:
            print("📈 ANALYTICS DATA PREVIEW:")
            print(json.dumps(analytics, indent=2)[:1000] + "...")
    except Exception as e:
        print(f"❌ Error generating analytics: {e}")

def metrics_report(sessions=10, output_file=None):
    """Создать всесторонний отчет"""
    try:
        from llmstruct.metrics_tracker import get_metrics_tracker
        import time
        tracker = get_metrics_tracker()
        analytics = tracker.get_analytics_data()
        if 'error' in analytics:
            print(f"❌ {analytics['error']}")
            return
        recent_sessions = analytics.get('token_usage_over_time', [])[-sessions:]
        report = f"""📊 LLMSTRUCT PROJECT METRICS REPORT\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}\nReport Period: Last {len(recent_sessions)} sessions\n\n🎯 SUMMARY:\n- Total Sessions Analyzed: {len(recent_sessions)}\n- Average Tokens per Session: {sum(s['tokens'] for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0:.0f}\n- Total Token Usage: {sum(s['tokens'] for s in recent_sessions):,}\n\n📈 TRENDS:\n- Efficiency Trend: {'📈 Improving' if len(analytics['efficiency_trends']) > 1 and analytics['efficiency_trends'][-1]['efficiency'] > analytics['efficiency_trends'][0]['efficiency'] else '📉 Declining'}\n- Token Usage Trend: {'📈 Increasing' if len(recent_sessions) > 1 and recent_sessions[-1]['tokens'] > recent_sessions[0]['tokens'] else '📉 Decreasing'}\n\n🎯 RECOMMENDATIONS:\n"""
        if recent_sessions:
            avg_efficiency = sum(s['efficiency'] for s in analytics['efficiency_trends'][-sessions:]) / min(sessions, len(analytics['efficiency_trends']))
            if avg_efficiency < 0.7:
                report += "- ⚠️ Low efficiency detected. Review workflow patterns.\n"
            if sum(s['tokens'] for s in recent_sessions) > 100000:
                report += "- 💰 High token usage. Consider context optimization.\n"
            error_sessions = [s for s in analytics['error_patterns'][-sessions:] if s['false_paths'] > 0 or s['rollbacks'] > 0]
            if error_sessions:
                report += f"- 🔧 {len(error_sessions)} sessions with inefficiencies. Review error patterns.\n"
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📋 Report saved to {output_file}")
        else:
            print(report)
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def metrics_track(event_type, details=None):
    """Ручное отслеживание событий"""
    try:
        from llmstruct.metrics_tracker import track_workflow_event
        track_workflow_event(event_type, details)
        print(f"📊 Tracked event: {event_type}")
        if details:
            print(f"    Details: {details}")
    except Exception as e:
        print(f"❌ Error tracking event: {e}")

def metrics_tokens():
    """Показать детальную статистику токенов"""
    try:
        from llmstruct.metrics_tracker import get_token_summary, get_metrics_tracker
        print("📊 **Token Usage Summary**")
        print("=" * 50)
        summary = get_token_summary()
        if not summary:
            print("❌ No token data available")
            return
        print(f"📱 **Telegram Interactions:**")
        print(f"   • Total tokens: {summary.get('telegram_tokens', 0):,}")
        print(f"   • Interactions: {summary.get('telegram_interactions_count', 0)}")
        print(f"\n🔌 **API Interactions:**")
        print(f"   • Total tokens: {summary.get('api_tokens', 0):,}")
        print(f"   • Interactions: {summary.get('api_interactions_count', 0)}")
        print(f"\n💰 **Overall:**")
        print(f"   • Total tokens: {summary.get('total_tokens', 0):,}")
        print(f"   • Estimated cost: ${summary.get('estimated_cost_usd', 0):.6f}")
        tracker = get_metrics_tracker()
        telegram_interactions = tracker.session_data.get('telegram_interactions', [])
        if telegram_interactions:
            print(f"\n📱 **Recent Telegram Interactions:**")
            for i, interaction in enumerate(telegram_interactions[-5:], 1):
                print(f"   {i}. {interaction.get('total_tokens_estimate', 0)} tokens "
                      f"(user: {interaction.get('user_tokens_estimate', 0)}, "
                      f"bot: {interaction.get('bot_tokens_estimate', 0)}, "
                      f"context: {interaction.get('context_tokens', 0)})")
        api_interactions = tracker.session_data.get('api_interactions', [])
        if api_interactions:
            print(f"\n🔌 **Recent API Interactions:**")
            for i, interaction in enumerate(api_interactions[-5:], 1):
                print(f"   {i}. {interaction.get('endpoint', 'unknown')} - "
                      f"{interaction.get('total_tokens', 0)} tokens "
                      f"(req: {interaction.get('request_tokens', 0)}, "
                      f"resp: {interaction.get('response_tokens', 0)}, "
                      f"ctx: {interaction.get('context_tokens', 0)})")
    except Exception as e:
        print(f"❌ Error getting token summary: {e}")

async def cmd_metrics(args):
    """Управление метриками проекта"""
    try:
        if args.metrics_action == 'status':
            metrics_status()
        elif args.metrics_action == 'summary':
            metrics_summary()
        elif args.metrics_action == 'analytics':
            metrics_analytics(args.output, args.format)
        elif args.metrics_action == 'tokens':
            metrics_tokens()
        elif args.metrics_action == 'report':
            metrics_report(args.sessions, args.output)
        elif args.metrics_action == 'track':
            metrics_track(args.event_type, args.details)
        else:
            print("❌ Unknown metrics action")
    except Exception as e:
        print(f"❌ Metrics command failed: {e}") 