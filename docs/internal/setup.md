# llmstruct Internal Setup

Setup guide for `llmstruct` team (@kpblcaoo, @momai, @ivan-ib). Focus: Local development, Qwen, VPS.

## Local Setup
1. **Clone Repo**:
   ```bash
   git clone https://github.com/kpblcaoo/llmstruct.git
   cd llmstruct
   ```
2. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Qwen-1.5B** (3060Ti, TSK-016):
   ```bash
   python src/llmstruct/cli.py --model qwen-1.5b --spec struct.json
   ```
   - Optimize VRAM: Use quantization (LoRA, TSK-016).
4. **Test Parser**:
   ```bash
   python src/llmstruct/parser.py --input src/ --output struct.json
   pytest src/tests/test_parser.py
   ```

## VPS Setup (TSK-018)
- **Deploy**: Use Nginx (@momai, TSK-014).
- **Run Qwen-7B** (v0.3.0):
   ```bash
   docker run -v ./struct.json:/app/struct.json llmstruct:qwen-7b
   ```
- **Monitor**: Grafana for metrics (TSK-015, @momai).

## Notes
- Check API limits (Anthropic, Grok, TSK-014).
- Use `internal/roadmap.md` for priorities.
- Ping @kpblcaoo for 1–2h onboarding call (TSK-019).