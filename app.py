import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import random
from constants import (question_1,
                        question_2,
                        question_3a,
                        question_3b
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


def push_to_bigquery(rows: dict,
                     project_id: str = "healthy-dragon-300820",
                     dataset_id: str = "success_enabler_search_feedback",
                     ):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_credentials"]
    )
    client = bigquery.Client(credentials= credentials, project=project_id)
    table_id: str = "feedback_table_from_streamlit"
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job = client.insert_rows_json(table_ref, rows)




def get_random_row(df: pd.DataFrame) -> pd.Series:
    selected_index = random.choice(df.index)
    selected_row = df.loc[selected_index]

    # Cache the selected row index to ensure it won't be selected again
    cached_indices = st.session_state.get('selected_indices', set())
    cached_indices.add(selected_index)
    st.session_state['selected_indices'] = cached_indices

    return selected_row

def format_func(option):
    return labels[options.index(option)]


st.markdown("<div class='title'>Success Enabler Search & Discovery Feedback Form</div>", unsafe_allow_html=True)

if 'name' not in st.session_state:
    st.session_state.name = ''

st.markdown("<div class='email-input-container'>", unsafe_allow_html=True)
name = st.text_input("Email", key="name", help="Please enter your first and last name",
                      value=st.session_state.name)
st.markdown("</div><div class='spacer'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <p>You will be given a search query followed by the results. Provide a rating and feedback, click 'submit' and you will be given another to rate. When you are finished, click <b>I'm Done!</b> at the bottom of the page.</p>
    """,
    unsafe_allow_html=True
)

df = import_dataframe()

if 'feedback_list' not in st.session_state:
    st.session_state.feedback_list = []

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
        if isinstance(selected_row['Employer'], str):
            employer = selected_row["Employer"]
        else:
            employer = "None"
        st.markdown("**Query**:  " + selected_row['Input'])
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**Success Enablers Returned**:")
        success_enablers_list = str(selected_row['Success Enablers']).split(',')
        success_enablers = [f"{i + 1}. {item}" for i, item in enumerate(success_enablers_list)]
        st.write("\n".join(success_enablers))
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**AI Summary**: ")
        st.write(selected_row["Summary"])
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**Employer**: " + str(selected_row["Employer"]))
        st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
        st.markdown("**Journeys:**")
        if isinstance(selected_row['Journeys'], str):
            journey = selected_row["Journeys"]
            journeys_list = str(journey).split(',')
            journeys = [f"{i + 1}. {item}" for i, item in enumerate(journeys_list)]
            st.write("\n".join(journeys))
        else:
            journeys = "None"
            st.write(journeys)
        with col2:
            with st.form("feedback_form"):
                st.markdown(question_1)
                options = [-1, 0, 1]
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
                accuracy_rating = st.radio(
                    "Select your answer:",
                    options=["Yes", "No", "Neutral"],
                    index=None, key="accuracy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                accuracy_input = st.text_area("Enter your thoughts here", key="accuracy_input",
                                              )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                if isinstance(employer, str):
                    st.markdown(question_3a)
                    summary_rating = st.radio(
                        "Select your answer:",
                        options=["Yes", "No", "Neutral"],
                        index=None, key="summary")
                    st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                    summary_input = st.text_area("Enter your thoughts here", key="summary_input",
                                                 )
                else:
                    st.markdown(question_3b)
                    summary_rating = st.radio(
                        "Select your answer:",
                        options=["Yes", "No", "Neutral"],
                        index=None, key="summary")
                    st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                    summary_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000),
                                                  )
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                user_feedback = [{"Query": selected_row['Input'],
                                 "Success Enablers": selected_row['Success Enablers'],
                                 "Employer": employer,
                                 "Summary": selected_row['Summary'],
                                 "Journeys": journeys,
                                 "Q1 Rating": relevancy_rating,
                                 "Q1 Comments": relevancy_input,
                                 "Q2 Rating": accuracy_rating,
                                 "Q2 Comments": accuracy_input,
                                 "Q3 Rating": summary_rating,
                                 "Q3 Comments": summary_input,
                                  "Name": name}]
                submitted = st.form_submit_button("Submit", help="Click to submit your feedback",
                                                  on_click=push_to_bigquery(user_feedback))
                if submitted:
                    st.markdown(f"<div class='main-content'>Thanks! Try Another</div>", unsafe_allow_html=True)


    
