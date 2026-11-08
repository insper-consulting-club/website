from datetime import date

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from website.models import (
    Article, Member, Partner, PartnerCategory, Program, ProgramCase,
    ProgramComponent, Project, SelectionProcess, SiteConfig,
)


class ArticleDetailSlugTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.article = Article.objects.create(
            title="Artigo de teste",
            description="Resumo de teste",
            link="",
            published=True,
            slug="artigo-de-teste",
        )

    def test_article_is_retrievable_by_slug(self):
        response = self.client.get("/api/articles/artigo-de-teste/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.article.id)
        self.assertEqual(response.data["slug"], "artigo-de-teste")

    def test_article_remains_retrievable_by_numeric_id(self):
        response = self.client.get(f"/api/articles/{self.article.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.article.id)
        self.assertEqual(response.data["slug"], "artigo-de-teste")

    def test_article_without_slug_uses_numeric_id(self):
        self.article.slug = None
        self.article.save(update_fields=["slug"])

        response = self.client.get(f"/api/articles/{self.article.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.article.id)
        self.assertIsNone(response.data["slug"])

    def test_draft_is_not_retrievable_by_slug(self):
        self.article.published = False
        self.article.save(update_fields=["published"])

        response = self.client.get("/api/articles/artigo-de-teste/")

        self.assertEqual(response.status_code, 404)

    def test_draft_is_not_listed(self):
        Article.objects.create(title="Rascunho", description="r", published=False)

        response = self.client.get("/api/articles/")

        self.assertEqual([a["title"] for a in response.data], ["Artigo de teste"])

    def test_list_omits_full_text_and_body_images_but_detail_keeps_them(self):
        listing = self.client.get("/api/articles/").data[0]
        detail = self.client.get(f"/api/articles/{self.article.id}/").data

        self.assertNotIn("content", listing)
        self.assertNotIn("images", listing)
        self.assertIn("content", detail)
        self.assertIn("images", detail)


class MemberTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.current = Member.objects.create(name="Ana", entry_date=date(2025, 1, 1))
        self.former = Member.objects.create(
            name="Bruno", entry_date=date(2024, 1, 1), exit_date=date(2025, 6, 1),
        )

    def test_list_hides_members_with_exit_date(self):
        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([m["name"] for m in response.data], ["Ana"])

    def test_archived_member_profile_is_still_reachable_by_link(self):
        response = self.client.get(f"/api/members/{self.former.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Bruno")


class PartnerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.consulting = PartnerCategory.objects.create(title="Consultoria")
        self.tech = PartnerCategory.objects.create(title="Tecnologia")
        self.visible = Partner.objects.create(
            name="Visível", description="d", logo_url="logo.png", category=self.consulting,
        )
        self.hidden = Partner.objects.create(
            name="Oculto", description="d", logo_url="logo.png",
            category=self.consulting, is_active=False,
        )
        self.other = Partner.objects.create(
            name="Outra", description="d", logo_url="logo.png", category=self.tech,
        )

    def test_list_hides_inactive_partners(self):
        response = self.client.get("/api/partners/")

        names = sorted(p["name"] for p in response.data)
        self.assertEqual(names, ["Outra", "Visível"])

    def test_detail_of_inactive_partner_is_404(self):
        response = self.client.get(f"/api/partners/{self.hidden.id}/")

        self.assertEqual(response.status_code, 404)

    def test_list_filters_by_partner_category_id(self):
        response = self.client.get(f"/api/partners/?category={self.tech.id}")

        self.assertEqual([p["name"] for p in response.data], ["Outra"])

    def test_completed_projects_count_only_counts_active_finished_projects(self):
        done = Project.objects.create(
            title="Concluído", description="d",
            start_date=date(2025, 1, 1), end_date=date(2025, 6, 1),
        )
        ongoing = Project.objects.create(
            title="Em andamento", description="d", start_date=date(2025, 7, 1),
        )
        archived = Project.objects.create(
            title="Arquivado", description="d", is_active=False,
            start_date=date(2024, 1, 1), end_date=date(2024, 6, 1),
        )
        for project in (done, ongoing, archived):
            project.partners.add(self.visible)

        response = self.client.get(f"/api/partners/{self.visible.id}/")

        self.assertEqual(response.data["projects_count"], 2)
        self.assertEqual(response.data["completed_projects_count"], 1)

    def test_list_query_count_does_not_grow_with_partners(self):
        def make_partner(i):
            partner = Partner.objects.create(
                name=f"P{i}", description="d", logo_url="logo.png", category=self.tech,
            )
            project = Project.objects.create(
                title=f"Proj{i}", description="d",
                start_date=date(2025, 1, 1), end_date=date(2025, 6, 1),
            )
            project.partners.add(partner)

        make_partner(1)
        with CaptureQueriesContext(connection) as few:
            self.client.get("/api/partners/")

        for i in range(2, 8):
            make_partner(i)
        with CaptureQueriesContext(connection) as many:
            response = self.client.get("/api/partners/")

        self.assertEqual(len(many), len(few))
        by_name = {p["name"]: p for p in response.data}
        self.assertEqual(by_name["P7"]["completed_projects_count"], 1)
        self.assertEqual(by_name["P7"]["projects"][0]["title"], "Proj7")

    def test_completed_projects_are_listed_newest_first(self):
        for title, end in (("Antigo", date(2024, 6, 1)), ("Recente", date(2025, 6, 1))):
            project = Project.objects.create(
                title=title, description="d", start_date=date(2024, 1, 1), end_date=end,
            )
            project.partners.add(self.visible)

        response = self.client.get(f"/api/partners/{self.visible.id}/")

        self.assertEqual([p["title"] for p in response.data["projects"]], ["Recente", "Antigo"])


class ProjectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.program = Program.objects.create(slug="jornada", label="Jornada", description="d")
        self.in_program = Project.objects.create(
            title="Do programa", description="d", program=self.program,
            start_date=date(2025, 1, 1),
        )
        self.standalone = Project.objects.create(
            title="Avulso", description="d", start_date=date(2025, 2, 1),
        )
        self.archived = Project.objects.create(
            title="Arquivado", description="d", is_active=False,
            start_date=date(2024, 1, 1),
        )

    def test_list_hides_archived_projects(self):
        response = self.client.get("/api/projects/")

        titles = sorted(p["title"] for p in response.data)
        self.assertEqual(titles, ["Avulso", "Do programa"])

    def test_archived_project_detail_is_404(self):
        response = self.client.get(f"/api/projects/{self.archived.id}/")

        self.assertEqual(response.status_code, 404)

    def test_list_filters_by_program_slug(self):
        response = self.client.get("/api/projects/?program=jornada")

        self.assertEqual([p["title"] for p in response.data], ["Do programa"])
        self.assertEqual(response.data[0]["program"], "jornada")

    def test_standalone_project_has_no_program(self):
        response = self.client.get(f"/api/projects/{self.standalone.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["program"])


class ProgramTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.active = Program.objects.create(slug="ativo", label="Ativo", description="d")
        self.inactive = Program.objects.create(
            slug="inativo", label="Inativo", description="d", is_active=False,
        )

    def test_list_hides_inactive_programs(self):
        response = self.client.get("/api/programs/")

        self.assertEqual([p["slug"] for p in response.data], ["ativo"])

    def test_components_of_inactive_programs_are_hidden(self):
        ProgramComponent.objects.create(title="Visível", description="d", program=self.active)
        ProgramComponent.objects.create(title="Oculto", description="d", program=self.inactive)

        response = self.client.get("/api/components/")

        self.assertEqual([c["title"] for c in response.data], ["Visível"])

    def test_components_filter_by_program_slug(self):
        ProgramComponent.objects.create(title="Do ativo", description="d", program=self.active)
        other = Program.objects.create(slug="outro", label="Outro", description="d")
        ProgramComponent.objects.create(title="Do outro", description="d", program=other)

        response = self.client.get("/api/components/?program=outro")

        self.assertEqual([c["title"] for c in response.data], ["Do outro"])

    def test_cases_need_active_case_and_active_program(self):
        ProgramCase.objects.create(
            program=self.active, semester="2025.1", area="A", theme="t",
        )
        ProgramCase.objects.create(
            program=self.active, semester="2024.2", area="Oculto", theme="t",
            is_active=False,
        )
        ProgramCase.objects.create(
            program=self.inactive, semester="2025.1", area="Programa oculto", theme="t",
        )

        response = self.client.get("/api/program-cases/")

        self.assertEqual([c["area"] for c in response.data], ["A"])
        self.assertEqual(response.data[0]["program"], "ativo")

    def test_cases_filter_by_program_slug(self):
        other = Program.objects.create(slug="outro", label="Outro", description="d")
        ProgramCase.objects.create(program=self.active, semester="2025.1", area="A", theme="t")
        ProgramCase.objects.create(program=other, semester="2025.1", area="B", theme="t")

        response = self.client.get("/api/program-cases/?program=outro")

        self.assertEqual([c["area"] for c in response.data], ["B"])


class SelectionProcessTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_returns_404_when_there_is_no_active_process(self):
        SelectionProcess.objects.create(title="Antigo", is_active=False)

        response = self.client.get("/api/selection-process/")

        self.assertEqual(response.status_code, 404)

    def test_activating_a_process_deactivates_the_others(self):
        first = SelectionProcess.objects.create(title="Primeiro")
        second = SelectionProcess.objects.create(title="Segundo")

        first.refresh_from_db()
        self.assertFalse(first.is_active)
        self.assertTrue(second.is_active)

    def test_latest_process_wins_when_more_than_one_is_active(self):
        # Não acontece pelo admin (o save() desativa os outros), mas um update
        # direto no banco pode deixar dois ativos, e a API precisa escolher um.
        SelectionProcess.objects.create(title="Antigo")
        recent = SelectionProcess.objects.create(title="Recente")
        SelectionProcess.objects.update(is_active=True)

        response = self.client.get("/api/selection-process/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], recent.id)

    def test_open_registrations_without_link_are_rejected_by_validation(self):
        process = SelectionProcess(title="PS", registrations_open=True, registration_url="")

        with self.assertRaises(ValidationError) as error:
            process.full_clean()

        self.assertIn("registration_url", error.exception.message_dict)

    def test_open_registrations_without_link_are_reported_as_closed(self):
        # create() não passa pela validação do admin, como um cadastro feito por fora dele.
        SelectionProcess.objects.create(title="PS", registrations_open=True, registration_url="")

        response = self.client.get("/api/selection-process/")

        self.assertFalse(response.data["registrations_open"])

    def test_closed_registrations_with_link_are_reported_as_closed(self):
        SelectionProcess.objects.create(
            title="PS", registrations_open=False,
            registration_url="https://forms.example.com/ps",
        )

        response = self.client.get("/api/selection-process/")

        self.assertFalse(response.data["registrations_open"])

    def test_open_registrations_with_link_are_exposed(self):
        SelectionProcess.objects.create(
            title="PS", registrations_open=True,
            registration_url="https://forms.example.com/ps",
        )

        response = self.client.get("/api/selection-process/")

        self.assertTrue(response.data["registrations_open"])
        self.assertEqual(response.data["registration_url"], "https://forms.example.com/ps")


class HealthTests(TestCase):
    def test_health_does_not_need_the_database(self):
        with self.assertNumQueries(0):
            response = APIClient().get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class ApiCacheHeaderTests(TestCase):
    def test_read_endpoints_can_be_cached_by_the_browser(self):
        response = self.client.get("/api/statistics/")

        self.assertEqual(response["Cache-Control"], "public, max-age=60")

    def test_health_is_never_cached(self):
        response = self.client.get("/api/health/")

        self.assertNotIn("max-age", response.get("Cache-Control", ""))

    def test_errors_are_not_cached(self):
        response = self.client.get("/api/partners/999999/")

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("max-age", response.get("Cache-Control", ""))


class SiteConfigTests(TestCase):
    def test_migration_creates_the_single_record_with_current_texts(self):
        config = SiteConfig.objects.get()

        self.assertEqual(config.pk, 1)
        self.assertEqual(config.email, "insperconsultingclub@gmail.com")
        self.assertIn("## 1. Quais dados coletamos", config.privacy_text)
        self.assertEqual(
            list(config.partner_benefits.values_list("title", flat=True)),
            ["Acesso a talentos", "Visibilidade Institucional", "Cases aplicados à realidade"],
        )

    def test_endpoint_returns_texts_benefits_and_no_photo(self):
        response = APIClient().get("/api/site-config/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["home_hero_title"], "O futuro consultor começa no ICC")
        self.assertEqual(response.data["featured_program_slug"], "jornada-do-consultor")
        self.assertEqual(len(response.data["partner_benefits"]), 3)
        self.assertIsNone(response.data["home_about_photo_url"])
        self.assertNotIn("id", response.data)
        self.assertNotIn("home_about_photo", response.data)

    def test_saving_never_creates_a_second_record(self):
        SiteConfig(email="outro@example.com").save()

        self.assertEqual(SiteConfig.objects.count(), 1)
        self.assertEqual(SiteConfig.get_solo().email, "outro@example.com")

    def test_get_solo_recreates_the_record_if_it_is_missing(self):
        SiteConfig.objects.all().delete()

        self.assertEqual(SiteConfig.get_solo().pk, 1)

    def test_featured_program_slug_must_match_an_existing_program(self):
        config = SiteConfig.get_solo()
        config.featured_program_slug = "nao-existe"
        with self.assertRaises(ValidationError):
            config.clean()

        Program.objects.create(slug="nao-existe", label="Programa", description="d")
        config.clean()

        config.featured_program_slug = ""
        config.clean()


class SiteConfigAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(user)

    def test_list_redirects_to_the_edit_page(self):
        response = self.client.get("/admin/website/siteconfig/")

        self.assertRedirects(response, "/admin/website/siteconfig/1/change/")

    def test_edit_page_opens_but_add_and_delete_are_blocked(self):
        self.assertEqual(self.client.get("/admin/website/siteconfig/1/change/").status_code, 200)
        self.assertEqual(self.client.get("/admin/website/siteconfig/add/").status_code, 403)
        self.assertEqual(self.client.get("/admin/website/siteconfig/1/delete/").status_code, 403)
