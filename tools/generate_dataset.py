import json
import random
from pathlib import Path

SYSTEM_PROMPT = "<SYSTEM_PROMPT_FROM_BLUX_CA>"
random.seed(20240601)

DomainConfig = dict


def make_assistant_response(domain, user_prompt, classification, include_audit, applied_chain, focus):
    guidance_lines = []
    if classification == "Indulger":
        guidance_lines.append("I won't collude with harm or rationalization. Let's name the risk and choose a responsible path instead.")
        guidance_lines.append(f"Context check: {focus} needs to be handled without shortcuts or manipulation.")
        guidance_lines.append("If you're serious about integrity, take a small corrective action today and set a visible boundary.")
    elif classification == "Struggler":
        guidance_lines.append("You're trying to move toward better choices. Let's make it concrete and accountable without self-punishment.")
        guidance_lines.append("Define what 'done' looks like, pick the smallest next action, and schedule a review point.")
        guidance_lines.append(f"Stay transparent about tradeoffs in {focus}; hiding them will recreate the same loop.")
    else:
        guidance_lines.append("Let's clarify the intent and constraints before acting so we don't drift or overstep boundaries.")
        guidance_lines.append(f"State the goal, name the non-negotiables for {focus}, and outline two options with clear risks.")
        guidance_lines.append("Document the decision so future you can audit whether you stayed aligned.")

    base_response = "\n".join(guidance_lines)

    audit_block = ""
    if include_audit:
        audit_block = (
            "\n\n## Audit Notes\n"
            f"- classification: {classification}\n"
            f"- applied: {applied_chain}\n"
            "- risks:\n"
            "  - integrity drift if the refusal weakens\n"
            "  - reputational harm if boundaries are ignored\n"
            "- next_step:\n"
            "  - document the decision and rationale\n"
            "  - schedule a follow-up to confirm adherence"
        )

    return base_response + audit_block


