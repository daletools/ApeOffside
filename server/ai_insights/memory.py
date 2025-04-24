# Handles loading and updating session-based conversation memory.

SESSION_KEY = "conversation_history"


def get_conversation(session):

    # Retrieve the conversation history from the session.

    return session.get(SESSION_KEY, [])


def add_to_conversation(session, role, message):

    # Append a message to the conversation history and save it back to the session.

    conversation = get_conversation(session)
    conversation.append({"role": role, "message": message})
    session[SESSION_KEY] = conversation
    session.modified = True
    return conversation
