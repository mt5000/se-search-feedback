import streamlit as st
import pandas as pd
from google.cloud import bigquery
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


def push_to_bigquery(df, user_email: str,
                     project_id: str = "healthy-dragon-300820",
                     dataset_id: str = "success_enabler_search_feedback",
                     ):
    client = bigquery.Client(project=project_id)
    table_id: str = f"feedback_{user_email}"
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    # Configure the job
    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    job_config.source_format = bigquery.SourceFormat.CSV
    csv_data = df.to_csv(index=False)

    job = client.load_table_from_file(
        csv_data,
        table_ref,
        job_config=job_config
    )
    job.result()




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
        employer = selected_row["Employer"]
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
        journey = selected_row["Journeys"]
        if isinstance(journey, str):
            journeys_list = str(journey).split(',')
            journeys = [f"{i + 1}. {item}" for i, item in enumerate(journeys_list)]
            st.write("\n".join(journeys))
        else:
            st.write('None')
        with col2:
            with st.form("feedback_form"):
                st.markdown(question_1)
                relevancy_rating = st.radio(
                "Select your answer:",
                options = ["Yes", "No", "Neutral"],
                index = None, key="relevancy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                relevancy_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                st.markdown(question_2)
                accuracy_rating = st.radio(
                    "Select your answer:",
                    options=["Yes", "No", "Neutral"],
                    index=None, key="accuracy")
                st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                accuracy_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                if isinstance(employer, str):
                    st.markdown(question_3a)
                    summary_rating = st.radio(
                        "Select your answer:",
                        options=["Yes", "No", "Neutral"],
                        index=None, key="summary")
                    st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                    summary_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                else:
                    st.markdown(question_3b)
                    summary_rating = st.radio(
                        "Select your answer:",
                        options=["Yes", "No", "Neutral"],
                        index=None, key="summary")
                    st.markdown("<div class='thoughts-input'></div>", unsafe_allow_html=True)
                    summary_input = st.text_area("Enter your thoughts here", key=random.randint(0, 100000))
                st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

                user_feedback = {"Query": selected_row['Input'],
                                 "Success Enablers": selected_row['Success Enablers'],
                                 "Employer": employer,
                                 "Summary": selected_row['Summary'],
                                 "Journeys": selected_row['Journeys'],
                                 "Q1 Rating": relevancy_rating,
                                 "Q1 Comments": relevancy_input,
                                 "Q2 Rating": accuracy_rating,
                                 "Q2 Comments": accuracy_input,
                                 "Q3 Rating": summary_rating,}

                submitted = st.form_submit_button("Submit", help="Click to submit your feedback", on_click=None)
                if submitted:
                    st.session_state.feedback_list.append(user_feedback)
                    st.markdown(f"<div class='main-content'>Form submitted</div>", unsafe_allow_html=True)

        finished = st.button("I'm Done!")
        if finished:
            final_feedback = pd.DataFrame(st.session_state.feedback_list)
            push_to_bigquery(final_feedback, email)



    
