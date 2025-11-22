# import streamlit as st
# from langgraph_backend import chatbot
# from langchain_core.messages import HumanMessage, AIMessage
# import uuid # to generate random new thread id

# # **************************************** utility functions *************************

# def generate_thread_id():
#     thread_id = uuid.uuid4()
#     return thread_id

# def reset_chat():
#     thread_id = generate_thread_id()
#     st.session_state['thread_id'] = thread_id
#     add_thread(st.session_state['thread_id'])
#     st.session_state['message_history'] = []

# def add_thread(thread_id):
#     if thread_id not in st.session_state['chat_threads']:
#         st.session_state['chat_threads'].append(thread_id)

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
#     # Check if messages key exists in state values, return empty list if not
#     return state.values.get('messages', [])


# # **************************************** Session Setup ******************************
# if 'message_history' not in st.session_state:
#     st.session_state['message_history'] = []

# if 'thread_id' not in st.session_state:
#     st.session_state['thread_id'] = generate_thread_id()

# if 'chat_threads' not in st.session_state:
#     st.session_state['chat_threads'] = []

# add_thread(st.session_state['thread_id'])


# # **************************************** Sidebar UI *********************************

# st.sidebar.title('LangGraph Chatbot')

# if st.sidebar.button('New Chat'):
#     reset_chat()

# st.sidebar.header('My Conversations')

# # for thread_id in st.session_state['chat_threads'][::-1]:
# #     if st.sidebar.button(str(thread_id)):
# #         st.session_state['thread_id'] = thread_id
# #         messages = load_conversation(thread_id)

# #         temp_messages = []

# #         for msg in messages:
# #             if isinstance(msg, HumanMessage):
# #                 role='user'
# #             else:
# #                 role='assistant'
# #             temp_messages.append({'role': role, 'content': msg.content})

# #         st.session_state['message_history'] = temp_messages
# for thread_id in st.session_state['chat_threads'][::-1]:
#     messages = load_conversation(thread_id)
    
#     # Get a short preview text from the first user message (if exists)
#     if messages:
#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 preview_text = msg.content[:40] + "..." if len(msg.content) > 40 else msg.content
#                 break
#         else:
#             preview_text = "(Empty conversation)"
#     else:
#         preview_text = "(New chat)"

#     # Display preview button
#     if st.sidebar.button(preview_text, key=f"btn_{thread_id}"):
#         st.session_state['thread_id'] = thread_id
#         temp_messages = []

#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 role = 'user'
#             else:
#                 role = 'assistant'
#             temp_messages.append({'role': role, 'content': msg.content})

#         st.session_state['message_history'] = temp_messages

# # **************************************** Main UI ************************************

# # loading the conversation history
# for message in st.session_state['message_history']:
#     with st.chat_message(message['role']):
#         st.text(message['content'])

# user_input = st.chat_input('Type here')

# if user_input:

#     # first add the message to message_history
#     st.session_state['message_history'].append({'role': 'user', 'content': user_input})
#     with st.chat_message('user'):
#         st.text(user_input)

#     CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

#      # first add the message to message_history
#     with st.chat_message("assistant"):
#         def ai_only_stream():
#             for message_chunk, metadata in chatbot.stream(
#                 {"messages": [HumanMessage(content=user_input)]},
#                 config=CONFIG,
#                 stream_mode="messages"
#             ):
#                 if isinstance(message_chunk, AIMessage):
#                     # yield only assistant tokens
#                     yield message_chunk.content

#         ai_message = st.write_stream(ai_only_stream())

#     st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

# version 2

import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid  # to generate random new thread id

# **************************************** utility functions *************************

def generate_thread_id():
    return str(uuid.uuid4()) 

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def delete_thread(thread_id):
    """Remove the thread from session state and its saved conversation."""
    if thread_id in st.session_state['chat_threads']:
        st.session_state['chat_threads'].remove(thread_id)
    if st.session_state.get('thread_id') == thread_id:
        reset_chat()
    st.success("Chat deleted!")


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

# ✅ Store chat titles separately
if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    st.rerun()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    messages = load_conversation(thread_id)
    
    # Title or preview text
    title = st.session_state['chat_titles'].get(thread_id)

    if not title:  # If title not manually set yet, use first user message
        if messages:
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    title = msg.content[:20] + "..." if len(msg.content) > 20 else msg.content
                    break
            else:
                title = "(Empty conversation)"
        else:
            title = "(New chat)"

    # Sidebar row layout
    cols = st.sidebar.columns([6, 2])  # Chat name + delete

    with cols[0]:
        if st.button(title, key=f"btn_{thread_id}"):
            st.session_state['thread_id'] = thread_id
            temp_messages = []
            for msg in messages:
                role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
                temp_messages.append({'role': role, 'content': msg.content})
            st.session_state['message_history'] = temp_messages

    with cols[1]:
        if st.button("🗑️", key=f"del_{thread_id}", help="Delete this chat"):
            delete_thread(thread_id)
            st.rerun()


