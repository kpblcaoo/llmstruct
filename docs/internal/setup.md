# llmstruct Internal Setup

**Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T23:00:27.888546Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Local Setup

1. **Clone Repo**:
   ```bash
   git clone https://github.com/kpblcaoo/llmstruct.git
   cd llmstruct
   ```
2. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Qwen-1.5B** (TSK-016):
   ```bash
   python src/llmstruct/cli.py --model qwen-1.5b --spec struct.json
   ```

## 2. VPS Setup (TSK-018)

- **Deploy**: Use Nginx (TSK-014).
- **Run Qwen-7B** (v0.3.0):
   ```bash
   docker run -v ./struct.json:/app/struct.json llmstruct:qwen-7b
   ```
- **Monitor**: Grafana for metrics (TSK-015).

## 3. Notes

- Check API limits (TSK-014).
- Use `internal/roadmap.md` for priorities.
- Ping @kpblcaoo for onboarding (TSK-019).
