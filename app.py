from datetime import datetime

import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import random
from constants import (question_1,
                       question_2,
                       question_3,
                       )

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


def update_text():
    st.session_state.name = st.session_state.name_input


def increment_counter():
    st.session_state['counter'] += 1


def push_to_bigquery(rows: dict,
                     project_id: str = "healthy-dragon-300820",
                     dataset_id: str = "success_enabler_search_feedback",
                     ):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_credentials"]
    )
    try:
        client = bigquery.Client(credentials= credentials, project=project_id)
        table_id: str = "se_app_feedback"
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            st.write(f"Errors occurred while inserting rows: {errors}")
    except Exception as e:
        st.write(e)



def get_random_row(df: pd.DataFrame) -> pd.Series:
    # Always picking a new row after submission.
    remaining_indices = df.index.difference(st.session_state.get('selected_indices', set()))
    if not remaining_indices.empty:
        selected_index = random.choice(remaining_indices)
        st.session_state['selected_row_index'] = selected_index
    else:
        st.session_state['selected_row_index'] = None  # No more rows to select.

    if st.session_state['selected_row_index'] is not None:
        selected_row = df.loc[st.session_state['selected_row_index']]
    else:
        selected_row = None
    return selected_row


def format_func(option):
    return labels[options.index(option)]


st.markdown("<div class='title'>Success Enabler Search & Discovery Feedback Form</div>", unsafe_allow_html=True)

if 'name' not in st.session_state:
    st.session_state.name = ''

st.markdown("<div class='email-input-container'>", unsafe_allow_html=True)
name = st.text_input("Name", key="name_input", help="Please enter your first and last name",
                      value=st.session_state.name, on_change=update_text)
st.markdown("</div><div class='spacer'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <p>You will be given a search query followed by the results. Provide a rating and feedback, click 'submit' and you will be given another to rate. When you are finished, simply close this page</p>
    """,
    unsafe_allow_html=True
)

df = import_dataframe()

if 'selected_indices' not in st.session_state:
    st.session_state['selected_indices'] = set()
# Exclude already selected rows
remaining_indices = df.index.difference(st.session_state['selected_indices'])
df = df.loc[remaining_indices]

if df.empty:
    st.markdown("<div class='main-content'>All rows have been reviewed!</div>", unsafe_allow_html=True)
elif st.session_state.name != '':
    if 'counter' not in st.session_state:
        st.session_state['counter'] = 0
    col1, col2 = st.columns([1, 2])
    selected_row = get_random_row(df)
    with col1:
        st.subheader(f"You've submitted {st.session_state.counter} times")
        if isinstance(selected_row['Employer'], str):
            employer = selected_row["Employer"]
        else:
            employer = "None"
        if isinstance(selected_row['Success Enablers'], str):
            se = selected_row['Success Enablers']
            success_enablers_list = str(se).split(',')
            success_enablers = [f"{i + 1}. {item}" for i, item in enumerate(success_enablers_list)]
        else:
            success_enablers = "None"
        query = selected_row['Input']
        st.markdown("**Query**:  " + query)
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**Success Enablers Returned**:")
        st.write("\n".join(success_enablers))
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**Employer**: " + employer)
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**AI Summary**: ")
        st.write(selected_row["Summary"])
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**Journeys:**")
        if isinstance(selected_row['Journeys'], str):
            journey = selected_row["Journeys"]
            journeys_list = str(journey).split(',')
            journeys = [f"{i + 1}. {item}" for i, item in enumerate(journeys_list)]
            journeys = "\n".join(journeys)
        else:
            journeys = "None"
        st.write(journeys)
        with col2:
            with st.form("feedback_form", clear_on_submit=True, enter_to_submit=False):
                st.markdown(question_1)
                options = [1, -1, 0]
                labels = ["Yes", "No", "Neutral"]
                relevancy_rating = st.radio(
                "Select your answer:",
                options = options, format_func = format_func,
                key="relevancy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                relevancy_input = st.text_area("Enter your thoughts here", key="relevancy_input",
                                               )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                st.markdown(question_2)
                labels = ["No", "Yes", "Neutral"]
                accuracy_rating = st.radio(
                    "Select your answer:",
                    options=options, format_func = format_func,
                    key="accuracy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                accuracy_input = st.text_area("Enter your thoughts here", key="accuracy_input",
                                              )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                st.markdown(question_3)
                labels = ["Yes", "No", "Neutral"]
                summary_rating = st.radio(
                    "Select your answer:",
                    options=options, format_func = format_func,
                    key="summary")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                summary_input = st.text_area("Enter your thoughts here", key="summary_input",
                                             )

                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                current_datetime = datetime.now()
                time = current_datetime.strftime("%Y-%m-%d %H:%M")
                user_feedback = [{"Query": query,
                                 "Success Enablers": ', '.join(success_enablers),
                                 "Employer": employer,
                                 "Summary": selected_row['Summary'],
                                 "Journeys": journeys,
                                 "Q1 Relevancy Rating": relevancy_rating,
                                 "Q1 Relevancy Comments": relevancy_input,
                                 "Q2 Accuracy Rating": accuracy_rating,
                                 "Q2 Accuracy Comments": accuracy_input,
                                 "Q3 Summary Rating": summary_rating,
                                 "Q3 Summary Comments": summary_input,
                                  "Name": name,
                                  "Time Submitted": time,}]
                st.write(selected_row)
                submitted = st.form_submit_button("Submit", help="Click to submit your feedback",
                                    on_click=increment_counter)
                if submitted:
                    push_to_bigquery(user_feedback)
                    st.markdown(f"<div class='main-content'>Thanks! Try Another!</div>", unsafe_allow_html=True)
                    # Add the selected index to the set of reviewed indices
                    st.session_state['selected_indices'].add(st.session_state['selected_row_index'])



else:
    st.subheader("Enter Your Name To Get Started")

    
