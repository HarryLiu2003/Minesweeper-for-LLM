"""
# Author: Yinghao Li
# Modified: February 17th, 2024
# ---------------------------------------
# Description: GPT api call and message cache.
"""

import json
import openai
import os # Import os for environment variables
from dotenv import load_dotenv # Import dotenv
from typing import Union
from .prompts import *
from .io import save_json

# Load .env file at module import time
load_dotenv()

# Models known not to support the 'system' role
# MODELS_WITHOUT_SYSTEM_ROLE = set() # No longer needed

# Models known not to support certain parameters (temp, top_p)
MODELS_WITH_LIMITED_PARAMS = {'o3-mini', 'o4-mini'} # Add o4-mini

class GPT:
    def __init__(
        self,
        resource_path: str,
        temperature: int = 0,
        max_tokens: int = 30000,
        top_p: float = 0.95,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: list[str] = None,
    ) -> None:
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.engine = load_gpt_resources(resource_path)

    def response(self, messages: Union[list[dict[str, str]], "MessageCache"]) -> str:
        """
        Generate response from GPT.
        """
        if isinstance(messages, MessageCache):
            # Get the raw message list from the cache
            messages_to_send = messages.content
        else:
            # Assume it's already a list
            messages_to_send = messages

        # Filter out system message if the model doesn't support it
        # if self.engine in MODELS_WITHOUT_SYSTEM_ROLE and raw_messages and raw_messages[0].get('role') == 'system':
        #     messages_to_send = raw_messages[1:]
        # else:
        #     messages_to_send = raw_messages # System message filtering removed

        # Handle instruct models (legacy completion API)
        if "instruct" in self.engine:
            prompt = messages_to_send[-1]["content"] # Assuming last message is user prompt
            r = openai.Completion.create(
                engine=self.engine,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stop=self.stop,
            )
            return r["choices"][0]["text"]
        # Handle chat models (ChatCompletion API)
        else:
            # Prepare parameters, excluding those not supported by certain models
            params = {
                "messages": messages_to_send,
                "model": self.engine,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty,
                "stop": self.stop,
            }
            # Add the correct max tokens parameter based on model type
            if self.engine.startswith('o'): 
                params["max_completion_tokens"] = self.max_tokens
            else:
                params["max_tokens"] = self.max_tokens
            
            # Conditionally add parameters not supported by some o-series models
            if self.engine not in MODELS_WITH_LIMITED_PARAMS:
                 params["temperature"] = self.temperature
                 params["top_p"] = self.top_p # Include top_p only if temp is also included
            # else: # For o3-mini and o4-mini, omit both temperature and top_p
                 # pass

            r = openai.ChatCompletion.create(**params) 

            return r["choices"][0]["message"]["content"]

    def __call__(self, messages: Union[list[dict[str, str]], "MessageCache"]) -> str:
        return self.response(messages)


class MessageCache:
    def __init__(self, system_role: str = None) -> None:
        self.system_role = (
            system_role
            if system_role is not None
            else "You are a helpful assistant who is good at playing Minesweeper."
        )
        self.message_cache = list()
        self.add_message("system", self.system_role)

    def add_message(self, role: str, content: str) -> None:
        self.message_cache.append(
            {"role": role, "content": content},
        )

    def add_user_message(self, content: str) -> None:
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        self.add_message("assistant", content)

    @property
    def content(self) -> list[dict[str, str]]:
        return self.message_cache

    def __str__(self) -> str:
        message = ""
        for msg in self.message_cache:
            message += f">> {msg['role'].upper()}:\n{msg['content']}\n\n"
        return message

    def __repr__(self) -> str:
        return self.__str__()

    def print(self) -> None:
        print(self.__str__())

    def save(self, path: str) -> None:
        save_json(self.message_cache, path, collapse_level=2)

    def load(self, path: str) -> "MessageCache":
        with open(path, "r", encoding="utf-8") as f:
            self.message_cache = json.load(f)
        return self

    def save_plain(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.__str__())


def load_gpt_resources(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        resource_dict = json.load(f)

    # Process the dictionary *before* setting attributes
    processed_dict = {}
    for k, v in resource_dict.items():
        if k == "api_key" and v == "ENV:OPENAI_API_KEY":
            # If placeholder found, fetch from environment
            env_key = os.getenv("OPENAI_API_KEY")
            if not env_key:
                raise ValueError("API key placeholder found in config, but OPENAI_API_KEY environment variable is not set.")
            processed_dict[k] = env_key
        else:
            # Otherwise, use the value directly
            processed_dict[k] = v

    # Set attributes using the processed dictionary
    for k, v in processed_dict.items():
        if k != "engine":
            # Ensure value is not None before setting, as openai lib might not like None for some attrs
            if v is not None: 
                setattr(openai, k, v)

    # Check if api_key was actually set (either from JSON or Env)
    if not hasattr(openai, 'api_key') or not openai.api_key:
         raise ValueError(f"OpenAI API key was not configured. Check {path} or the OPENAI_API_KEY environment variable.")

    engine = processed_dict.get("engine")
    if not engine:
         raise ValueError(f"Engine/Model ID not found in configuration file: {path}")

    return engine
