import streamlit as st
import mysql.connector
import os
import base64

# --- CSS ---
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

    /* Tick badge */
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

    /* Badge merah untuk 'Taken' */
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
    
    /* Hidden button styling */
    .hidden-btn {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    
</style>
""", unsafe_allow_html=True)

def get_connection():
    return mysql.connector.connect(
        host="137.59.109.94",
        port=3306,
        user="alfadiagno22_gamifiedqc",
        password="Cittamall13_",         
        database="alfadiagno22_gamifiedqc"
    )

st.title("📝 Create a New Account")

new_username = st.text_input("Username")
new_password = st.text_input("Password", type="password")
new_role = st.selectbox("Role", ["lab", "admin"])

# --- Avatars ---
avatars = {
    "Zareth":"avatars/zareth.png",
    "Dreadon":"avatars/Dreadon.png",
    "Selindra":"avatars/Selindra.png",
    "Raviel":"avatars/Raviel.png",
    "Takeshi":"avatars/Takeshi.png",
    "Synkro":"avatars/Synkro.png",
    "Zyphira":"avatars/Zyphira.png",
    "Umbra":"avatars/Umbra.png",
}

st.markdown("🎭 **Choose Your Avatar**")

# session state
if "selected_avatar" not in st.session_state:
    st.session_state.selected_avatar = None


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
    
# --- Fetch used avatars from DB ---
def get_used_avatars():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT avatar FROM labs_users")
    used = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return set(used)

used_avatars = get_used_avatars()

cols = st.columns(4)

for i, (name, path) in enumerate(avatars.items()):
    with cols[i % 4]:
        if os.path.exists(path):
            img_base64 = img_to_base64(path)
            
            is_used = name in used_avatars
            selected_class = "selected" if st.session_state.selected_avatar == name else ""

            ############
            is_used = name in used_avatars  
            onclick_attr = f"onclick=\"selectAvatar('{name}', 'card-{i}', 'btn-{i}')\"" if not is_used else ""
            card_class = f"avatar-card {'taken' if is_used else ''} {selected_class}"

           # Display card
            st.markdown(
                f"""
                <div class="{card_class}">
                    <img src="data:image/png;base64,{img_base64}" class="avatar-image"/>
                    <div class="avatar-name">{name}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Add a fixed spacer so button aligns
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

            # Button for available avatars
            if st.button("select", key=f"btn-{i}", help=name, use_container_width=True, disabled=is_used):
                st.session_state.selected_avatar = name

# --- JS for instant visual highlight + trigger hidden button ---
st.markdown("""
<script>
function selectAvatar(name, cardId) {
    // Remove 'selected' from all cards
    document.querySelectorAll('.avatar-card').forEach(el => el.classList.remove('selected'));
    // Add 'selected' to clicked card
    document.getElementById(cardId).classList.add('selected');
    // Click hidden Streamlit button to update session_state
    const hiddenBtn = window.parent.document.querySelector(`button[title="${name}"]`);
    if (hiddenBtn) hiddenBtn.click();
}
</script>
""", unsafe_allow_html=True)

# --- Account Creation ---
if st.button("Create Account"):
    if not st.session_state.selected_avatar:
        st.warning("⚠️ Please choose an avatar before creating your account.")
    elif not new_username or not new_password:
        st.warning("⚠️ Please fill all fields.")
    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO labs_users (username, password, role, avatar) VALUES (%s, %s, %s, %s)",
                (new_username, new_password, new_role, st.session_state.selected_avatar),
            )
            conn.commit()
            cur.close()
            conn.close()
            st.success("✅ Account created! Go back to Login.")
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