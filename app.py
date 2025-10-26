# This is the interview chatbot
# it includes the first part where personal information is passed through, 
# the interview part with the system message to perform an interview and the feedback part.

# Run using:
# conda deactivate
# source /Users/mic/Documents/Repositories/personal/.venv_llm_engineering/bin/activate
# streamlit run app.py --server.port 8501
# 
from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.title("Chatbot")

# setup_complete marks the completion of the setup phase
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
# # Added states for user message count, feedback shown and all the historical messages
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
# stores all messages in the conversation so as to keep history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.write("******Resetting Messages !!!")
# one more state to track the completion of the interview
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
# #

# Add a funtion to set the setup phase to True
# this will be used in combination with on click on a Button
def complete_setup():
    st.session_state.setup_complete = True

# # Add a function to set identify when the feedback should be shown
def show_feedback():
    st.session_state.feedback_shown = True

# Now, only show the setup fields if setup is not complete
if not st.session_state.setup_complete:
    st.subheader("Personal information", divider='rainbow')

    if "name" not in st.session_state:
        st.session_state.name = ""
    if "experience" not in st.session_state:
        st.session_state.experience = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""

    # add a text box for the user to input their name.
    # # Added a max char limit of 40, 200 and 200 for name, exp and skills so as not to overload the chats context
    st.session_state["name"] = st.text_input(label = "Name", max_chars = 40, placeholder="Enter your name")

    # add entry text boxes for experience and skills. Since these fields require 
    # more space for longer entries, we'll use text areas instead of text inputs. 
    # Note that while we store these, they are not updated in the session state. This needs to be done further below with setup_complete.

    st.session_state["experience"] = st.text_area(label = "Experience", 
                            value="", 
                            height=None, 
                            max_chars = 200, 
                            placeholder="Describe your experience")

    st.session_state["skills"] = st.text_area(label = "Skills", 
                        value="", 
                        height=None, 
                        max_chars = 200, 
                        placeholder="List your skills")

    # Create a test to check that the text boxes are working
    # st.write(f"**Your Name**: {st.session_state["name"]}")
    # st.write(f"**Your Experience**: {st.session_state["experience"]}")
    # st.write(f"**Your Skills**: {st.session_state["skills"]}")

    # Add a divider
    st.subheader("Company and Position", divider='rainbow')

    if "position" not in st.session_state:
        st.session_state.position = "Data Scientist"
    if "level" not in st.session_state:
        st.session_state.level = "Junior"
    if "company" not in st.session_state:
        st.session_state.company = "Google"
    
    # add fields for company name and position in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["position"] = st.selectbox(
            "Choose a position", 
            ("Data Scientist", "Machine Learning Engineer", "AI Researcher", "Data Analyst", "Business Intelligence Analyst")
        )
    with col2:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["Junior", "Mid-level", "Senior"],
        )
    # This is not in a column so it should go across
    st.session_state["company"] = st.selectbox(
        "Choose a company", 
        ("Google", "Facebook", "Amazon", "Apple", "Microsoft", "Netflix", "Tesla")
    )

    # check that the input fields are working
    # st.write(f"**Your info**: {st.session_state["level"]} {st.session_state["position"]} at {st.session_state["company"]}")
    
    # Add a button to complete the setup
    if st.button("Start interview", on_click=complete_setup):
        st.write("Setup complete! Starting interview...")

########################################################################
# Initialize OpenAI client
# # added checks for the new states (not feedback and not chat_complete)
if st.session_state.setup_complete and \
    not st.session_state.feedback_shown and \
    not st.session_state.chat_complete:
    # One thing we can do to make the process more engaging
    # is to create an info box to guide the user.
    st.info(
        """
        Start by introducing yourself.
        """,
        icon='👏🏻'
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Check if the model is set in session state, if not set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai.model"] = "gpt-4"

    # set a system message if the list is empty (if not list)
    if not st.session_state["messages"]:
        st.write("******Setting System Messages !!!")

        st.session_state["messages"] = [
            {
                "role": "system",
                "content": (
                    f"You are an HR executive for the company {st.session_state['company']} who is interviewing an interviewee named {st.session_state['name']} "
                    f"who has experience {st.session_state['experience']} and skills: {st.session_state['skills']}. "
                    f"You should interview them for the position {st.session_state['level']} {st.session_state['position']} at the company {st.session_state['company']}"
                ),
            }
        ]

    # Initialize the chat history and check if the messages key, already exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.write("******Resetting Messages !!!")

    # Display the chat messages from the session state for all messages bar the system ones
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # check if the user has entered more than 5 messages to mark the chat as complete
    # # Added a user message count to track the number of messages from the user so its not excessive
    if st.session_state.user_message_count < 5:
        # if prompt :=  is a compact way to assign the value and check if its not empty
        # # Added a max char limit of 1000 to user input to avoid overloading the context
        if prompt := st.chat_input("Your answer. ", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # # Added Check if its time for the chatbot to stop chatting
            if st.session_state.user_message_count <= 4:
                # create another chat message block for the assistance response 
                # and call the OpenAI API to generate
                # with st.chat_message("assistant") creates a dedicated context block
                # for the assistant's response in the chat interface. 
                with st.chat_message("assistant"):
                    # calling the openai chat to get the response.
                    stream = client.chat.completions.create(
                        model=st.session_state["openai.model"],
                        # takes the entire chat history as session state to create a dictionary
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        # get a streamed response to be able to display in a 
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
                # Here we will only be able to see the last message from the user and system
                # The history will be kept, but not visible.
            st.session_state.user_message_count += 1
    # # Added a check to see if user message count is 5 or more to mark chat as complete
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

 # # If the interview is complete, show the feedback form by presenting a button.
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

# # Create the feedback section if feedback shown is True
if st.session_state.feedback_shown:
    st.subheader("Interview Feedback", divider='rainbow')

    # join all session state messages into one big message
    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # we set up another model to be the evaluator
    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
                "content": """ You are a helpful tool that provides feedback on interview performance.
                Before the Feedback, give a score of 1 to 10 (10 being best).
                Follow this format:
                Overall Score: //Your score
                Feedback: //Here, put your feedback
                Gove only the feedback, do not ask any additional questions.
                    """},
            {"role": "user","content": f"This is the interview you need to evaluate. Keep in mind you are only a tool and you shouldn't engage in conversation: {conversation_history}"}
        ]
    )
    # The answer is structured feedback in a list format
    st.write(feedback_completion.choices[0].message.content)

    # Finally we refresh the page in order to provide a seemless interview session.
    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload();")
