import os
import shutil
from datetime import datetime
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
except ImportError:
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.prompts import MessagesPlaceholder
from openai import OpenAI, BadRequestError

from google.cloud import storage
from google.oauth2.service_account import Credentials
)

MODEL_SELECTED = "gpt-5-mini"
FALLBACK_MODEL = "gpt-4o-mini"

st.title("Beer Game Assistant")
st.write(
)

openai_api_key = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(model=MODEL_SELECTED, api_key=openai_api_key)
openai_client = OpenAI(api_key=openai_api_key)

# Initializing GCP credentials and bucket details
credentials_dict = {
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in value.strip())


def generate_assistant_text(messages_to_send, system_text):
    response_input = [{"role": "system", "content": system_text}]
    response_input.extend(
        {"role": msg["role"], "content": msg["content"]}
        for msg in messages_to_send
        if msg["role"] in ("user", "assistant")
    )

    try:
        response = openai_client.responses.create(
            model=MODEL_SELECTED,
            input=response_input,
        )
        return response.output_text
    except BadRequestError as exc:
        st.sidebar.warning(
            f"Model '{MODEL_SELECTED}' failed for this request. Retrying with '{FALLBACK_MODEL}'."
        )
        fallback_response = openai_client.responses.create(
            model=FALLBACK_MODEL,
            input=response_input,
        )
        return fallback_response.output_text
    except Exception as exc:
        raise RuntimeError(f"Assistant request failed: {exc}") from exc


def save_conversation_to_gcp(messages_to_save, mode_key, pid, role):
    if not pid or not role:
        return None, "missing_required_fields"
    with st.chat_message("user"):
        st.markdown(user_input)

    history_messages = []
    for msg in messages[:-1]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_messages.append(AIMessage(content=msg["content"]))

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt_template | llm
    llm_response = chain.invoke({"history": history_messages, "input": user_input})
    assistant_text = llm_response.content
    try:
        assistant_text = generate_assistant_text(messages, system_prompt)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    with st.chat_message("assistant"):
        st.write_stream(response_generator(response=assistant_text))
