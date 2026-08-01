import unittest
import json
from app import app
from database import db
from seed import seed_database

class StudentApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            seed_database()

    def test_dashboard_endpoint(self):
        """Feature 1 & 3: Visual growth dashboard, metrics, completed topics summary."""
        response = self.client.get('/student/dashboard')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('summaryStats', data)
        self.assertIn('weeklyQuizProgress', data)
        self.assertIn('subjectQuizScores', data)
        self.assertIn('nextSession', data)
        self.assertIn('todaysTasks', data)

    def test_progress_endpoint(self):
        """Feature 1 & 3: Completed topics breakdown and learning pace progress."""
        response = self.client.get('/student/progress')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('completedTopics', data)
        self.assertIn('growthMetrics', data)

    def test_faqs_endpoint(self):
        """Feature 2: FAQ section with search filtering."""
        response = self.client.get('/student/faqs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(len(data.get('faqs', [])), 5)

        # Test search filter
        search_res = self.client.get('/student/faqs?q=quiz')
        self.assertEqual(search_res.status_code, 200)
        search_data = json.loads(search_res.data)
        self.assertTrue(search_data.get('success'))

    def test_weekly_quizzes_endpoint(self):
        """Feature 4: Weekly quizzes listing."""
        response = self.client.get('/student/quizzes')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(len(data.get('quizzes', [])), 3)

    def test_quiz_details_and_at_least_5_questions(self):
        """Feature 4: Quiz details with at least 5 questions per quiz."""
        response = self.client.get('/student/quizzes/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        questions = data.get('questions', [])
        self.assertGreaterEqual(len(questions), 5, "Quiz must contain at least 5 questions")

    def test_quiz_submission(self):
        """Feature 4: Quiz submission and score calculation."""
        payload = {
            "answers": {
                "1": "B",
                "2": "B",
                "3": "B",
                "4": "C",
                "5": "A"
            }
        }
        response = self.client.post('/student/quizzes/1/submit', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('score', data)
        self.assertIn('correctCount', data)

    def test_booking_slots_endpoint(self):
        """Features 5 & 6: Booking time slots for Regular and One-to-One sessions."""
        response = self.client.get('/student/booking-slots')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        slots = data.get('bookingSlots', {})
        self.assertIn('regular', slots)
        self.assertIn('oneToOne', slots)

    def test_book_session(self):
        """Features 5 & 6: Session booking action."""
        payload = {"session_id": 1}
        response = self.client.post('/student/book-session', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))

    def test_upcoming_sessions_24h_notice(self):
        """Feature 7: Upcoming session details available at least 24h before session."""
        response = self.client.get('/student/upcoming-sessions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('upcoming_sessions', data)
        upcoming = data.get('upcoming_sessions', [])
        if upcoming:
            self.assertTrue(upcoming[0].get('available_24h_notice'))

    def test_study_tips_endpoint(self):
        """Feature 8: Study shortcuts, techniques, and tips shared post-session."""
        response = self.client.get('/student/study-tips')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('studyTips', data)
        tips = data.get('studyTips', [])
        self.assertGreaterEqual(len(tips), 3)

    def test_interactive_assignments(self):
        """Feature 9: Interactive post-session assignments available same day."""
        response = self.client.get('/student/assignments')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('assignments', data)
        assignments = data.get('assignments', [])
        self.assertGreaterEqual(len(assignments), 4)

        # Update assignment progress
        update_res = self.client.post('/student/assignments/1/update-progress', data=json.dumps({"progress": 75}), content_type='application/json')
        self.assertEqual(update_res.status_code, 200)
        update_data = json.loads(update_res.data)
        self.assertTrue(update_data.get('success'))
        self.assertEqual(update_data.get('progress'), 75)

if __name__ == '__main__':
    unittest.main()
