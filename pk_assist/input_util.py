def should_exit(user_input):
    return user_input.lower() in {"exit", "quit", "bye"}

def should_list(user_input):
    return user_input.lower() in {"list", "list notes"}

def should_show(user_input):
    return user_input.lower().startswith("show ")

def should_search(user_input):
    return user_input.lower().startswith("search") or user_input.lower().startswith("query")

def should_retrieve(user_input):
    return user_input.lower().startswith("retrieve")

def should_ask(user_input):
    return user_input.lower().startswith("ask")

def should_evaluate(user_input):
    return user_input.lower().startswith("evaluate")