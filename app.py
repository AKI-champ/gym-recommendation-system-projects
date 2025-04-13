import streamlit as st
import pickle
import requests

# Custom CSS and animations
st.markdown("""
    <style>
        p {
            color: #000;
            font-size: 40px;
            text-align: center;
            font-family: 'Arial', sans-serif;
        }
        .fade-in {
            animation: fadeIn 2s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 15px 32px;
            font-size: 16px;
            margin: 10px 0;
            cursor: pointer;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# 🔎 Get exercise ID (not used in recommend function right now, kept for future use)
def get_exercise_id_from_name(name):
    url = f"https://wger.de/api/v2/exercise/?language=2&limit=500&name={name}"
    try:
        response = requests.get(url)
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["id"]
        else:
            print(f" No ID found for exercise name: {name}")
            return None
    except Exception as e:
        print(f"Error fetching ID for name '{name}': {e}")
        return None

# 🤝 Recommendation logic (SAFE)
def recommend(exercise, gym_list_df, distance):
    matches = gym_list_df[gym_list_df["Title"] == exercise]
    
    if matches.empty:
        st.error(f"Exercise '{exercise}' not found in the dataset.")
        return []

    gym_index = matches.index[0]

    if gym_index >= len(distance):
        st.error("Exercise index is out of bounds for the similarity matrix.")
        return []

    distance_row = distance[gym_index]

    if len(distance_row) != len(gym_list_df):
        st.error("Similarity matrix and dataset size mismatch.")
        return []

    gym_list_sorted = sorted(list(enumerate(distance_row)), key=lambda x: x[1], reverse=True)[1:6]

    recommended = []
    for i in gym_list_sorted:
        title = gym_list_df.iloc[i[0]]["Title"]
        recommended.append(title)
    return recommended

# 📦 Load data
try:
    with open("gym.pkl", "rb") as f:
        gym_list_df = pickle.load(f)

    with open("similarity.pkl", "rb") as f1:
        similarity = pickle.load(f1)
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

# 🧾 List of gym titles
gym_list = gym_list_df["Title"]

# 🚀 Streamlit App UI
st.title("Workout Recommendation System")

option = st.selectbox("Choose an exercise", gym_list)

if st.button("Recommend"):
    recommended_gyms = recommend(option, gym_list_df, similarity)
    if recommended_gyms:
        st.write("Recommended Exercises:")
        for exercise in recommended_gyms:
            st.markdown(f'<p class="fade-in">{exercise}</p>', unsafe_allow_html=True)
