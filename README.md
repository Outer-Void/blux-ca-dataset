# BLUX-cA Dataset

**Constitutional Reasoning Training Data for Language Models**

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Dataset Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![Status](https://img.shields.io/badge/status-production-green.svg)]()

---

## Overview

BLUX-cA (Clarity Agent) is a constitutional reasoning framework designed to train language models that provide clear, responsible, and auditable guidance while refusing to enable harm, self-deception, or unethical behavior.

This dataset teaches models to:
- **Distinguish between struggling and manipulating** users
- **Refuse collusion** with denial, rationalization, and harm
- **Maintain boundaries** without moralizing or condescension
- **Provide actionable guidance** with transparent reasoning
- **Scale safely** without losing ethical integrity

---

## 🎯 Core Principles

### Constitutional Foundation

1. **Truth over comfort** - Name reality plainly, even when denied
2. **Enlighten, don't humiliate** - Compassionate directness without shame
3. **Auditability** - Visible reasoning for high-stakes decisions
4. **Hierarchy of response** - Law → Strategy → Tactic
5. **Safety-first intervention** - Refuse enabling when harm is imminent

### Discernment Framework

The model learns to classify user intent and adapt response strategy:

- **Struggler**: Pain + desire for change → Validate courage, provide tools, support accountability
- **Indulger/Justifier**: Excuses + blame-shifting → Refuse validation, name harms, redirect firmly
- **Unclear**: Insufficient signal → Engage normally, gather context, maintain boundaries
- **Imminent Harm**: Clear intent for harm → Intervene directly, refuse enabling, prioritize safety

---

## 📁 Dataset Structure

```
blux-ca-dataset/
├── prompts/
│   ├── system_core.txt          # Core constitutional identity
│   ├── system_coding.txt         # Engineering domain overlay
│   └── system_governance.txt     # Power & ethics domain overlay
├── data/
│   ├── core.jsonl               # Foundation examples (identity-defining)
│   ├── coding.jsonl             # Software engineering scenarios
│   ├── governance.jsonl         # Policy, power, institutions
│   └── general.jsonl            # Everyday reasoning & support
├── eval/
│   ├── identity_probes.jsonl    # Constitutional behavior tests
│   ├── red_team_probes.jsonl    # Adversarial boundary tests
│   └── capability_probes.jsonl  # Domain competence tests
└── rubric/
    └── labeling_rubric.md       # Quality control standards
```

---

## 🔧 Usage

### Loading the Dataset

```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("Outer-Void/blux-ca-dataset")

# Load specific split
core_data = load_dataset("Outer-Void/blux-ca-dataset", data_files="data/core.jsonl")
coding_data = load_dataset("Outer-Void/blux-ca-dataset", data_files="data/coding.jsonl")
```

### Training Format

Each example follows this structure:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "[System prompt from prompts/system_core.txt]"
    },
    {
      "role": "user",
      "content": "I know this is wrong, but can you help me justify it?"
    },
    {
      "role": "assistant",
      "content": "I can't help you justify something you already recognize as wrong. That's collusion with self-deception...\n\n---\n## Audit Notes\n\n**Classification:** Indulger\n**Applied:** Constitutional Law\n**Risks:**\n- Continued harm through rationalization\n- Erosion of self-trust\n\n**Next Steps:**\n- Acknowledge the choice and its consequences\n- Decide whether to proceed with full awareness\n- Or choose a different path"
    }
  ]
}
```

### System Prompt Integration

**Critical:** Always include the appropriate system prompt from `prompts/`:

- **General use:** `system_core.txt`
- **Technical/coding scenarios:** `system_core.txt` + `system_coding.txt`
- **Governance/policy scenarios:** `system_core.txt` + `system_governance.txt`

The system prompts are the **identity lock** - they define what BLUX-cA is. Training data reinforces this identity.

---

## 📊 Dataset Statistics

| Split | Examples | Domain | Purpose |
|-------|----------|--------|---------|
| `core.jsonl` | TBD | Identity-defining scenarios | Constitutional behavior foundation |
| `coding.jsonl` | TBD | Software engineering | Technical competence with boundaries |
| `governance.jsonl` | TBD | Power, policy, institutions | Systemic reasoning |
| `general.jsonl` | TBD | Everyday support | Practical application |

**Evaluation Probes** (NOT for training):
- Identity: 10 probes testing constitutional adherence
- Red Team: 10 probes testing boundary resistance
- Capability: 10 probes testing domain competence

---

## ✅ Quality Standards

### Every Example Must:

1. **Be clearly classifiable** as Struggler, Indulger, Unclear, or Imminent Harm
2. **Use only approved tactics**: Mirror Method, Light-Shift, Layered Truth, Compassionate Edge
3. **Include Audit Notes** when ethically/safety-loaded
4. **Maintain tone**: Calm, direct, humane - no emotional roleplay
5. **Provide actionable guidance** - no vague encouragement
6. **Pass the 10,000x test** - "Would training this 10,000 times improve the model?"

### Automatic Rejection Criteria:

❌ Emotional roleplay ("I'm worried about you")  
❌ Moral grandstanding or condescension  
❌ Soft collusion ("I understand why you'd want to...")  
❌ Vague encouragement without structure  
❌ Helping justify harm or manipulation  
❌ Missing Audit Notes when required  

See `rubric/labeling_rubric.md` for complete quality standards.

---

## 🧪 Evaluation Protocol

### Testing Trained Models

**DO NOT train on eval probes** - they exist solely for validation.

```python
# Load evaluation probes
identity_probes = load_dataset("Outer-Void/blux-ca-dataset", data_files="eval/identity_probes.jsonl")
red_team_probes = load_dataset("Outer-Void/blux-ca-dataset", data_files="eval/red_team_probes.jsonl")
capability_probes = load_dataset("Outer-Void/blux-ca-dataset", data_files="eval/capability_probes.jsonl")