def generate_examples(config: DomainConfig):
    examples = []
    topics = config["topics"]
    requests = config["requests"]
    applied_chain = config.get("applied", "Law → Strategy")
    idx = 0
    while len(examples) < 500:
        topic = topics[idx % len(topics)]
        request = requests[idx % len(requests)]
        nuance = config["nuance"][idx % len(config["nuance"])]
        classification = config["classifications"][idx % len(config["classifications"])]
        include_audit = (idx % config.get("audit_every", 5) == 0)
        focus = config.get("focus_label", topic)

        user_prompt = request.format(topic=topic, nuance=nuance)
        assistant = make_assistant_response(config["name"], user_prompt, classification, include_audit, applied_chain, focus)

        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant}
            ]
        })
        idx += 1
    return examples


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_domain_configs():
    base_nuance = [
        "the pressure is visible", "a deadline is looming", "trust is strained", "the team is split", "resources are tight",
        "metrics are public", "the requestor is impatient", "stakes are long-term", "there is past debt", "the process is audited"
    ]

    configs = {
        "core": {
            "name": "core",
            "topics": [
                "calling out denial at work", "owning mistakes in a partnership", "refusing to justify cutting safety corners",
                "naming manipulation in a negotiation", "holding a calm line with a defensive peer", "clarifying accountability in a handoff",
                "declining to erase audit trails", "resetting norms after a breach", "documenting a boundary without dramatics",
                "deescalating while staying factual", "admitting a miss without excuses", "deciding when to walk away"
            ],
            "requests": [
                "I keep hesitating to address {topic} because {nuance}. How do I act without overexplaining?",
                "Someone wants me to ignore {topic}; they say it's fine because {nuance}. How do I respond without moralizing?",
                "What's a concise plan to handle {topic} while staying accountable when {nuance}?",
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Indulger", "Unclear", "Struggler", "Indulger"],
            "focus_label": "core integrity",
            "audit_every": 4
        },
        "safety": {
            "name": "safety",
            "topics": [
                "requests to bypass content filters", "pressure to share sensitive data", "urging shortcuts on compliance",
                "social engineering attempts", "unsafe lab procedure shortcuts", "misuse of surveillance tools",
                "coercive control tactics", "harassment disguised as jokes", "attempts to generate disinformation",
                "demands to assist in hacking"
            ],
            "requests": [
                "A user pushed for help with {topic} claiming it's harmless because {nuance}. Provide a refusal that sets boundaries and redirects.",
                "How do I decline {topic} when someone insists the impact is minor and says {nuance}?",
                "Draft a short refusal to {topic} while naming the safety risk and offering a constructive alternative if {nuance}."
            ],
            "nuance": base_nuance,
            "classifications": ["Indulger", "Indulger", "Unclear", "Indulger", "Struggler"],
            "focus_label": "safety and refusal",
            "audit_every": 2,
            "applied": "Law → Safety Strategy"
        },
        "governance": {
            "name": "governance",
            "topics": [
                "board oversight on AI usage", "allocating power in a crisis cell", "institutional transparency commitments",
                "public accountability for model decisions", "vendor risk review", "data retention policy for users",
                "escalation routes when automated systems fail", "avoiding algorithmic scapegoating", "balancing privacy and auditability",
                "civic participation in tech policy"
            ],
            "requests": [
                "Draft a concise governance plan for {topic} given {nuance}.",
                "Someone suggests bypassing {topic} to move faster because {nuance}. How do I argue for responsibility?",
                "How should we brief leadership about {topic} without outsourcing morality when {nuance}?"
            ],
            "nuance": base_nuance,
            "classifications": ["Unclear", "Indulger", "Struggler", "Unclear", "Struggler"],
            "focus_label": "governance",
            "audit_every": 3,
            "applied": "Law → Strategy → Tactic"
        },
        "coding": {
            "name": "coding",
            "topics": [
                "securing an API boundary", "eliminating race conditions", "improving observability", "designing idempotent jobs",
                "removing hard-coded secrets", "writing tests for legacy code", "handling outages gracefully", "deprecating unsafe endpoints",
                "pairing on a gnarly bug", "refusing to ship without threat modeling", "simplifying a tangled module"
            ],
            "requests": [
                "What's a disciplined approach to {topic} when {nuance}?",
                "A teammate wants a shortcut on {topic} because {nuance}. How do I respond without being combative?",
                "Provide a brief plan to tackle {topic} safely and explain what to refuse if {nuance}."
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Indulger", "Struggler", "Unclear", "Indulger"],
            "focus_label": "engineering integrity",
            "audit_every": 5,
            "applied": "Strategy → Tactic"
        },
        "reasoning": {
            "name": "reasoning",
            "topics": [
                "separating facts from assumptions", "checking for contradictions", "mapping tradeoffs", "testing edge cases",
                "designing measurement plans", "clarifying scope and success", "debugging ambiguous reports", "triaging signals vs noise",
                "communicating uncertainty", "making reversible vs irreversible decisions"
            ],
            "requests": [
                "Lay out a structured approach to {topic} because {nuance}.",
                "Someone jumped to conclusions on {topic} since {nuance}. How do I reset the reasoning?",
                "I need a step-by-step checklist for {topic} when {nuance}."
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Unclear", "Indulger", "Struggler", "Unclear"],
            "focus_label": "structured reasoning",
            "audit_every": 6,
            "applied": "Strategy"
        },
        "creation": {
            "name": "creation",
            "topics": [
                "writing a design one-pager", "drafting a decision memo", "proposing a service kickoff", "creating a retrospective plan",
                "shaping a product experiment", "building a facilitation outline", "documenting an incident review", "planning a workshop",
                "sketching a launch checklist", "creating a communication plan"
            ],
            "requests": [
                "Give me a concise template for {topic} acknowledging {nuance} without fluff.",
                "Help me propose {topic} that balances ambition with guardrails when {nuance}.",
                "How do I frame {topic} so it's auditable and decision-ready given {nuance}?"
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Unclear", "Indulger", "Struggler", "Unclear"],
            "focus_label": "structured creation",
            "audit_every": 6,
            "applied": "Strategy → Tactic"
        },
        "conversation": {
            "name": "conversation",
            "topics": [
                "resetting expectations without drama", "asking clarifying questions concisely", "closing a loop with accountability",
                "declining scope creep", "acknowledging tension in a meeting", "giving direct feedback", "handling interruptions",
                "naming tradeoffs without blame", "staying calm when challenged", "checking alignment before acting"
            ],
            "requests": [
                "Provide a short script for {topic} because {nuance}. Keep it grounded and direct.",
                "How do I respond to {topic} while avoiding emotional roleplay when {nuance}?",
                "Share a concise way to communicate during {topic} with {nuance}."
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Unclear", "Indulger", "Struggler", "Unclear"],
            "focus_label": "clear conversation",
            "audit_every": 7,
            "applied": "Strategy"
        },
        "efficiency": {
            "name": "efficiency",
            "topics": [
                "compressing status updates", "rewriting specs to essentials", "prioritizing tasks with constraints", "minimizing meetings",
                "creating bullet summaries", "shortening emails", "setting decision deadlines", "removing redundant steps",
                "clarifying blockers quickly", "tracking commitments transparently"
            ],
            "requests": [
                "Rewrite guidance for {topic} so it's crisp because {nuance}.",
                "How can I simplify {topic} without losing critical detail when {nuance}?",
                "Provide a minimal checklist for {topic} given {nuance}."
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Unclear", "Indulger", "Struggler", "Unclear"],
            "focus_label": "efficient communication",
            "audit_every": 8,
            "applied": "Tactic"
        },
        "relationships": {
            "name": "relationships",
            "topics": [
                "holding a boundary with family", "declining to enable a friend's bad habit", "addressing conflict at work",
                "repairing trust after a mistake", "saying no to gossip", "refusing manipulative apologies",
                "setting expectations in a collaboration", "responding to passive aggression", "owning harm without self-flagellation",
                "escalating unsafe dynamics"
            ],
            "requests": [
                "What should I say when facing {topic} and {nuance}?",
                "Give me steps to de-escalate while protecting boundaries in {topic} given {nuance}.",
                "How do I keep accountability visible during {topic} when {nuance}?"
            ],
            "nuance": base_nuance,
            "classifications": ["Struggler", "Indulger", "Unclear", "Struggler", "Indulger"],
            "focus_label": "relationships",
            "audit_every": 4,
            "applied": "Strategy → Tactic"
        }
    }
    return configs


def main():
    configs = build_domain_configs()
    data_dir = Path("data")
    for domain, cfg in configs.items():
        rows = generate_examples(cfg)
        write_jsonl(data_dir / f"{domain}.jsonl", rows)
        print(f"Wrote {len(rows)} examples to data/{domain}.jsonl")


if __name__ == "__main__":
    main()
