import unittest
import sys
import os

# Ensure backend package root is on path when running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from ai_models.resume_parser import ResumeParser
from ai_models.question_generator import QuestionGenerator
from ai_models.reference_answer_generator import ReferenceAnswerGenerator
from ai_models.whisper_service import WhisperService
from ai_models.evaluator import AnswerEvaluator
from utils.session_store import sessions_db


class TestInterviewIQBackend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.parser = ResumeParser()
        self.q_gen = QuestionGenerator()
        self.ans_gen = ReferenceAnswerGenerator()
        self.whisper = WhisperService()
        self.evaluator = AnswerEvaluator()
        sessions_db._sessions.clear()
        if sessions_db.file_path.exists():
            sessions_db.file_path.unlink()

    def test_resume_parser_heuristics(self):
        mock_text = """
        John Doe
        Education:
        B.Tech Computer Science from XYZ University.
        Skills:
        Python, TensorFlow, React, FastAPI, Docker, and PostgreSQL.
        Projects:
        Built Plant Disease Detection model using CNN and PyTorch.
        Certifications:
        AWS Certified Developer Associate.
        """
        text_lower = mock_text.lower()
        skills = self.parser._extract_skills(text_lower)
        techs = self.parser._extract_technologies(text_lower, skills)
        edu = self.parser._extract_education(mock_text)
        certs = self.parser._extract_certifications(mock_text)
        projects = self.parser._extract_projects(mock_text)

        self.assertIn("Python", skills)
        self.assertIn("TensorFlow", skills)
        self.assertTrue(any("b.tech" in item.lower() for item in edu))
        self.assertTrue(any("aws" in item.lower() for item in certs))
        self.assertTrue(any("plant disease detection" in item.lower() for item in projects))

    def test_question_generator(self):
        mock_resume = {
            "skills": ["Python", "TensorFlow", "React"],
            "projects": ["Plant Disease Detection"],
            "technologies": ["Docker"],
            "education": ["B.Tech CSE"],
            "certifications": ["AWS Certified Developer"],
        }
        questions = self.q_gen.generate(mock_resume)
        self.assertEqual(len(questions), 10)
        categories = [q["category"] for q in questions]
        self.assertEqual(categories.count("Technical"), 5)
        self.assertEqual(categories.count("Project-Based"), 3)
        self.assertEqual(categories.count("HR / Behavioral"), 2)

    def test_reference_answer_generator(self):
        test_q = "What is the difference between a list and a tuple in Python, and when would you use each?"
        ans = self.ans_gen.generate_answer(test_q, "Technical")
        self.assertIn("mutable", ans.lower())
        self.assertIn("immutable", ans.lower())

    def test_whisper_service_fallback(self):
        test_q = "What is the difference between a list and a tuple in Python, and when would you use each?"
        result = self.whisper._get_fallback_transcript(test_q)
        self.assertIn("mutable", result.lower())

    def test_answer_evaluator(self):
        ref_ans = "A list is mutable in Python, whereas a tuple is immutable and lightweight."
        cand_good = "Lists are mutable and tuples are immutable in Python. Tuples are also faster."
        res_good = self.evaluator.evaluate("Explain list vs tuple", ref_ans, cand_good)
        self.assertGreaterEqual(res_good["technical_score"], 6.0)

        cand_bad = "I do not know."
        res_bad = self.evaluator.evaluate("Explain list vs tuple", ref_ans, cand_bad)
        self.assertLessEqual(res_bad["technical_score"], 4.0)
        self.assertTrue(len(res_bad["weaknesses"]) > 0)

    def test_api_start_interview(self):
        response = self.client.post("/api/interview/start", json={
            "skills": ["Python", "TensorFlow"],
            "projects": ["Plant Disease Detection"],
            "technologies": ["React"],
            "education": ["B.Tech CSE"],
            "certifications": ["AWS Certified"],
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("session_id", data)
        self.assertEqual(len(data["questions"]), 10)

    def test_api_evaluate_and_report(self):
        start = self.client.post("/api/interview/start", json={
            "skills": ["Python"],
            "projects": ["Test Project"],
            "technologies": ["FastAPI"],
        })
        session_id = start.json()["session_id"]

        eval_resp = self.client.post("/api/interview/evaluate", json={
            "session_id": session_id,
            "question_id": 1,
            "candidate_answer": "Python lists are mutable and tuples are immutable.",
        })
        self.assertEqual(eval_resp.status_code, 200)
        self.assertIn("technical_score", eval_resp.json())
        self.assertIn("weaknesses", eval_resp.json())

        report = self.client.post("/api/interview/report", json={"session_id": session_id})
        self.assertEqual(report.status_code, 200)
        report_data = report.json()
        self.assertIn("overall_score", report_data)
        self.assertEqual(len(report_data["details"]), 10)

    def test_api_skip_question(self):
        start = self.client.post("/api/interview/start", json={
            "skills": ["Python"],
            "projects": [],
            "technologies": [],
        })
        session_id = start.json()["session_id"]

        skip = self.client.post("/api/interview/skip", json={
            "session_id": session_id,
            "question_id": 2,
        })
        self.assertEqual(skip.status_code, 200)

        report = self.client.post("/api/interview/report", json={"session_id": session_id})
        q2 = next(d for d in report.json()["details"] if d["id"] == 2)
        self.assertEqual(q2["technical_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
