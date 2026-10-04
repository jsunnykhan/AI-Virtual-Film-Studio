import os

import litellm

from shared.core.settings import get_settings


def configure_tracing() -> None:
    settings = get_settings()
    enabled = settings.langchain_tracing_v2 and bool(settings.langchain_api_key.strip())

    os.environ["LANGCHAIN_TRACING_V2"] = str(enabled).lower()
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
    os.environ["LANGSMITH_API_KEY"] = settings.langchain_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langchain_project
    os.environ["LANGSMITH_BASE_URL"] = settings.langchain_endpoint

    callbacks = litellm.success_callback
    if callbacks is None:
        callback_list = []
    elif isinstance(callbacks, str):
        callback_list = [callbacks]
    else:
        callback_list = list(callbacks)

    if enabled and "langsmith" not in callback_list:
        callback_list.append("langsmith")
    elif not enabled:
        callback_list = [
            callback for callback in callback_list if callback != "langsmith"
        ]

    litellm.success_callback = callback_list
