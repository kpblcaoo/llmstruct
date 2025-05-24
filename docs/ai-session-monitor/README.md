# AI Session Monitor - LLMStruct

Real-time monitoring and visualization dashboard for AI-assisted development sessions.

## 🎯 Features

- **Real-time Session Tracking**: Monitor active AI sessions and task queues
- **Rampage Prevention**: Built-in constraints to prevent autonomous large-scale changes
- **GitHub Integration**: Automatic dashboard updates via GitHub Actions
- **Mobile-Optimized**: Responsive design for monitoring on the go
- **Constraint Compliance**: Visual indicators for AI session limits and warnings

## 📊 Dashboard

Visit the live dashboard: [AI Session Monitor](https://kpblcaoo.github.io/llmstruct/ai-session-monitor)

### Dashboard Components

1. **Session Activity**: Real-time metrics of AI commits and changes
2. **Rampage Prevention Status**: Current constraint enforcement status  
3. **Active Sessions**: Number of ongoing development sessions
4. **Configuration Changes**: Recent updates to AI constraints
5. **Activity Timeline**: Historical view of AI session patterns
6. **Compliance Chart**: Visual representation of constraint adherence

## 🛡️ AI Constraints

The system implements several layers of protection:

- **Session Limits**: Maximum 5 changes per session
- **Consultation Requirements**: Automatic escalation for complex changes
- **Scope Limitations**: Prevention of unauthorized scope expansion
- **Real-time Monitoring**: Continuous tracking of AI activity patterns

## 🔧 Configuration Files

- `data/copilot/ai_constraints.json` - Core constraint definitions
- `data/copilot/session_rules.json` - User profiles and workflow rules
- `data/copilot/warnings.json` - Warning system configuration
- `data/copilot/processing_queue.json` - Real-time task tracking

## 🚀 GitHub Actions Integration

The dashboard is automatically updated by the `ai-session-monitor.yml` workflow:

- **Triggers**: Push to copilot configs, scheduled updates, manual dispatch
- **Validation**: JSON schema validation for all constraint files
- **Analytics**: Automatic analysis of recent AI activity
- **Alerting**: Issue creation for high activity patterns
- **Deployment**: Automatic GitHub Pages deployment

## 📱 Mobile Support

The dashboard is optimized for mobile devices with:

- Responsive grid layout
- Touch-friendly controls
- Offline data caching
- Push notification support (future)

## 🔍 Monitoring Metrics

- AI commits in last 24 hours
- Configuration file changes
- Active session count
- Constraint violation tracking
- Performance metrics and error rates

## 🤖 Integration with VS Code Copilot

The system integrates seamlessly with VS Code through `copilot_init.json`:

```json
{
  "processing_queue_integration": {
    "enabled": true,
    "real_time_monitoring": true,
    "rampage_prevention": true,
    "github_sync": true
  }
}
```

## 🛠️ Development

To contribute to the AI Session Monitor:

1. **Local Testing**: Validate JSON schemas and test dashboard locally
2. **Configuration Updates**: Follow the modular structure in `data/copilot/`
3. **Dashboard Changes**: Update the GitHub Actions workflow for new features
4. **Constraint Modifications**: Test thoroughly with rampage prevention limits

## 📈 Future Enhancements

- WebSocket integration for true real-time updates
- Advanced analytics and ML-based anomaly detection
- Integration with external monitoring services
- Enhanced mobile app with native push notifications
- Custom constraint rule engine

---

Built with 🦈 by the LLMStruct team | [GitHub Repository](https://github.com/kpblcaoo/llmstruct)
