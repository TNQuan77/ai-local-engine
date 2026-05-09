from skills.definitions import SKILLS


def get_skill_prompt(skill: str, working_dir: str, args: str = "") -> str | None:
    """
    Build the system prompt for a given skill.
    Returns None if the skill is unknown.
    """
    definition = SKILLS.get(skill)
    if not definition:
        return None
    return definition["prompt_template"].format(
        working_dir=working_dir,
        args=args,
    )


def list_skills() -> list[dict]:
    return [
        {"name": name, "description": d["description"]}
        for name, d in SKILLS.items()
    ]
