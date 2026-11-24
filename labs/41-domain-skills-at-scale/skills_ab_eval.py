"""A/B evaluation: does a skill actually help? Run each prompt with and without skills, then have a
judge compare the two answers blind (order randomized). Reports the skills win rate.

    python skills_ab_eval.py prompts.txt          # one prompt per line
"""
import json
import random
import sys

from pydantic import BaseModel
from strands import Agent, AgentSkills

MODEL = "global.anthropic.claude-sonnet-4-6"


class Verdict(BaseModel):
    winner: str          # "A", "B" or "tie"
    reason: str


def answer(prompt: str, with_skills: bool) -> str:
    plugins = [AgentSkills(skills="./skills/")] if with_skills else []
    return str(Agent(model=MODEL, plugins=plugins, callback_handler=None)(prompt))


judge = Agent(model=MODEL, callback_handler=None, system_prompt=(
    "You are a strict senior reviewer. Compare two answers to the same question for correctness, rigor, "
    "use of an appropriate method, and actionable specificity. Ignore length and style. Reply A, B or tie."))

if __name__ == "__main__":
    prompts = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    wins = ties = 0
    for p in prompts:
        skilled, plain = answer(p, True), answer(p, False)
        flip = random.random() < 0.5
        a, b = (skilled, plain) if not flip else (plain, skilled)
        v = judge(f"QUESTION:\n{p}\n\nANSWER A:\n{a}\n\nANSWER B:\n{b}", structured_output_model=Verdict).structured_output
        skilled_won = (v.winner == "A") != flip if v.winner in ("A", "B") else None
        wins += skilled_won is True
        ties += skilled_won is None
        print(json.dumps({"prompt": p[:60], "skills_won": skilled_won, "reason": v.reason[:160]}))
    n = len(prompts)
    print(json.dumps({"n": n, "skills_win_rate": round(wins / max(n - ties, 1), 2), "ties": ties}))
