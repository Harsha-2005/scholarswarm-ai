import fitz  # PyMuPDF
import os

os.makedirs("sample_data", exist_ok=True)

def create_rahul_resume():
    doc = fitz.open()
    page = doc.new_page()
    
    resume_content = """RAHUL SHARMA
Jalandhar, Punjab, India | Email: rahul.sharma.cs@lpu.in | Phone: +91-98765-43210
GitHub: https://github.com/rahul-ai-dev | LinkedIn: linkedin.com/in/rahul-sharma-ai

CAREER OBJECTIVE & STUDY ABROAD GOAL
Final-year B.Tech Computer Science and Engineering student (CGPA: 8.2/10.0) seeking admission and 
merit/need-based scholarship funding for a Master's program in Artificial Intelligence, Machine Learning, 
or Computer Vision in Canada, Germany, or Singapore (2027 Intake). Coming from a middle-class family 
in Jalandhar, I require tuition waivers, teaching/research assistantships, or international fellowships.

EDUCATION
Lovely Professional University (LPU), Phagwara, Punjab, India
Bachelor of Technology (B.Tech) in Computer Science & Engineering (2023 - 2027)
Current CGPA: 8.20 / 10.0

TECHNICAL SKILLS
- Languages: Python, C++, SQL, JavaScript
- AI/ML Frameworks: PyTorch, TensorFlow, Hugging Face Transformers, LangChain, scikit-learn, OpenCV
- Backend & MLOps: FastAPI, Docker, Git, Linux, Rest APIs, MongoDB, PostgreSQL

KEY AI & ENGINEERING PROJECTS
1. MediScan-RAG: Clinical Diagnostic Assistant using Multimodal RAG
   - Built an end-to-end Retrieval-Augmented Generation pipeline using LangChain, ChromaDB, and Llama-3.
   - Reduced hallucination rates on medical QA datasets by 28% via hybrid dense+sparse retrieval (BM25 + FAISS).
   
2. CropGuard-CV: Real-Time Plant Disease Detection for Punjab Farmers
   - Trained a lightweight MobileNetV3 and YOLOv8 model in PyTorch on 18,000 leaf images with 94.6% accuracy.
   - Deployed as a quantized ONNX model served via FastAPI for low-end Android devices.

3. FinSentiment-BERT: Financial News Sentiment Analyzer
   - Fine-tuned FinBERT using LoRA (PEFT) on Indian stock market news headlines to predict intraday volatility.

ACHIEVEMENTS & EXTRACURRICULARS
- Winner (First Runner-Up), Smart Punjab AI Hackathon 2025 (out of 120 teams).
- Solved 400+ Data Structures and Algorithms problems on LeetCode and Codeforces.
- Student Coordinator, AI & Robotics Club, Jalandhar Tech Chapter.
"""
    rect = fitz.Rect(40, 40, 555, 800)
    page.insert_textbox(rect, resume_content, fontsize=10.5, fontname="helv")
    doc.save("sample_data/rahul_resume.pdf")
    doc.close()
    print("✅ Created sample_data/rahul_resume.pdf")

def create_rahul_marksheet():
    doc = fitz.open()
    page = doc.new_page()
    
    marksheet_content = """OFFICIAL ACADEMIC TRANSCRIPT / CONSOLIDATED MARKSHEET
UNIVERSITY: Lovely Professional University, Punjab, India
STUDENT NAME: Rahul Sharma
REGISTRATION NO: 12309845
PROGRAMME: B.Tech (Computer Science and Engineering)

SEMESTER-WISE GRADE REPORT (Scale: 10.0)
-----------------------------------------------------------------------------------
Course Code | Course Title                                  | Credits | Grade | Points
-----------------------------------------------------------------------------------
CSE101      | Computer Programming in C++                   | 4       | A     | 8.0
MTH166      | Differential Equations and Linear Algebra     | 4       | A+    | 9.0
CSE205      | Data Structures and Algorithms                | 4       | A+    | 9.0
MTH302      | Probability and Statistics for CS             | 4       | A     | 8.0
CSE306      | Computer Networks                             | 3       | B+    | 7.0
CSE316      | Operating Systems                             | 4       | A     | 8.0
CSE320      | Software Engineering                          | 3       | A     | 8.0
INT404      | Artificial Intelligence Essentials            | 4       | O     | 10.0
INT422      | Deep Learning and Neural Networks             | 4       | A+    | 9.0
INT428      | Natural Language Processing                   | 4       | A+    | 9.0
CSE325      | Database Management Systems                   | 3       | A     | 8.0
CSE408      | Design and Analysis of Algorithms             | 4       | B+    | 7.0
-----------------------------------------------------------------------------------

CUMULATIVE PERFORMANCE SUMMARY:
Semesters Completed: 6 of 8
Total Credits Earned: 138
Cumulative Grade Point Average (CGPA): 8.20 / 10.00
Active Backlogs: 0 (Zero)
Medium of Instruction: English
"""
    rect = fitz.Rect(40, 40, 555, 800)
    page.insert_textbox(rect, marksheet_content, fontsize=10, fontname="cour")
    doc.save("sample_data/rahul_marksheet.pdf")
    doc.close()
    print("✅ Created sample_data/rahul_marksheet.pdf")

if __name__ == "__main__":
    create_rahul_resume()
    create_rahul_marksheet()