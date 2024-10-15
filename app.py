import streamlit as st
import pandas as pd
import random

st.markdown(
    """
    <style>
    .title {
        font-size: 2.5em;
        color: #000000;
        text-align: center;
    }
    .main-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
    }
    .submit-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1.2em;
    }
    .submit-button:hover {
        background-color: #45a049;
    }
        .spacer {
        margin-top: 40px; 
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def import_dataframe(filepath: str = "./search_output_for_eval_preprocessed.csv") -> pd.DataFrame:
    data = pd.read_csv(filepath)
    return data


def get_random_row(df: pd.DataFrame) -> pd.Series:
    selected_index = random.choice(df.index)
    selected_row = df.loc[selected_index]

    # Cache the selected row index to ensure it won't be selected again
    cached_indices = st.session_state.get('selected_indices', set())
    cached_indices.add(selected_index)
    st.session_state['selected_indices'] = cached_indices

    return selected_row


st.markdown("<div class='title'>Success Enabler Search & Discovery Feedback Form</div>", unsafe_allow_html=True)

st.markdown("<div class='email-input-container'>", unsafe_allow_html=True)
email = st.text_input("Email", key="email", help="Please enter your email address")
st.markdown("</div><div class='spacer'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class='main-content'>
    <p>You will be given a search query followed by the results. Provide a rating and feedback, click 'submit' and you will be given another to rate. When you are finished, simply exit this page.</p>
    </div>
    """,
    unsafe_allow_html=True
)

df = import_dataframe()

# Exclude already selected rows
if 'selected_indices' in st.session_state:
    remaining_indices = df.index.difference(st.session_state['selected_indices'])
    df = df.loc[remaining_indices]

if df.empty:
    st.markdown("<div class='main-content'>All rows have been reviewed!</div>", unsafe_allow_html=True)
else:
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_row = get_random_row(df)
        # st.markdown("<div class='main-content'>", unsafe_allow_html=True)
        st.markdown("**Query**: " + selected_row['Input'])
        st.markdown("**Success Enablers Returned**:")
        success_enablers_list = str(selected_row['Success Enablers']).split(',')
        success_enablers = [f"{i + 1}. {item}" for i, item in enumerate(success_enablers_list)]
        st.write("\n".join(success_enablers))
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**AI Summary**: ")
        st.write(selected_row["Summary"])
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        employer = selected_row["Employer"]
        st.markdown("**Employer**: " + str(selected_row["Employer"]))
        st.markdown("**Journeys**")
        journey = selected_row["Journeys"]
        if isinstance(journey, str):
            journeys_list = str(journey).split(',')
            journeys = [f"{i + 1}. {item}" for i, item in enumerate(journeys_list)]
            st.write("\n".join(journeys))
        else:
            st.write(journey)
        with col2:
            with st.form("feedback_form"):
                st.markdown("1. **Are the Success Enablers relevant to the query?** ")
                relevancy_rating = st.radio(
                "Select your answer:",
                options = ["Yes", "No", "Neutral"],
                index = None, key="relevancy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                relevancy_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                st.markdown("2. **Are there missing Success Enablers (even if you are not sure we offer them)?**")
                accuracy_rating = st.radio(
                    "Select your answer:",
                    options=["Yes", "No", "Neutral"],
                    index=None, key="accuracy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                accuracy_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                if isinstance(employer, str):
                    st.markdown("**Employer: If the summary mentions resources, does it make clear what the user should do?**")
                    summary_rating = st.radio(
                        "Select your answer:",
                        options=["Yes", "No", "Neutral"],
                        index=None, key="summary")
                    st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                    summary_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                else:
                    st.markdown("**Summary: Does the summary answer the query in a useful way and fulfill the user's intent?**")
                    summary_rating = st.radio(
                        "Select your answer:",
                        options=["Yes", "No", "Neutral"],
                        index=None, key="summary")
                    st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                    summary_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                submitted = st.form_submit_button("Submit", help="Click to submit your feedback", on_click=None)
                if submitted:
                    st.markdown(f"<div class='main-content'>Form submitted</div>", unsafe_allow_html=True)



    
