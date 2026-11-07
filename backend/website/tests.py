from django.test import TestCase
from rest_framework.test import APIClient

from website.models import Media


class MediaDetailSlugTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.article = Media.objects.create(
			title="Artigo de teste",
			description="Resumo de teste",
			link="",
			published=True,
			slug="artigo-de-teste",
		)

	def test_article_is_retrievable_by_slug(self):
		response = self.client.get("/api/news/artigo-de-teste/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["id"], self.article.id)
		self.assertEqual(response.data["slug"], "artigo-de-teste")

	def test_article_remains_retrievable_by_numeric_id(self):
		response = self.client.get(f"/api/news/{self.article.id}/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["id"], self.article.id)
		self.assertEqual(response.data["slug"], "artigo-de-teste")

	def test_article_without_slug_uses_numeric_id(self):
		self.article.slug = None
		self.article.save(update_fields=["slug"])

		response = self.client.get(f"/api/news/{self.article.id}/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["id"], self.article.id)
		self.assertIsNone(response.data["slug"])

	def test_draft_is_not_retrievable_by_slug(self):
		self.article.published = False
		self.article.save(update_fields=["published"])

		response = self.client.get("/api/news/artigo-de-teste/")

		self.assertEqual(response.status_code, 404)
