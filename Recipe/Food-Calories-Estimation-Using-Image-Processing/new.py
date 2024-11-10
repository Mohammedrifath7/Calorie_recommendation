import streamlit as st
import requests
from groq import Groq

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
HF_HEADERS = {"Authorization": "Bearer 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"}

# Groq API setup
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Helper functions
def get_image_caption(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(HF_API_URL, headers=HF_HEADERS, data=data)
    if response.status_code != 200:
        st.error(f"Error fetching image caption: {response.text}")
        return None
    response_data = response.json()
    return response_data[0]['generated_text'] if response_data else None

def get_calorie_details(caption):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Analyze the calories and nutritional content of the dish described as '{caption}' and provide details."
                "A 5 line description of the dish,like what and all presented in the dish"
                "Give like points only about the calories and nutrictional function present dont give description,just give points"
                "Give totally only 10 lines"
            }],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error fetching calorie details: {e}")
        return None

def recommend_vegetarian_dish(caption):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Recommend a vegetarian dish with similar calorie content as the non-vegetarian dish described as '{caption}'."
                "Definitely recommend a good vegeteraian dish,which is healthy and tasty"
                "Recommend Dish and below that you can provide the description of the dish about calories and nutrictional function present in the dish,But initally display the dish name"
                "give like points like colons for calories and nutrictional function present in the dish"
                """
                May be for example:
                * Calories: approximately 400-500 per serving
                * Protein: 35-40g (from chicken and rice)
                * Fat: 10-12g (from chicken and rice)
                * Carbohydrates: 60-65g (from rice and vegetables)
                * Fiber: 5-6g (from rice, vegetables, and chicken skin)
                * Sodium: 400-500mg (from chicken and vegetables)
                * Sugar: 5-6g (naturally occurring from vegetables and rice)
                * Cholesterol: 60-70mg (from chicken)
                """
                "Like the above give for the Vegetarian dish,of your recommendation"
                "Just recommend the dish based on the calories and nutrictional function present dont give description,just give points"
                "Give totally only 10 lines"
            }],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error fetching vegetarian dish recommendation: {e}")
        return None

def get_recipe_details():
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": "Provide the detailed recipe, ingredients, and cooking instructions for the recommended vegetarian dish."
            }],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error fetching recipe details: {e}")
        return None

def parse_nutritional_points(text):
    lines = text.split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

# Custom CSS for styling
st.markdown("""
    <style>
    .highlight {
        font-size: 1.2em;
        font-weight: bold;
        color: #FF6347;
        transition: color 0.3s ease;
    }
    .highlight:hover {
        color: #FF4500;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stExpander {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .stExpander:hover {
        background-color: #f1f1f1;
    }
    .box {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        transition: background-color 0.3s ease;
    }
    .box:hover {
        background-color: #f1f1f1;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.title("AI-based Recipe Recommender")
st.header("Upload an Image of a Non-Vegetarian Dish")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with open("temp_image.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Generate the image caption
    st.write("Generating a description for the dish...")
    caption = get_image_caption("temp_image.jpg")
    
    if caption:
        st.write(f"**Image Caption:** {caption}")
        
        # Layout with two columns for calorie chart and recommendation button
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Calorie Chart")
            with st.container():
                if st.button("Show Calorie Details"):
                    calorie_details = get_calorie_details(caption)
                    if calorie_details:
                        description, nutritional_points = calorie_details.split('\n\n', 1)
                        st.text(description)
                        nutritional_data = parse_nutritional_points(nutritional_points)
                        st.table(nutritional_data)
                    else:
                        st.warning("Could not fetch calorie details. Please try again.")

        with col2:
            st.subheader("Vegetarian Food Recommendation")
            with st.container():
                if st.button("Get Vegetarian Dish"):
                    veg_recommendation = recommend_vegetarian_dish(caption)
                    if veg_recommendation:
                        # Highlight the dish name
                        dish_name = veg_recommendation.split('\n')[0]
                        st.markdown(f"<div class='highlight'>{dish_name}</div>", unsafe_allow_html=True)
                        nutritional_points = '\n'.join(veg_recommendation.split('\n')[1:])
                        nutritional_data = parse_nutritional_points(nutritional_points)
                        st.table(nutritional_data)
                        st.session_state['show_recipe'] = True  # Set to show recipe details

        # Display recipe if vegetarian recommendation button was clicked
        if 'show_recipe' in st.session_state and st.session_state['show_recipe']:
            with st.expander("Recipe and Instructions"):
                recipe_details = get_recipe_details()
                if recipe_details:
                    st.write(recipe_details)
                else:
                    st.warning("Could not fetch recipe details. Please try again.")
    else:
        st.error("Failed to generate image caption. Please try again.")