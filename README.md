# LMS Demo — Streamlit

Simple LMS with separate Admin and Student login.

## Features
- Separate Admin and Student login
- Manual student creation
- Course creation
- Add YouTube/Vimeo videos by URL
- Upload MP4/WebM/MOV videos
- Student video viewing
- Simple JSON storage

### Demo accounts
Admin: `admin` / `admin123`
Student: `student` / `student123`

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit secrets
For production create `.streamlit/secrets.toml`:
```toml
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "change-this-password"
```

## Hosting note
Local uploaded files are not reliable permanent storage on hosted Streamlit deployments. For permanent videos, connect the upload layer to persistent object storage such as Supabase Storage, Cloudinary or AWS S3. For production, use proper database-backed authentication and password hashing.
