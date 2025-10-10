import streamlit as st
import mysql.connector
import os
from PIL import Image
import io

st.set_page_config(
    page_title="LLKK - Lab Legend Kingdom Kvalis",
    layout="wide",  
    initial_sidebar_state="auto"
)

# Optimized CSS - Remove heavy animations
st.markdown("""
<style>
    .avatar-card {
        position: relative;
        border: 2px solid transparent;
        border-radius: 10px;
        padding: 8px;
        height: 180px; /* Reduced height */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        cursor: pointer;
        margin-bottom: 5px;
        background: white;
    }

    .avatar-card:hover {
        border-color: #6c757d;
        background-color: #f8f9fa; 
    }

    .avatar-card.selected {
        border-color: #28a745;
        background-color: #e8f5e9;
        box-shadow: 0 2px 6px rgba(40,167,69,0.2);
    }

    .avatar-card.selected::after {
        content: "✔";
        position: absolute;
        top: 5px;
        right: 5px;
        background-color: #28a745;
        color: white;
        font-size: 12px;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .avatar-image {
        width: 100%;
        height: 120px; /* Reduced height */
        object-fit: contain;
        margin-bottom: 4px;
    }

    .avatar-name {
        text-align: center;
        font-weight: 600;
        font-size: 12px; /* Smaller font */
        margin-top: 5px;
    }
    
    .avatar-card.taken {
        opacity: 0.5;
        cursor: not-allowed;
    }
  
    .avatar-card.taken::after {
        content: "Taken";
        position: absolute;
        top: 5px;
        right: 5px;
        background-color: #c62828;
        color: white;
        font-size: 10px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 10px;
    }
    
    .admin-note {
        padding: 8px;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin: 8px 0;
        font-size: 14px;
    }
</style>  
""", unsafe_allow_html=True)

def get_connection():
    """Optimized database connection with error handling"""
    try:
        return mysql.connector.connect(
            host="145.223.18.115",
            port=3306,
            user="admin",
            password="@Cittamall13",         
            database="gamifiedqc",
            connect_timeout=10
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def check_username_exists(username):
    """Check if username already exists"""
    if not username or len(username.strip()) == 0:
        return False
    
    conn = get_connection()
    if not conn:
        return True  # Assume exists to prevent creation if DB fails
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT username FROM labs_users WHERE username = %s", (username.strip(),))
        result = cur.fetchone() is not None
        return result
    except Exception as e:
        st.error(f"Error checking username: {e}")
        return True
    finally:
        if conn:
            conn.close()

def get_used_avatars():
    """Get list of used avatars"""
    conn = get_connection()
    if not conn:
        return set()
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT avatar FROM labs_users WHERE avatar IS NOT NULL")
        used = [row[0] for row in cur.fetchall()]
        return set(used)
    except Exception as e:
        st.error(f"Error loading avatars: {e}")
        return set()
    finally:
        if conn:
            conn.close()

def optimize_image(image_path, max_size=(150, 150)):
    """Optimize image size and format to reduce memory usage"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize image
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes with optimization
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=70, optimize=True)
            img_bytes.seek(0)
            
            return img_bytes
    except Exception as e:
        st.error(f"Error optimizing image {image_path}: {e}")
        return None

def display_avatar_card(name, path, is_used, is_selected):
    """Display a single avatar card with optimized image"""
    if not os.path.exists(path):
        st.error(f"Image not found: {path}")
        return
    
    # Optimize image
    img_bytes = optimize_image(path)
    if not img_bytes:
        return
    
    selected_class = "selected" if is_selected else ""
    taken_class = "taken" if is_used else ""
    
    st.markdown(
        f"""
        <div class="avatar-card {taken_class} {selected_class}">
            <img src="data:image/jpeg;base64,{base64.b64encode(img_bytes.getvalue()).decode()}" class="avatar-image"/>
            <div class="avatar-name">{name}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main application
st.title("📝 Create a New Account")

# Input fields
new_username = st.text_input("Username")
new_password = st.text_input("Password", type="password")
new_role = st.selectbox("Role", ["lab", "admin"])

if new_role == "admin":
    st.markdown("""
    <div class="admin-note">
        <strong>ℹ️ Admin Note:</strong> As an admin, you don't need to select an avatar.
    </div>
    """, unsafe_allow_html=True)

# Avatar definitions
avatars = {
    "Zareth": "avatars/zareth.png",
    "Dreadon": "avatars/Dreadon.png",
    "Selindra": "avatars/Selindra.png",
    "Raviel": "avatars/Raviel.png",
    "Takeshi": "avatars/Takeshi.png",
    "Synkro": "avatars/Synkro.png",
    "Zyphira": "avatars/Zyphira.png",
    "Umbra": "avatars/Umbra.png",
    "Kaira": "avatars/Kaira.png",
    "Ignar": "avatars/Ignar.png",
    "Ryden": "avatars/Ryden.png",
    "Nyra": "avatars/Nyra.png",
    "Kaen": "avatars/Kaen.png",
    "Raika": "avatars/Raika.png",
    "Dain": "avatars/Dain.png",
    "Veyra": "avatars/Veyra.png",
    "Reiko": "avatars/Reiko.png",
    "Kane & Lyra": "avatars/kanenlyra.png",
    "Mimi": "avatars/Mimi.png",
    "Rowan": "avatars/Rowan.png",
    "Taro": "avatars/Taro.png",
    "Eldric": "avatars/Eldric.png",
    "Noel": "avatars/Noel.png",
    "Elias": "avatars/Elias.png",
    "Finn": "avatars/Finn.png",
}

# Session state for selected avatar
if "selected_avatar" not in st.session_state:
    st.session_state.selected_avatar = None

# Display avatars only for lab role
if new_role == "lab":
    st.markdown("🎭 **Choose Your Avatar**")
    
    # Load used avatars
    used_avatars = get_used_avatars()
    
    # Display in columns with lazy loading
    cols = st.columns(4)
    
    for i, (name, path) in enumerate(avatars.items()):
        with cols[i % 4]:
            is_used = name in used_avatars
            is_selected = st.session_state.selected_avatar == name
            
            # Display optimized avatar card
            display_avatar_card(name, path, is_used, is_selected)
            
            # Selection button
            if st.button(f"Select {name}", key=f"btn-{i}", use_container_width=True, disabled=is_used):
                st.session_state.selected_avatar = name
                st.rerun()

# Create account button
if st.button("Create Account"):
    if not new_username or not new_password:
        st.warning("⚠️ Please fill all fields.")
    elif check_username_exists(new_username):
        st.error("❌ Username already exists! Please choose a different username.")
    elif new_role == "lab" and not st.session_state.selected_avatar:
        st.warning("⚠️ Please choose an avatar before creating your account.")
    else:
        try:
            conn = get_connection()
            if not conn:
                st.error("❌ Cannot connect to database. Please try again.")
                st.stop()
                
            cur = conn.cursor()
            avatar_value = None if new_role == "admin" else st.session_state.selected_avatar
            
            cur.execute(
                "INSERT INTO labs_users (username, password, role, avatar) VALUES (%s, %s, %s, %s)",
                (new_username, new_password, new_role, avatar_value),
            )
            conn.commit()
            st.success("✅🎉 Account Created Successfully! Go back to Login.")
            st.session_state.selected_avatar = None
            
        except mysql.connector.Error as err:
            st.error(f"❌ Database error: {err}")
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()