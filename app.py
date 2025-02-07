from datetime import datetime
import os

import streamlit as st
import pandas as pd
from google.cloud import bigquery
import s3fs
from google.oauth2 import service_account
import random
from constants import (question_1,
                       question_2,
                       question_3,
                       question_4,
                       )
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
s3_data_path = os.getenv('dataset_uri')

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


# @st.cache_data
# def import_dataframe(filepath: str = "./search_eval.csv") -> pd.DataFrame:
#     data = pd.read_csv(filepath)
#     return data


def update_text():
    st.session_state.name = st.session_state.name_input


def update_query_list(questions: dict):
    st.session_state.query_list.append(questions)
    st.session_state['counter'] += 1

@st.cache_data
def read_s3_file_to_dataframe(s3_path = s3_data_path):
    s3 = s3fs.S3FileSystem(key=aws_access_key, secret=aws_secret_key)
    dataframe = pd.read_csv(s3.open(s3_path, 'r'))
    return dataframe

def save_dataframe_to_s3(dataframe, s3_path = s3_data_path):
    s3 = s3fs.S3FileSystem(key=aws_access_key, secret=aws_secret_key)
    with s3.open(s3_path, 'w') as f:
        dataframe.to_csv(f, index=False)


def push_to_bigquery(queries: dict,
                     user_feedback: dict,
                     project_id: str = "healthy-dragon-300820",
                     dataset_id: str = "success_enabler_search_feedback",
                     table_id: str = "se_app_feedback_v2",
                     ):
    merged_list = [{**queries, **user_feedback}]
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_credentials"]
    )
    try:
        client = bigquery.Client(credentials= credentials, project=project_id)
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        errors = client.insert_rows_json(table_ref, merged_list)
        if errors:
            st.write(f"Errors occurred while inserting rows: {errors}")
    except Exception as e:
        st.write(e)


def get_random_row(df: pd.DataFrame) -> tuple[pd.Series, int]:
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
    return selected_row, selected_index


def format_func(option):
    return labels[options.index(option)]


st.markdown("<div class='title'>Success Enabler Search & Discovery Feedback Form</div>", unsafe_allow_html=True)

if 'name' not in st.session_state:
    st.session_state.name = ''
if 'query_list' not in st.session_state:
    st.session_state.query_list = []

st.markdown("<div class='email-input-container'>", unsafe_allow_html=True)
name = st.text_input("Name", key="name_input", help="Please enter your first and last name",
                      value=st.session_state.name, on_change=update_text)
st.markdown("</div><div class='spacer'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <p>You will be given a search query followed by the results. Provide a rating and feedback, click 'submit' and you will be given another to rate. When you are finished, simply exit the page</p>
    """,
    unsafe_allow_html=True
)

df = read_s3_file_to_dataframe()

if 'selected_indices' not in st.session_state:
    st.session_state['selected_indices'] = set()
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

# Exclude already selected rows
remaining_indices = df.index.difference(st.session_state['selected_indices'])
df_filtered = df.loc[remaining_indices]

if df_filtered.empty:
    st.markdown("<div class='main-content'>All rows have been reviewed!</div>", unsafe_allow_html=True)
elif st.session_state.name != '':
    with st.form("feedback_form", clear_on_submit=True, enter_to_submit=False):
        col1, col2 = st.columns([1, 2])
        selected_row, selected_index = get_random_row(df_filtered)
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
                success_enablers = '\n'.join(success_enablers)
            else:
                success_enablers = "None"
            query = selected_row['Query']
            st.markdown("**Query**:  " + query)
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown("**Success Enablers Returned**:")
            st.write(success_enablers)
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown("**Employer**: " + employer)
            st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
            st.markdown("**AI Summary**: ")
            if isinstance(selected_row['Summary'], str):
                summary = selected_row['Summary']
            else:
                summary = "None"
            st.write(summary)
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
                st.markdown(question_1)
                options = [1, -1, 0]
                labels = ["Yes", "No", "Neutral"]
                relevancy_rating = st.radio(
                "Select your answer:",
                options = options, format_func = format_func,
                key="relevancy_score")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                relevancy_comments= st.text_area("Enter your thoughts here",
                                               key="relevancy_input"
                                              )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                st.markdown(question_2)
                labels = ["No", "Yes", "Neutral"]
                accuracy_rating = st.radio(
                    "Select your answer:",
                    options=options, format_func = format_func,
                    key="accuracy_acore")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                accuracy_comments = st.text_area("Enter your thoughts here", key="accuracy_input",
                                              )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                st.markdown(question_3)
                labels = ["Yes", "No", "Neutral"]
                summary_rating = st.radio(
                    "Select your answer:",
                    options=options, format_func = format_func,
                    key="summary_score")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                summary_comments = st.text_area("Enter your thoughts here", key="summary_input",
                                             )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                st.markdown(question_4)
                labels = ["Yes", "No", "Neutral"]
                journey_rating = st.radio(
                    "Select your answer:",
                    options=options, format_func=format_func,
                    key="journey_score")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                journey_comments = st.text_area("Enter your thoughts here", key="journey_input",
                                                )

                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                current_datetime = datetime.now()
                time = current_datetime.strftime("%Y-%m-%d %H:%M")
                queries = {"Query": query,
                            "Success Enablers": success_enablers,
                            "Employer": employer,
                            "Summary": summary,
                            "Journeys": journeys,}
                user_feedback = {
                                  "Q1 Relevancy Rating": relevancy_rating,
                                  "Q1 Relevancy Comments": relevancy_comments,
                                  "Q2 Accuracy Rating": accuracy_rating,
                                  "Q2 Accuracy Comments": accuracy_comments,
                                  "Q3 Summary Rating": summary_rating,
                                  "Q3 Summary Comments": summary_comments,
                                  "Q4 Journeys Rating": journey_rating,
                                  "Q4 Journeys Comments": journey_comments,
                                  "Name": name,
                                  "Time Submitted": time, }
                submitted = st.form_submit_button("Submit and Give Me Another!", help="Click to submit your feedback",
                                    on_click=update_query_list, args=(queries, ))
                if submitted:
                    st.markdown(f"<div class='main-content'>Thanks! Try Another!</div>", unsafe_allow_html=True)
                    # Add the selected index to the set of reviewed indices
                    st.session_state['selected_indices'].add(st.session_state['selected_row_index'])
                    push_to_bigquery(st.session_state.query_list.pop(), user_feedback)


else:
    st.subheader("Enter Your First and Last Name To Get Started")

    