# **************************************** Main UI ************************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # Add user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # ✅ Automatically set chat title when first message is received
    thread_id = st.session_state['thread_id']
    if thread_id not in st.session_state['chat_titles'] or st.session_state['chat_titles'][thread_id] in ["(New chat)", None]:
        st.session_state['chat_titles'][thread_id] = user_input[:20] + "..." if len(user_input) > 20 else user_input

    CONFIG = {'configurable': {'thread_id': thread_id}}

    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})


# version 3
    
# import streamlit as st
# from langchain.schema import HumanMessage, AIMessage
# import uuid
# from langgraph_backend import chatbot

# # Dummy conversation loader/saver
# def load_conversation(thread_id):
#     return st.session_state.get("conversations", {}).get(thread_id, [])

# def save_conversation(thread_id, messages):
#     st.session_state["conversations"][thread_id] = messages

# # Initialize session state
# if "chat_threads" not in st.session_state:
#     st.session_state["chat_threads"] = []
# if "thread_id" not in st.session_state:
#     st.session_state["thread_id"] = None
# if "conversations" not in st.session_state:
#     st.session_state["conversations"] = {}
# if "titles" not in st.session_state:
#     st.session_state["titles"] = {}

# st.sidebar.title("💬 Chat History")

# # --- Sidebar for threads ---
# for thread_id in st.session_state["chat_threads"][::-1]:
#     messages = load_conversation(thread_id)

#     # Get preview text (first user message)
#     if messages:
#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 preview_text = msg.content[:40] + "..." if len(msg.content) > 40 else msg.content
#                 break
#         else:
#             preview_text = "(Empty conversation)"
#     else:
#         preview_text = "(New chat)"

#     # Get saved title (if renamed automatically)
#     title = st.session_state["titles"].get(thread_id, preview_text)

#     cols = st.sidebar.columns([6, 1])
#     with cols[0]:
#         if st.button(title, key=f"btn_{thread_id}"):
#             st.session_state["thread_id"] = thread_id
#             temp_messages = []
#             for msg in messages:
#                 role = "user" if isinstance(msg, HumanMessage) else "assistant"
#                 temp_messages.append({"role": role, "content": msg.content})
#             st.session_state["message_history"] = temp_messages

#     with cols[1]:
#         # Delete button
#         if st.button("🗑️", key=f"del_{thread_id}"):
#             st.session_state["chat_threads"].remove(thread_id)
#             st.session_state["conversations"].pop(thread_id, None)
#             st.session_state["titles"].pop(thread_id, None)
#             st.rerun()

# st.sidebar.divider()

# # --- Main chat area ---
# if st.button("➕ New Chat"):
#     new_id = str(uuid.uuid4())
#     st.session_state["thread_id"] = new_id
#     st.session_state["chat_threads"].append(new_id)
#     st.session_state["message_history"] = []
#     st.session_state["titles"][new_id] = "(New Chat)"
#     st.rerun()

# st.title("💡 AI Chatbot")

# if "thread_id" in st.session_state and st.session_state["thread_id"]:
#     thread_id = st.session_state["thread_id"]

#     # Display message history
#     for msg in st.session_state.get("message_history", []):
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # --- Chat input ---
#     if prompt := st.chat_input("Type your message..."):
#         st.session_state["message_history"].append({"role": "user", "content": prompt})

#         # ✅ Auto-rename chat after first user message
#         if st.session_state["titles"].get(thread_id, "(New Chat)") == "(New Chat)":
#             st.session_state["titles"][thread_id] = prompt[:40] + ("..." if len(prompt) > 40 else "")

#         # Dummy AI response
#         with st.chat_message("assistant"):
#             def ai_only_stream():
#                 for message_chunk, metadata in chatbot.stream(
#                     {"messages": [HumanMessage(content=prompt)]},
#                     config={'configurable': {'thread_id': thread_id}},
#                     stream_mode="messages"
#                 ):
#                     if isinstance(message_chunk, AIMessage):
#                         yield message_chunk.content

#             ai_message = st.write_stream(ai_only_stream())

#         st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

#         # Save conversation
#         messages = []
#         for msg in st.session_state["message_history"]:
#             if msg["role"] == "user":
#                 messages.append(HumanMessage(content=msg["content"]))
#             else:
#                 messages.append(AIMessage(content=msg["content"]))
#         save_conversation(thread_id, messages)

#         st.rerun()
# else:
#     st.info("Click **New Chat** to start a conversation.")
