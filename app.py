import streamlit as st
import json
import hashlib
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
UPLOAD_DIR = Path("uploads")
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
STUDENTS_FILE = DATA_DIR / "students.json"
COURSES_FILE = DATA_DIR / "courses.json"

DEFAULT_STUDENTS = [{"id":"S001","name":"Demo Student","email":"student@example.com","username":"student","password":"student123","active":True}]
DEFAULT_COURSES = [{"id":"C001","title":"Introduction to Web Development","description":"A simple demo course.","videos":[{"title":"Welcome","type":"url","url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}]}]

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_json(path, default):
    if not path.exists(): save_json(path, default)
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return default

def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()
def verify_password(password, stored): return password == stored or hash_password(password) == stored

def embed_url(url):
    if "youtube.com/watch?v=" in url: return "https://www.youtube.com/embed/" + url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return "https://www.youtube.com/embed/" + url.split("youtu.be/")[1].split("?")[0]
    if "vimeo.com/" in url:
        vid=url.rstrip("/").split("/")[-1]
        if vid.isdigit(): return f"https://player.vimeo.com/video/{vid}"
    return None

def logout():
    st.session_state.role=None; st.session_state.user=None; st.rerun()

def login_page():
    st.title("🎓 LMS Demo")
    st.caption("Simple Learning Management System built with Streamlit")
    tab_student, tab_admin = st.tabs(["Student Login", "Admin Login"])
    with tab_student:
        with st.form("student_login"):
            username=st.text_input("Username"); password=st.text_input("Password",type="password"); submit=st.form_submit_button("Login")
        if submit:
            students=load_json(STUDENTS_FILE,DEFAULT_STUDENTS)
            user=next((s for s in students if s["username"]==username and verify_password(password,s["password"]) and s.get("active",True)),None)
            if user: st.session_state.role="student"; st.session_state.user=user; st.rerun()
            st.error("Invalid student username or password.")
    with tab_admin:
        with st.form("admin_login"):
            username=st.text_input("Admin username"); password=st.text_input("Admin password",type="password"); submit=st.form_submit_button("Admin Login")
        if submit:
            au=st.secrets.get("ADMIN_USERNAME","admin"); ap=st.secrets.get("ADMIN_PASSWORD","admin123")
            if username==au and password==ap: st.session_state.role="admin"; st.session_state.user={"username":username,"name":"Administrator"}; st.rerun()
            st.error("Invalid admin credentials.")

def admin_dashboard():
    st.sidebar.title("Admin Panel")
    page=st.sidebar.radio("Menu",["Dashboard","Students","Courses","Add Video"])
    if st.sidebar.button("Logout"): logout()
    students=load_json(STUDENTS_FILE,DEFAULT_STUDENTS); courses=load_json(COURSES_FILE,DEFAULT_COURSES)
    if page=="Dashboard":
        st.title("📊 Admin Dashboard"); a,b,c=st.columns(3); a.metric("Students",len(students)); b.metric("Courses",len(courses)); c.metric("Videos",sum(len(x.get("videos",[])) for x in courses))
    elif page=="Students":
        st.title("👨‍🎓 Student Management")
        with st.form("add_student"):
            name=st.text_input("Student name"); email=st.text_input("Email"); username=st.text_input("Username"); password=st.text_input("Password",type="password"); add=st.form_submit_button("Add Student")
        if add:
            if not all([name,email,username,password]): st.error("Fill all fields.")
            elif any(s["username"]==username for s in students): st.error("Username already exists.")
            else:
                students.append({"id":f"S{len(students)+1:03d}","name":name,"email":email,"username":username,"password":hash_password(password),"active":True}); save_json(STUDENTS_FILE,students); st.success("Student added successfully.")
        st.dataframe([{"ID":s["id"],"Name":s["name"],"Email":s["email"],"Username":s["username"],"Active":s.get("active",True)} for s in students],use_container_width=True)
    elif page=="Courses":
        st.title("📚 Course Management")
        with st.form("add_course"):
            title=st.text_input("Course title"); description=st.text_area("Description"); add=st.form_submit_button("Create Course")
        if add:
            if not title: st.error("Course title is required.")
            else: courses.append({"id":f"C{len(courses)+1:03d}","title":title,"description":description,"videos":[]}); save_json(COURSES_FILE,courses); st.success("Course created.")
        for course in courses:
            with st.expander(course["title"]):
                st.write(course.get("description",""))
                for v in course.get("videos",[]): st.write(f"• {v['title']} ({v['type']})")
    else:
        st.title("🎥 Add Video")
        if not courses: st.warning("Create a course first."); return
        selected=st.selectbox("Course",[c["title"] for c in courses]); title=st.text_input("Video title"); mode=st.radio("Video source",["YouTube / Vimeo URL","Upload video file"])
        if mode=="YouTube / Vimeo URL":
            url=st.text_input("Paste YouTube or Vimeo URL")
            if st.button("Add URL Video"):
                if not title or not url: st.error("Enter title and URL.")
                else:
                    course=next(c for c in courses if c["title"]==selected); course["videos"].append({"title":title,"type":"url","url":url}); save_json(COURSES_FILE,courses); st.success("Video URL added.")
        else:
            uploaded=st.file_uploader("Upload MP4/WebM/MOV",type=["mp4","webm","mov"])
            if st.button("Upload Video") and uploaded:
                target=UPLOAD_DIR/f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{Path(uploaded.name).name}"; target.write_bytes(uploaded.getbuffer()); course=next(c for c in courses if c["title"]==selected); course["videos"].append({"title":title or uploaded.name,"type":"file","path":str(target)}); save_json(COURSES_FILE,courses); st.success("Video uploaded and added.")

def student_dashboard():
    if st.sidebar.button("Logout"): logout()
    courses=load_json(COURSES_FILE,DEFAULT_COURSES); st.title(f"🎓 Welcome, {st.session_state.user.get('name','Student')}")
    for course in courses:
        with st.expander(f"📘 {course['title']}"):
            st.write(course.get("description",""))
            for video in course.get("videos",[]):
                st.markdown(f"### {video['title']}")
                if video["type"]=="url":
                    embed=embed_url(video["url"])
                    if embed: st.components.v1.iframe(embed,height=420)
                    else: st.video(video["url"])
                else:
                    path=Path(video["path"])
                    if path.exists(): st.video(str(path))
                    else: st.warning("Uploaded video is not available on this server.")

def main():
    st.set_page_config(page_title="LMS Demo",page_icon="🎓",layout="wide")
    if "role" not in st.session_state: st.session_state.role=None; st.session_state.user=None
    if st.session_state.role is None: login_page()
    elif st.session_state.role=="admin": admin_dashboard()
    else: student_dashboard()

if __name__=="__main__": main()
