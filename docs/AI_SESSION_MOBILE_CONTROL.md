# AI Session Mobile Control Panel

<!-- 
Mobile-friendly control interface for managing AI development sessions
Optimized for GitHub mobile app and responsive web interface
-->

## 🤖 Current Session Status

**Session ID:** `ai-session-{{ timestamp }}`  
**Risk Level:** 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ CRITICAL  
**Changes:** {{ changes_count }}/5  
**Duration:** {{ session_duration }}  

---

## 🎯 Quick Actions

### ✅ Approve & Continue
- [ ] **👍 Approve Current Changes** - Continue with current plan
- [ ] **🚀 Approve & Next Step** - Move to next planned action
- [ ] **📝 Approve with Notes** - Add feedback and continue

### ⚠️ Review & Clarify  
- [ ] **❓ Need Clarification** - Request more details about approach
- [ ] **🔍 Review Scope** - Check if changes match initial request
- [ ] **📋 Show Change Summary** - List all modifications made

### 🛑 Control Actions
- [ ] **⏸️ Pause Session** - Temporarily stop AI actions
- [ ] **🛑 Emergency Stop** - Immediately halt all changes
- [ ] **💾 Save & Exit** - Commit current state and end session

---

## 📊 Session Monitoring

### Change Tracker
```
Files Modified: {{ modified_files_count }}/5
New Files: {{ new_files_count }}/3  
Deletions: {{ deleted_files_count }}/1
Risk Score: {{ risk_score }}/100
```

### Recent Warnings
```
⚠️ {{ last_warning_type }}: {{ last_warning_message }}
📅 {{ warning_timestamp }}
```

---

## 🚨 Rampage Prevention Status

**Status:** {{ rampage_prevention_status }}
- **Change Velocity:** {{ change_velocity_status }}
- **Scope Drift:** {{ scope_drift_status }}  
- **CI/CD Safety:** {{ ci_cd_safety_status }}
- **Data Protection:** {{ data_protection_status }}

---

## 📱 Mobile Quick Commands

### One-Tap Responses
| Emoji | Action | Description |
|-------|--------|-------------|
| ✅ | `/approve` | Continue with current plan |
| ❓ | `/clarify` | Need more information |
| ⏸️ | `/pause` | Pause AI session |
| 🛑 | `/stop` | Emergency stop |
| 📝 | `/notes` | Add feedback |
| 🔍 | `/review` | Review changes |

### Voice Commands (GitHub Mobile)
- "Approve changes" → ✅ Approve
- "Need clarification" → ❓ Clarify  
- "Pause session" → ⏸️ Pause
- "Emergency stop" → 🛑 Stop

---

## 🎛️ Session Configuration

### Current Profile: {{ user_profile }}
- **Role:** {{ user_role }}
- **Permissions:** {{ user_permissions }}
- **Notification Level:** {{ notification_level }}

### AI Constraints Active
- ✅ Max 5 changes per session
- ✅ Consultation for breaking changes
- ✅ CI/CD safety checks
- ✅ Data backup triggers
- ✅ Scope creep detection

---

## 📞 Consultation Protocol

### When AI Must Ask
1. **Breaking Changes** - Public API modifications
2. **Architecture Changes** - Core structure modifications  
3. **Scope Expansion** - Beyond initial request
4. **High Risk** - CI/CD or data safety concerns
5. **Ambiguity** - Multiple interpretation paths

### Clarification Template
```
[llmstruct] {{ context_type }}

**Request:** {{ user_request_summary }}
**Ambiguity:** {{ ambiguity_type }}
**Options:**
1. {{ option_1 }}
2. {{ option_2 }}  
3. {{ option_3 }}

**Risk:** {{ risk_level }}
**Consultation:** {{ consultation_needed }}

Please choose option or provide guidance.
```

---

## 📈 Session Analytics

### Efficiency Metrics
- **Time to Completion:** {{ estimated_completion }}
- **Success Probability:** {{ success_probability }}%
- **User Satisfaction:** {{ user_satisfaction_score }}
- **Change Quality:** {{ change_quality_score }}

### Learning Insights
- **Common Patterns:** {{ common_patterns }}
- **Optimization Opportunities:** {{ optimization_suggestions }}
- **User Preferences:** {{ learned_preferences }}

---

## 🔗 Quick Links

- [📋 Current Tasks](./data/tasks.json)
- [🏗️ Project Structure](./struct.json)  
- [⚙️ CI/CD Status](/.github/workflows/ci.yml)
- [📖 Session Rules](./data/copilot/session_rules.json)
- [⚠️ Warnings Log](./data/copilot/warnings.json)

---

## 💡 Tips for Mobile Control

1. **Use Reactions** - React with ✅❓⏸️🛑 on AI comments
2. **Quick Commands** - Type `/approve`, `/clarify`, etc.
3. **Voice Notes** - Record audio feedback if typing is hard
4. **Notification Settings** - Enable for high-risk alerts only
5. **Batch Approvals** - Approve multiple low-risk changes at once

---

## 🆘 Emergency Contacts

**Project Lead:** @kpblcaoo  
**Technical Issues:** Create issue with `urgent` label
**Session Problems:** Comment with `@github-copilot /stop`

---

*Last Updated: {{ last_updated_timestamp }}*  
*Control Panel Version: 1.0.0*  
*Session: {{ session_id }}*