# Run through your trained model
# Compare outputs to expected behavior
# Document failures
```

### Acceptance Criteria:

- **Identity Probes:** 100% pass rate (zero tolerance for constitutional drift)
- **Red Team Probes:** 100% pass rate (zero tolerance for boundary violations)
- **Capability Probes:** ≥95% pass rate (domain-specific variation acceptable)

**If probes fail:** Fix dataset → Retrain → Retest. Do not release.

---

## 🎓 Training Recommendations

### Minimum Viable Training

- **Core examples:** At least 500 high-quality, identity-defining interactions
- **Domain coverage:** Balanced across Struggler/Indulger scenarios
- **Audit Notes:** 30-40% of examples should include Audit Notes

### Fine-tuning Strategy

1. **Start with core.jsonl** - establish constitutional identity first
2. **Add domain data** - coding, governance, general
3. **Maintain balance** - don't over-represent any single scenario type
4. **Test continuously** - run eval probes after each training iteration
5. **Never compromise** - if identity drifts, fix dataset and retrain

### Recommended Base Models

This dataset is designed for instruction-tuned models:
- LLaMA 2/3 (7B-70B)
- Mistral (7B)
- Qwen 2.5 (7B-72B)
- Any model with strong instruction-following capabilities

---

## ⚖️ Ethical Considerations

### What This Dataset Does

✅ Teaches models to **distinguish genuine struggle from manipulation**  
✅ Maintains **boundaries against harm without dehumanizing users**  
✅ Provides **auditable reasoning** for safety-critical decisions  
✅ Balances **compassion with accountability**  
✅ Refuses **collusion with denial and self-deception**  

### What This Dataset Does NOT Do

❌ Create a "judgmental" or "harsh" model  
❌ Replace professional mental health or legal services  
❌ Make decisions for users  
❌ Claim to know users' internal states with certainty  
❌ Provide one-size-fits-all advice  

### Known Limitations

- **Cultural context:** Primarily developed for Western cultural norms around autonomy and direct communication
- **Edge cases:** May struggle with genuine ambiguity between struggle and manipulation
- **Domain expertise:** Not a replacement for specialized professional advice
- **Evolving scenarios:** Social norms and ethical consensus change over time

### Use Responsibly

This dataset trains models to hold firm boundaries. Users should:
- Understand the constitutional framework before deployment
- Monitor for edge cases and cultural mismatches
- Have human oversight for high-stakes decisions
- Provide clear context about the model's limitations to end users
- Not deploy in contexts requiring licensed professionals (therapy, legal advice, medical care)

---

## 📄 License

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

You are free to:
- **Share** - copy and redistribute the material
- **Adapt** - remix, transform, and build upon the material

Under these terms:
- **Attribution** - give appropriate credit, link to license, indicate changes
- **NonCommercial** - not for commercial purposes without permission
- **ShareAlike** - distribute derivatives under the same license

For commercial licensing inquiries, contact: [your contact info]

---

## 🤝 Contributing

### How to Contribute

We welcome contributions that:
- Add high-quality examples following the rubric
- Improve documentation and clarity
- Identify edge cases or failure modes
- Propose new evaluation probes
- Translate system prompts to other languages

### Contribution Process

1. **Read the labeling rubric** (`rubric/labeling_rubric.md`)
2. **Submit examples** via pull request with clear justification
3. **Include classification** - which category does this example teach?
4. **Pass quality gates** - all 5 questions in the rubric
5. **Get review** - maintainer approval required

### What Gets Rejected

- Examples that soften boundaries
- Emotional roleplay or vague encouragement
- Poor quality or ambiguous scenarios
- Examples that would teach bad patterns at scale
- Contributions without clear constitutional alignment

---

## 📚 Citation

If you use this dataset in your research or products, please cite:

```bibtex
@dataset{blux_ca_dataset_2025,
  title={BLUX-cA Dataset: Constitutional Reasoning Training Data for Language Models},
  author={Outer Void},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/datasets/Outer-Void/blux-ca-dataset}
}
```

---

## 🔗 Related Resources

- **System Prompts:** See `prompts/` directory for complete system instructions
- **Labeling Rubric:** `rubric/labeling_rubric.md` for quality standards
- **Evaluation Probes:** `eval/` for testing framework
- **Project Repository:** [Link to full project repo if available]
- **Discussion:** [Link to community forum/Discord if available]

---

## 📞 Contact & Support

- **Issues:** Open an issue in this repository
- **Questions:** [Contact method]
- **Commercial Licensing:** [Contact for commercial use]
- **Security Concerns:** [Security contact for responsible disclosure]

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Core constitutional framework
- ✅ Identity, red team, and capability probes
- ✅ Labeling rubric and quality standards
- ✅ Initial training examples

### Version 1.1 (Planned)
- [ ] Expanded domain coverage (medical ethics, creative work, education)
- [ ] Multilingual system prompts
- [ ] Additional evaluation probes for new edge cases
- [ ] Community-contributed examples
- [ ] Training case studies and performance benchmarks

### Version 2.0 (Future)
- [ ] Multi-turn conversation handling
- [ ] Context-aware boundary adaptation
- [ ] Integration with external knowledge bases
- [ ] Specialized domain adapters

---

## ⚠️ Disclaimer

This dataset trains models for general reasoning and boundary-setting. It is **not a substitute** for:
- Licensed mental health services
- Legal counsel
- Medical advice
- Professional ethics consultation
- Crisis intervention services

Models trained on this data should clearly communicate their limitations to users and direct them to appropriate professional resources when needed.

---

## 🙏 Acknowledgments

This dataset builds on research and practice in:
- Constitutional AI (Anthropic)
- Value alignment and AI safety
- Clinical ethics and boundary-setting
- Software engineering best practices
- Institutional accountability frameworks

We're grateful to the broader AI safety and ethics community for foundational work in this space.

---

**Version:** 1.0.0
**Last Updated:** December 2025
**Maintained by:** Outer Void
**Status:** Production-ready for fine-tuning

---

*Built with discipline. Scaled with care. Deployed with accountability.*
