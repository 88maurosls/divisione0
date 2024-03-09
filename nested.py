import streamlit as st

st.write("# This works:")

if "button1" not in st.session_state:
    st.session_state["button1"] = False

if "button2" not in st.session_state:
    st.session_state["button2"] = False


if st.button("Button1"):
    st.session_state["button1"] = not st.session_state["button1"]

if st.session_state["button1"]:
    if st.button("Button2"):
        st.session_state["button2"] = not st.session_state["button2"]
        st.write("**Button3!!!**")