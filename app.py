import streamlit as st
import pandas as pd
import random
from streamlit_star_rating import st_star_rating

@st.cache_data()
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



st.title("Success Enabler Search & Discovery Feedback Form")

email = st.text_input("Email")

st.write("You will be given a search query followed by the results. "
             "Provide a rating (10 being best) and feedback, click 'submit' and you will "
             "be given a another to rate. When you are finished, simply exit this page.")

df = import_dataframe()

# Exclude already selected rows
if 'selected_indices' in st.session_state:
    remaining_indices = df.index.difference(st.session_state['selected_indices'])
    df = df.loc[remaining_indices]

if df.empty:
    st.write("All rows have been reviewed!")
else:
    with st.form("feedback_form"):
        selected_row = get_random_row(df)
        st.markdown("**Query**:")
        st.write(selected_row["Input"])
        st.markdown("**Success Enablers Returned**:")
        st.write(selected_row["Success Enablers"])
        st.markdown("**AI Summary**: ")
        st.write(selected_row["Summary"])
        employer = selected_row["Employer"]
        st.markdown("**Employer**: ")
        st.write(selected_row["Employer"])
        st.markdown("**Journeys**")
        st.write(selected_row["Journeys"])
        st.markdown("1. **Relevancy**: Are the Success Enablers relevant to the query? ")
        relevancy_rating = st_star_rating("Relevancy Rating", maxValue=10, defaultValue=5, key="relevancy")
        relevancy_input = st.text_input("Enter your thoughts here", key=random.randint(0, 100000))
        st.markdown("2. **Accuracy**: Are there missing Success Enablers (even if you "
                    "are not sure we offer them)?")
        accuracy_rating = st_star_rating("Accuracy Rating", maxValue=10, defaultValue=5, key="accuracy")
        accuracy_input = st.text_input("Enter your thoughts here", key=random.randint(0, 100000))
        if isinstance(employer, str):
            st.markdown("**Employer**: If the summary mentions resources, does it make clear what the user should do?")
            summary_rating = st_star_rating("Summary Rating", maxValue=10, defaultValue=5, key="employer_summary")
            summary_input = st.text_input("Enter your thoughts here", key=random.randint(0, 100000))
        else:
            st.markdown("**Summary**: Does the summary answer the query in a useful way and fulfill the user's intent?")
            summary_rating = st.text_input("Enter your thoughts here", key=random.randint(0, 100000))
            summary_input = st.text_input("Enter your thoughts here", key=random.randint(0, 100000))
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write(f"Form submitted from {email}")


    
