import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


def make_question(text, days=0):
    pub_date = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=text, pub_date=pub_date)


class QuestionModelTests(TestCase):
    def test_str_returns_question_text(self):
        question = make_question("Favorite color?")
        self.assertEqual(str(question), "Favorite color?")

    def test_was_published_recently_true_for_new_question(self):
        self.assertTrue(make_question("New").was_published_recently())

    def test_was_published_recently_false_for_old_question(self):
        self.assertFalse(make_question("Old", days=-2).was_published_recently())


class ChoiceModelTests(TestCase):
    def test_str_returns_choice_text(self):
        question = make_question("Pick one")
        choice = Choice.objects.create(question=question, choice_text="Blue")
        self.assertEqual(str(choice), "Blue")


class PollsViewTests(TestCase):
    def test_index_with_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_index_lists_question(self):
        make_question("Is this listed?")
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Is this listed?")

    def test_detail_shows_question(self):
        question = make_question("Detail question")
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertContains(response, "Detail question")

    def test_vote_increments_choice_and_redirects(self):
        question = make_question("Vote question")
        choice = Choice.objects.create(question=question, choice_text="Yes")
        response = self.client.post(
            reverse("polls:vote", args=(question.id,)), {"choice": choice.id}
        )
        self.assertRedirects(response, reverse("polls:results", args=(question.id,)))
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

    def test_vote_without_choice_shows_error(self):
        question = make_question("Error question")
        response = self.client.post(reverse("polls:vote", args=(question.id,)))
        self.assertContains(response, "select a choice")

    def test_results_shows_votes(self):
        question = make_question("Results question")
        Choice.objects.create(question=question, choice_text="Maybe", votes=3)
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertContains(response, "3 votes")
