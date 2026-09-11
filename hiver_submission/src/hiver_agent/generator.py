
def draft_reply(query, intent, evidence, escalate):
    if not evidence:
        return ("I’m sorry you’re running into this. We’d like to take a closer look "
                "at your issue. Please contact Apple Support for further help." )
    historical=evidence[0]["response"].strip()
    if escalate:
        return ("Thanks for explaining the issue. Based on similar AppleSupport cases, "
                "this looks like it may need account/device-specific help. "
                "Please contact Apple Support so a specialist can take a closer look. "
                f"Relevant historical guidance: {historical}")
    return (f"Thanks for reaching out. This looks related to {intent.replace('_',' ')}. "
            f"Based on a similar AppleSupport case, a relevant next step was: {historical}")
