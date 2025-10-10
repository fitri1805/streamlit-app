import streamlit as st
import mysql.connector
import os
import base64

st.set_page_config(
    page_title="LLKK - Lab Legend Kingdom Kvalis",
    layout="wide",  
    initial_sidebar_state="auto"
)

st.markdown("""
<style>
    .avatar-card {
        position: relative;
        border: 2px solid transparent;
        border-radius: 10px;
        padding: 10px;
        transition: all 0.3s ease;
        height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        cursor: pointer;
        margin-bottom: 5px; /* Fixed margin to prevent movement */
    }

    .avatar-card:hover {
        border-color: #6c757d;
        background-color: grey; 
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .avatar-card.selected {
        border-color: #28a745;
        background-color: #e8f5e9; 
        box-shadow: 0 4px 12px rgba(40,167,69,0.3);
        color: black; 
    }

    .avatar-card.selected::after {
        content: "✔";
        position: absolute;
        top: 8px;
        right: 8px;
        background-color: #28a745;
        color: white;
        font-size: 14px;
        font-weight: bold;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }

    .avatar-image {
        width: 100%;
        height: 200px;
        object-fit: contain;
        margin-bottom: 4px;
        flex-shrink: 0;
    }

    .avatar-name {
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        margin-top: 10px;
    }
    
    .avatar-card.taken {
        opacity: 0.6;
        cursor: not-allowed;
        position: relative;
    }
  
    .avatar-card.taken::after {
        content: "Taken";
        position: absolute;
        top: 8px;
        right: 8px;
        background-color: #c62828;
        color: white;
        font-size: 11px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
   
    .hidden-btn {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .admin-note {
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
    }
    
</style>  
""", unsafe_allow_html=True)

def get_connection():
    return mysql.connector.connect(
        host="145.223.18.115",
        port=3306,
        user="admin",
        password="@Cittamall13",         
        database="gamifiedqc" 
    )

st.title("📝 Create a New Account")

new_username = st.text_input("Username")
new_password = st.text_input("Password", type="password")
new_role = st.selectbox("Role", ["lab", "admin"])

if new_role == "admin":
    st.markdown("""
    <div class="admin-note">
        <strong>ℹ️ Admin Note:</strong> As an admin, you don't need to select an avatar.
    </div>
    """, unsafe_allow_html=True)

avatars = {
    "Zareth":"avatars/zareth.png",
    "Dreadon":"avatars/Dreadon.png",
    "Selindra":"avatars/Selindra.png",
    "Raviel":"avatars/Raviel.png",
    "Takeshi":"avatars/Takeshi.png",
    "Synkro":"avatars/Synkro.png",
    "Zyphira":"avatars/Zyphira.png",
    "Umbra":"avatars/Umbra.png",
    "Kaira":"avatars/Kaira.png",
    "Ignar":"avatars/Ignar.png",
    "Ryden":"avatars/Ryden.png",
    "Nyra":"avatars/Nyra.png",
    "Kaen":"avatars/Kaen.png",
    "Raika":"avatars/Raika.png",
    "Dain":"avatars/Dain.png",
    "Veyra":"avatars/Veyra.png",
    "Reiko":"avatars/Reiko.png",
    "Kane & Lyra":"avatars/kanenlyra.png",
    "Mimi":"avatars/Mimi.png",
    "Rowan":"avatars/Rowan.png",
    "Taro":"avatars/Taro.png",
    "Eldric":"avatars/Eldric.png",
    "Noel":"avatars/Noel.png",
    "Elias":"avatars/Elias.png",
    "Finn":"avatars/Finn.png",
}

if new_role == "lab":
    st.markdown("🎭 **Choose Your Avatar**")

# session state
if "selected_avatar" not in st.session_state:
    st.session_state.selected_avatar = None


def check_username_exists(username):
    """Check if username already exists in database"""
    if not username or len(username.strip()) == 0:
        return False
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM labs_users WHERE username = %s", (username.strip(),))
    result = cur.fetchone() is not None
    cur.close()
    conn.close()
    return result

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_used_avatars():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT avatar FROM labs_users")
    used = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return set(used)

if new_role == "lab":
    used_avatars = get_used_avatars()
    cols = st.columns(4)

    for i, (name, path) in enumerate(avatars.items()):
        with cols[i % 4]:
            if os.path.exists(path):
                img_base64 = img_to_base64(path)
                
                is_used = name in used_avatars
                selected_class = "selected" if st.session_state.selected_avatar == name else ""

                st.markdown(
                    f"""
                    <div class="avatar-card {'taken' if is_used else ''} {selected_class}">
                        <img src="data:image/png;base64,{img_base64}" class="avatar-image"/>
                        <div class="avatar-name">{name}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"Select {name}", key=f"btn-{i}", use_container_width=True, disabled=is_used):
                    st.session_state.selected_avatar = name
                    st.rerun()  

                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

if st.button("Create Account"):
    if new_username and check_username_exists(new_username):
        st.error("❌ Username already exists! Please choose a different username.")
    elif new_role == "lab" and not st.session_state.selected_avatar:
        st.warning("⚠️ Please choose an avatar before creating your account.")
    elif not new_username or not new_password:
        st.warning("⚠️ Please fill all fields.")
    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            if new_role == "admin":
                avatar_value = None 
            else:
                avatar_value = st.session_state.selected_avatar
            cur.execute(
                "INSERT INTO labs_users (username, password, role, avatar) VALUES (%s, %s, %s, %s)",
                (new_username, new_password, new_role, avatar_value),
            )
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅🎉 Account Created Successfully! Go back to Login.")
            st.session_state.selected_avatar = None
        except mysql.connector.Error as err:
            st.error(f"❌ Database error: {err}")

st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stDataFrame {
            font-size: 12px;
        }
        .stButton > button {
            width: 100%;
            margin: 5px 0;
        }
        .stSelectbox, .stTextInput {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)