# 🧠 Attila AI – Academic Voice Assistant for Stevens Institute of Technology

**Attila AI** is a real-time AI-powered academic advisor built for Stevens Institute of Technology. It uses **Twilio Voice**, **OpenAI Realtime API**, **FastAPI**, and **Azure Services** to engage in intelligent phone conversations with students, providing academic guidance, course recommendations, and personalized planning.

---

## 🎯 Features

- **Voice-Based Interaction**: Students call in and interact with Attila in natural conversation.
- **Course Recommendations**: Retrieves personalized course suggestions using semantic search powered by Azure OpenAI and Pinecone.
- **Student Lookup**: Fetches student data like current semester, major, and CGPA using CWID.
- **Deadline Reminders**: Announces important academic deadlines toward the end of the call.
- **Human Escalation**: Automatically emails a human academic advisor when a complex issue is detected.
- **Interrupt Handling**: Detects student interruptions and dynamically adjusts responses.

---

## ⚙️ Tech Stack

- **FastAPI** – Backend server and WebSocket handler
- **Twilio** – Voice call routing and audio streaming via Twilio Media Streams
- **OpenAI Realtime API** – Streaming language model with tool calling
- **Azure OpenAI + Pinecone** – For semantic course recommendations
- **Azure Communication Services** – For email escalation to human advisors
- **LangChain + Pandas** – For embedding and summarizing course data

---

## 🛠️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/attila-ai.git
   cd attila-ai
   ```

2. **Create a `.env` file** and configure the following:
   ```
   COURSES_DATA_PATH=path/to/your/courses.csv

   AZURE_API_KEY=your_azure_openai_key
   AZURE_REGION=your_azure_region
   AZURE_API_BASE=your_azure_api_base_url

   AZURE_EMBEDDING_MODEL=your_model_name
   AZURE_EMBEDDING_VERSION=your_model_version
   AZURE_EMBEDDINGS_BASE=your_embeddings_base_url

   AZURE_EMAIL_URI=your_azure_communication_services_endpoint
   AZURE_EMAIL=your_sender_email

   HUMAN_ADVISOR_EMAIL=academic_advisor@gmail.com

   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_REGION=your_pinecone_region
   PINECONE_HOST=your_pinecone_host
   PINECONE_INDEX=your_pinecone_index_name

   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_number

   WEBSOCKET_URI=your_websocket_uri
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5050
   ```

5. **Set up Twilio Webhook**
   - Configure your Twilio number's **Voice > Webhook** to:
     ```
     https://your-server-url/incoming_call
     ```

---

## 🧪 Example Tools

The AI assistant is equipped with the following tools it can call dynamically:

- `get_student_id`: Fetch student profile from CWID
- `recommend_courses`: Suggest courses based on a query
- `send_email`: Escalate issue to human advisor
- `announce_deadlines`: Share academic deadlines
- `get_summary`: Recap the call before ending

---

## 📞 Call Flow

1. Student calls the Twilio number
2. Twilio connects audio to `/media-stream`
3. Audio is streamed bi-directionally with OpenAI Realtime API
4. Attila uses turn detection and tool-calling to assist
5. Recommendations, deadlines, and escalation handled in real time

---

## 📚 Dataset Format

Course data must be in CSV format with the following columns:
- `bp_id` – Unique course ID
- `summary` – A short summary of the course

## 🚀 Future Functional Enhancements

Here are several high-impact improvements planned for Attila AI that can expand its functionality, intelligence, and usefulness for students and advisors alike.

---

### 🧠 1. Session Persistence & Student Memory

- Store and retrieve past conversations per student using a backend database.
- Let Attila remember student preferences, academic goals, or previous issues across sessions.
- Technologies: PostgreSQL, Redis, or Firebase.

---

### 📊 2. Student Portal Dashboard

- Create a web dashboard where students can:
  - Review conversation summaries
  - Track course recommendations
  - View deadlines, advisor referrals, and semester insights
- Could be extended to advisors for case tracking and analytics.
- Stack: React + FastAPI + Tailwind CSS

---

### 📅 3. Personalized Planning Tools

- Let Attila help students build multi-semester academic plans.
- Consider electives, required cores, interests, and graduation timeline.
- Save and update plans across sessions for consistent advising.

---

Want to contribute to any of these? Open an issue or reach out to [hpatel29@stevens.edu](mailto:hpatel29@stevens.edu).
