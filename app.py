import streamlit as st
import psycopg2
import pandas as pd

# --- Configuration ---
PAGE_TITLE = "PostgreSQL Query Viewer"
PAGE_ICON = ":chart_with_upwards_trend:"  # You can use an emoji

# --- Initialize ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- Styling ---
# Custom CSS for a white background and dark text
streamlit_style = """
    <style>
        :root {
            --primary-color: #101828;  /* White background */
            --text-color: #101828;      /* Dark text */
            --accent-color: #6366f1;    /* Vibrant purple */
            --gray-color: #d1d5db;
            --dark-gray-color: #4b5563;
            --button-hover-color: #7e80f2;
        }

        body {
            background-color: var(--primary-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: var(--primary-color);
        }

        h1 {
            color: var(--accent-color);
            font-weight: 700;
            margin-bottom: 1.5rem;
        }
        h2{
           color: var(--text-color);
           font-size: 1.85rem;
           font-weight: 600;
           margin-bottom: 1rem;
        }

        .stTextInput > label {
            color: var(--gray-color);
        }

        .stNumberInput > label {
            color: var(--gray-color);
        }

        .stButton>button {
            background-color: var(--accent-color);
            color: #000000; /* Changed the color of the text to black */
            font-weight: 500;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.2);
        }

        .stButton>button:hover {
            background-color: var(--button-hover-color);
            color: white;
        }
        .stButton>button:active{
             box-shadow: 0 0.05rem 0.1rem rgba(0, 0, 0, 0.2);
             transform: translateY(1px);
        }

        .stTextInput>div>div>input {
            background-color: #ffffff;
            border: 0.0625rem solid var(--gray-color);
            color: var(--text-color);
            border-radius: 0.375rem;
            padding: 0.75rem;
            transition: border-color 0.2s ease;
        }

        .stTextInput>div>div>input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 0.125rem rgba(99, 102, 241, 0.25);
            outline: none;
        }
        .stNumberInput>div>div>input {
            background-color: #ffffff;
            border: 0.0625rem solid var(--gray-color);
            color: var(--text-color);
            border-radius: 0.375rem;
            padding: 0.75rem;
            transition: border-color 0.2s ease;
        }

        .stNumberInput>div>div>input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 0.125rem rgba(99, 102, 241, 0.25);
            outline: none;
        }

        .dataframe {
            background-color: #ffffff;
            border: 0.0625rem solid var(--gray-color);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-top: 1rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.2);
        }
        .dataframe thead th {
            background-color: #efefef;
            color: var(--text-color);
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
            border-bottom: 0.0625rem solid var(--gray-color);
        }
        .dataframe tbody td{
           padding: 0.75rem;
           border-bottom: 0.0625rem solid var(--gray-color);
        }

        .dataframe tbody tr:last-child td {
            border-bottom: none;
        }

        .st-expander {
            background-color: #ffffff;
            border-radius: 0.5rem;
            border: 0.0625rem solid var(--gray-color);
            margin-bottom: 1rem;
        }

        .st-expander-header {
            color: var(--text-color);
            font-weight: 600;
            padding: 0.75rem 1rem;
        }

        .st-expander-content {
            padding: 0 1rem 1rem 1rem;
            color: var(--gray-color);
        }
        .css-16idsb6 h2{
            color: var(--accent-color);
            font-size: 1.5rem;
            font-weight: 600;
        }

    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
"""
st.markdown(streamlit_style, unsafe_allow_html=True)


# --- Database Connection ---
@st.cache_resource
def get_connection(host, port, dbname, user, password):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None


# --- Main App ---
def main():
    st.title("PostgreSQL Query Viewer")

    # Database connection details
    with st.expander("Database Connection Details"):
        db_host = st.text_input("Host", value="localhost")
        db_port = st.text_input("Port", value="5432")
        db_name = st.text_input("Database Name")
        db_user = st.text_input("User")
        db_password = st.text_input("Password", type="password")

    # Query and show results
    st.subheader("Flight Delay Analysis")
    query = st.text_input(
        "Enter your SQL query:",
        """SELECT carrier_name, COUNT(*) AS total_delays
    FROM Flights
    WHERE arr_del15 = TRUE
    GROUP BY carrier_name
    ORDER BY total_delays DESC;""",
    )
    if st.button("Run Query"):
        conn = get_connection(db_host, db_port, db_name, db_user, db_password)
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                if cursor.description:
                    colnames = [description[0] for description in cursor.description]
                    st.write("Query Results:")
                    df = pd.DataFrame(results, columns=colnames)
                    st.dataframe(df)
                else:
                    st.write("Query executed successfully, but no data was returned.")
            except Exception as e:
                st.error(f"Error executing query: {e}")
                conn.rollback()
            finally:
                if cursor:
                    cursor.close()
                conn.close()


if __name__ == "__main__":
    main()
