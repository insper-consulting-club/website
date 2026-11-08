from datetime import date

from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from pathlib import Path
from unittest import mock

from django.test import override_settings
from django.utils import translation
from django.test import TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from website.models import (
    Article, Member, Partner, PartnerCategory, Program, ProgramCase,
    Directorate, NavItem, ProgramComponent, ProgramContentBlock, Project, SelectionProcess, SiteConfig, SiteText,
)


# As páginas do admin usam arquivos estáticos. O armazenamento do projeto exige o
# manifesto criado pelo collectstatic, que não existe num ambiente limpo; nos
# testes basta o armazenamento simples.
SEM_MANIFESTO = override_settings(STORAGES={
    **settings.STORAGES,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})


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


@SEM_MANIFESTO
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


class ProgramDetailTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.program = Program.objects.create(slug="pedagogico", label="Pedagógico", description="Resumo")
        ProgramContentBlock.objects.create(program=self.program, title="Segundo", text="B", order=2)
        ProgramContentBlock.objects.create(program=self.program, title="Primeiro", text="**A**", order=1)

    def test_detail_returns_blocks_in_order(self):
        response = self.client.get("/api/programs/pedagogico/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([b["title"] for b in response.data["content_blocks"]], ["Primeiro", "Segundo"])
        self.assertIsNone(response.data["content_blocks"][0]["image_url"])
        self.assertEqual(response.data["content_blocks"][0]["image_align"], "right")

    def test_list_does_not_carry_the_blocks(self):
        response = self.client.get("/api/programs/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("content_blocks", response.data[0])

    def test_hidden_or_unknown_program_returns_404(self):
        Program.objects.filter(pk=self.program.pk).update(is_active=False)

        self.assertEqual(self.client.get("/api/programs/pedagogico/").status_code, 404)
        self.assertEqual(self.client.get("/api/programs/nao-existe/").status_code, 404)

    def test_deleting_the_program_deletes_its_blocks(self):
        self.program.delete()

        self.assertEqual(ProgramContentBlock.objects.count(), 0)


class SiteTextTests(TestCase):
    def test_every_catalog_text_exists_in_the_database(self):
        from website.site_texts import TEXTOS

        self.assertEqual(SiteText.objects.count(), len(TEXTOS))
        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Quem constrói o clube")

    def test_sync_keeps_edited_values_and_recreates_missing_ones(self):
        from website.site_texts import sincroniza_textos

        SiteText.objects.filter(key="home.membros_titulo").update(value="Editado pelo ICC")
        SiteText.objects.filter(key="equipe.titulo").delete()
        SiteText.objects.create(key="chave.antiga", group="x", description="x", value="x")

        sincroniza_textos()

        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Editado pelo ICC")
        self.assertTrue(SiteText.objects.filter(key="equipe.titulo").exists())
        self.assertFalse(SiteText.objects.filter(key="chave.antiga").exists())

    def test_endpoint_returns_edited_and_default_texts(self):
        SiteText.objects.filter(key="home.membros_titulo").update(value="Editado pelo ICC")
        SiteText.objects.filter(key="equipe.titulo").delete()

        texts = APIClient().get("/api/site-config/").data["texts"]

        self.assertEqual(texts["home.membros_titulo"], "Editado pelo ICC")
        self.assertEqual(texts["equipe.titulo"], "Nossa Equipe")

    def test_frontend_fallback_file_matches_the_catalog(self):
        from website.management.commands.export_site_texts import gera_arquivo_ts

        arquivo = Path(__file__).resolve().parents[2] / "frontend" / "src" / "textosPadrao.ts"
        if not arquivo.exists():
            self.skipTest("Pasta do frontend indisponível neste ambiente.")
        self.assertEqual(
            arquivo.read_text(encoding="utf-8"), gera_arquivo_ts(),
            "frontend/src/textosPadrao.ts está desatualizado. Rode: python manage.py export_site_texts --saida ../frontend/src/textosPadrao.ts",
        )


@SEM_MANIFESTO
class SiteTextAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(user)
        self.texto = SiteText.objects.get(key="projetos.cases_titulo_varios")

    def test_list_and_edit_pages_open_but_add_and_delete_are_blocked(self):
        self.assertEqual(self.client.get("/admin/website/sitetext/").status_code, 200)
        self.assertEqual(self.client.get(f"/admin/website/sitetext/{self.texto.pk}/change/").status_code, 200)
        self.assertEqual(self.client.get("/admin/website/sitetext/add/").status_code, 403)
        self.assertEqual(self.client.get(f"/admin/website/sitetext/{self.texto.pk}/delete/").status_code, 403)

    def test_editing_must_keep_the_placeholders(self):
        url = f"/admin/website/sitetext/{self.texto.pk}/change/"

        recusado = self.client.post(url, {"value": "Cases do programa"})
        self.assertEqual(recusado.status_code, 200)
        self.texto.refresh_from_db()
        self.assertEqual(self.texto.value, "{programa}: {n} cases")

        aceito = self.client.post(url, {"value": "{n} cases em {programa}"})
        self.assertEqual(aceito.status_code, 302)
        self.texto.refresh_from_db()
        self.assertEqual(self.texto.value, "{n} cases em {programa}")

    def test_restore_action_goes_back_to_the_original_text(self):
        SiteText.objects.filter(pk=self.texto.pk).update(value="{n} outro texto {programa}")

        self.client.post("/admin/website/sitetext/", {
            "action": "restaurar", "_selected_action": [self.texto.pk],
        })

        self.texto.refresh_from_db()
        self.assertEqual(self.texto.value, "{programa}: {n} cases")


class NavItemTests(TestCase):
    def test_migration_reproduces_the_previous_menu(self):
        itens = list(NavItem.objects.values_list("label", "area", "page"))

        self.assertEqual(itens, [
            ("Nossa Equipe", "menu", "equipe"),
            ("Parceiros", "menu", "parceiros"),
            ("Projetos", "menu", "projetos"),
            ("Artigos", "menu", "artigos"),
            ("Seja membro", "rodape", "processo"),
            ("Contato", "menu", "contato"),
            ("Seja membro", "botao", "processo"),
        ])

    def test_endpoint_lists_active_items_with_resolved_paths(self):
        config = SiteConfig.get_solo()
        NavItem.objects.create(site_config=config, label="Instagram", url="https://example.com/ig", order=8)
        NavItem.objects.filter(label="Artigos").update(is_active=False)

        itens = APIClient().get("/api/site-config/").data["nav_items"]
        por_texto = {i["label"]: i for i in itens}

        self.assertNotIn("Artigos", por_texto)
        self.assertEqual(por_texto["Nossa Equipe"]["path"], "/equipe")
        self.assertFalse(por_texto["Nossa Equipe"]["external"])
        self.assertEqual(por_texto["Instagram"]["path"], "https://example.com/ig")
        self.assertTrue(por_texto["Instagram"]["external"])

    def test_home_page_points_to_the_root(self):
        item = NavItem(site_config=SiteConfig.get_solo(), label="Início", page="home")

        self.assertEqual(item.path, "/")

    def test_item_needs_exactly_one_destination(self):
        config = SiteConfig.get_solo()

        with self.assertRaises(ValidationError):
            NavItem(site_config=config, label="x").clean()
        with self.assertRaises(ValidationError):
            NavItem(site_config=config, label="x", page="equipe", url="/equipe").clean()
        NavItem(site_config=config, label="x", page="equipe").clean()
        NavItem(site_config=config, label="x", url="/equipe").clean()

    def test_free_link_must_be_an_address_or_a_site_path(self):
        config = SiteConfig.get_solo()

        with self.assertRaises(ValidationError):
            NavItem(site_config=config, label="x", url="javascript:alert(1)").clean()
        with self.assertRaises(ValidationError):
            NavItem(site_config=config, label="x", url="equipe").clean()
        NavItem(site_config=config, label="x", url="mailto:a@example.com").clean()


class SiteBrandTests(TestCase):
    def test_endpoint_returns_name_description_and_no_images_by_default(self):
        dados = APIClient().get("/api/site-config/").data

        self.assertEqual(dados["site_name"], "Liga Insper Consulting Club")
        self.assertIn("organização estudantil", dados["site_description"])
        self.assertIsNone(dados["logo_url"])
        self.assertIsNone(dados["favicon_url"])
        self.assertIsNone(dados["og_image_url"])
        for campo in ("logo", "favicon", "og_image"):
            self.assertNotIn(campo, dados)


@SEM_MANIFESTO
class TranslationFixesTests(TestCase):
    """A tradução em português do Django traz erros de grafia; locale/ os corrige."""

    def test_misspelled_django_texts_are_fixed(self):
        from django.utils.translation import gettext

        with translation.override("pt-br"):
            self.assertEqual(gettext("Toggle sorting"), "Alternar ordenação")
            self.assertIn("instalação do banco de dados", gettext(
                "Something’s wrong with your database installation. Make sure the appropriate database "
                "tables have been created, and make sure the database is readable by the appropriate user."
            ))
            self.assertIn("dados conflitantes", gettext("Conflicting form data submitted. Please try again."))
            self.assertIn("Obrigado", gettext(
                "There’s been an error. It’s been reported to the site administrators via email and should be "
                "fixed shortly. Thanks for your patience."
            ))

    def test_unfold_texts_are_translated(self):
        from django.utils.translation import gettext, ngettext, pgettext

        with translation.override("pt-br"):
            self.assertEqual(gettext("Apply Filters"), "Aplicar filtros")
            self.assertEqual(gettext("Reset filters"), "Limpar filtros")
            self.assertEqual(gettext("Toggle dark/light mode"), "Alternar entre o modo escuro e o claro")
            self.assertEqual(pgettext("verb", "impersonate"), "personificar")
            self.assertIn("“%(escaped_object)s”", gettext(
                'Are you sure you want to delete the %(object_name)s "%(escaped_object)s"? '
                "All of the following related items will be deleted:"
            ))
            plural = "\n                    Export %(len)s selected items.\n                "
            singular = "\n                    Export %(len)s selected item.\n                "
            self.assertEqual(ngettext(singular, plural, 1).strip(), "Exportar %(len)s item selecionado.")
            self.assertEqual(ngettext(singular, plural, 3).strip(), "Exportar %(len)s itens selecionados.")

    def test_translations_keep_the_placeholders_of_the_original(self):
        import gettext as stdlib_gettext
        import re

        arquivo = Path(__file__).resolve().parents[1] / "locale" / "pt_BR" / "LC_MESSAGES" / "django.mo"
        with open(arquivo, "rb") as f:
            catalogo = stdlib_gettext.GNUTranslations(f)._catalog
        marcas = r"%\(\w+\)s|\{\w*\}"
        verificadas = 0
        for chave, traducao in catalogo.items():
            if not chave:
                continue
            # Plurais vêm como (msgid, n); o contexto vem junto do msgid, separado por \x04.
            msgid = chave[0] if isinstance(chave, tuple) else chave
            msgid = msgid.split("\x04")[-1]
            self.assertEqual(sorted(re.findall(marcas, traducao)), sorted(re.findall(marcas, msgid)), msgid[:60])
            verificadas += 1
        self.assertGreater(verificadas, 100)

    def test_admin_list_page_shows_the_fixed_text(self):
        user = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(user)

        pagina = self.client.get("/admin/website/program/").content.decode()

        self.assertNotIn("ordenção", pagina)


@SEM_MANIFESTO
class AdminNavigationTests(TestCase):
    def test_superuser_sees_every_group_in_order(self):
        from config.navigation import navegacao

        usuario = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        requisicao = mock.Mock(user=usuario)

        grupos = navegacao(requisicao)

        self.assertEqual(
            [g["title"] for g in grupos],
            ["Site", "Equipe", "Parceiros", "Programas e projetos", "Artigos", "Processo seletivo", "Acesso"],
        )
        itens = [i["title"] for g in grupos for i in g["items"]]
        self.assertEqual(len(itens), 17)  # 15 modelos do site, mais Usuários e Grupos
        self.assertIn("Configuração do site", itens)

    def test_limited_user_only_sees_what_they_can_open(self):
        from django.contrib.auth.models import Permission
        from config.navigation import navegacao

        usuario = get_user_model().objects.create_user("editor", "ed@example.com", "senha-de-teste", is_staff=True)
        usuario.user_permissions.add(Permission.objects.get(codename="change_article"))
        usuario = get_user_model().objects.get(pk=usuario.pk)

        grupos = navegacao(mock.Mock(user=usuario))

        self.assertEqual([g["title"] for g in grupos], ["Artigos"])
        self.assertEqual([i["title"] for i in grupos[0]["items"]], ["Artigos"])

    def test_sidebar_is_rendered_in_the_admin(self):
        usuario = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(usuario)

        pagina = self.client.get("/admin/").content.decode()

        for titulo in ("Programas e projetos", "Processo seletivo", "Configuração do site"):
            self.assertIn(titulo, pagina)


class AdminViewOnSiteTests(TestCase):
    @override_settings(FRONTEND_URL="https://exemplo.com.br/")
    def test_buttons_point_to_the_public_pages(self):
        from django.contrib import admin

        def url(modelo, objeto):
            return admin.site._registry[modelo].view_on_site(objeto)

        programa = Program.objects.create(slug="pedagogico", label="Pedagógico", description="d")
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        artigo = Article.objects.create(title="A", description="d", slug="meu-artigo", published=True)
        sem_slug = Article.objects.create(title="B", description="d", published=True)
        parceiro = Partner.objects.create(name="X", description="d")
        membro = Member.objects.create(name="M", entry_date=date(2025, 1, 1))

        self.assertEqual(url(Program, programa), "https://exemplo.com.br/projetos/pedagogico")
        self.assertEqual(url(Project, projeto), f"https://exemplo.com.br/projetos/projeto/{projeto.pk}")
        self.assertEqual(url(Article, artigo), "https://exemplo.com.br/artigos/meu-artigo")
        self.assertEqual(url(Article, sem_slug), f"https://exemplo.com.br/artigos/{sem_slug.pk}")
        self.assertEqual(url(Partner, parceiro), f"https://exemplo.com.br/parceiros/{parceiro.pk}")
        self.assertEqual(url(Member, membro), f"https://exemplo.com.br/equipe/{membro.pk}")
        self.assertEqual(url(SiteConfig, SiteConfig.get_solo()), "https://exemplo.com.br/")

    @override_settings(FRONTEND_URL="https://exemplo.com.br")
    def test_hidden_records_have_no_button(self):
        from django.contrib import admin

        rascunho = Article.objects.create(title="A", description="d", published=False)
        arquivado = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1), is_active=False)
        oculto = Program.objects.create(slug="oculto", label="O", description="d", is_active=False)

        self.assertIsNone(admin.site._registry[Article].view_on_site(rascunho))
        self.assertIsNone(admin.site._registry[Project].view_on_site(arquivado))
        self.assertIsNone(admin.site._registry[Program].view_on_site(oculto))

    @override_settings(FRONTEND_URL="")
    def test_without_the_site_address_there_is_no_button(self):
        from django.contrib import admin

        programa = Program.objects.create(slug="pedagogico", label="Pedagógico", description="d")

        self.assertIsNone(admin.site._registry[Program].view_on_site(programa))


@SEM_MANIFESTO
class AdminReorderTests(TestCase):
    def test_saving_the_list_stores_the_new_order(self):
        usuario = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(usuario)
        Directorate.objects.all().delete()
        alfa, beta, gama = (Directorate.objects.create(name=n, order=i) for i, n in enumerate(["Alfa", "Beta", "Gama"], 1))

        # O Unfold reescreve os números de ordem no navegador ao arrastar; aqui vão prontos.
        dados = {"form-TOTAL_FORMS": "3", "form-INITIAL_FORMS": "3", "form-MIN_NUM_FORMS": "0",
                 "form-MAX_NUM_FORMS": "1000", "_save": "Salvar"}
        for i, (diretoria, ordem) in enumerate(((alfa, 2), (beta, 3), (gama, 1))):
            dados[f"form-{i}-id"] = str(diretoria.pk)
            dados[f"form-{i}-order"] = str(ordem)

        resposta = self.client.post("/admin/website/directorate/", dados)

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual([d.name for d in Directorate.objects.order_by("order")], ["Gama", "Alfa", "Beta"])

    def test_every_ordered_inline_is_sortable(self):
        from django.contrib import admin

        classes = {
            inline
            for modelo_admin in admin.site._registry.values()
            for inline in getattr(modelo_admin, "inlines", [])
            if any(campo.name == "order" for campo in inline.model._meta.get_fields())
        }
        # O cronograma do projeto é ordenado por data, e os participantes do case, por papel.
        fora = {"ProjectTimelineEventInline", "ProgramCaseParticipantInline"}
        for inline in classes:
            if inline.__name__ in fora:
                continue
            self.assertEqual(inline.ordering_field, "order", inline.__name__)
            self.assertTrue(inline.hide_ordering_field, inline.__name__)


@SEM_MANIFESTO
class EditorsGroupTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group

        self.grupo = Group.objects.get(name="Editores")
        self.editor = get_user_model().objects.create_user("editora", "ed@example.com", "senha-de-teste", is_staff=True)
        self.editor.groups.add(self.grupo)

    def codenames(self):
        return set(self.grupo.permissions.values_list("codename", flat=True))

    def test_group_is_created_by_migrate_with_the_expected_permissions(self):
        codenames = self.codenames()

        for esperado in ("change_article", "add_article", "view_member", "change_siteconfig", "change_sitetext",
                         "delete_projectimage", "view_position"):
            self.assertIn(esperado, codenames)
        for proibido in ("delete_article", "delete_member", "delete_project", "add_siteconfig", "delete_siteconfig",
                         "add_sitetext", "add_position", "change_position", "view_user", "change_user", "view_group",
                         "view_navitem", "change_navitem", "view_partnerbenefit", "change_partnerbenefit"):
            self.assertNotIn(proibido, codenames)

    def test_editor_edits_content_but_cannot_reach_users_or_delete_articles(self):
        self.client.force_login(self.editor)
        artigo = Article.objects.create(title="A", description="d", published=True)

        self.assertEqual(self.client.get("/admin/website/article/").status_code, 200)
        self.assertEqual(self.client.get(f"/admin/website/article/{artigo.pk}/change/").status_code, 200)
        self.assertEqual(self.client.get("/admin/website/siteconfig/1/change/").status_code, 200)
        self.assertEqual(self.client.get("/admin/auth/user/").status_code, 403)
        self.assertEqual(self.client.get("/admin/auth/group/").status_code, 403)
        self.assertEqual(self.client.get(f"/admin/website/article/{artigo.pk}/delete/").status_code, 403)

    def test_editor_sees_no_access_group_in_the_menu(self):
        from config.navigation import navegacao

        usuario = get_user_model().objects.get(pk=self.editor.pk)
        titulos = [g["title"] for g in navegacao(mock.Mock(user=usuario))]

        self.assertIn("Site", titulos)
        self.assertIn("Artigos", titulos)
        self.assertNotIn("Acesso", titulos)

    def test_migrate_keeps_adjustments_made_in_the_admin(self):
        from django.apps import apps
        from django.contrib.auth.models import Permission
        from website.editors_group import sincroniza_grupo_editores

        self.grupo.permissions.add(Permission.objects.get(codename="delete_article"))
        self.grupo.permissions.remove(Permission.objects.get(codename="change_sitetext"))

        self.assertFalse(sincroniza_grupo_editores(apps, apps.get_app_config("website")))

        self.assertIn("delete_article", self.codenames())
        self.assertNotIn("change_sitetext", self.codenames())

    def test_deleting_the_group_brings_back_the_default_on_the_next_migrate(self):
        from django.apps import apps
        from django.contrib.auth.models import Group, Permission
        from website.editors_group import sincroniza_grupo_editores

        self.grupo.permissions.add(Permission.objects.get(codename="delete_article"))
        self.grupo.delete()

        self.assertTrue(sincroniza_grupo_editores(apps, apps.get_app_config("website")))

        novo = Group.objects.get(name="Editores")
        codenames = set(novo.permissions.values_list("codename", flat=True))
        self.assertNotIn("delete_article", codenames)
        self.assertIn("change_article", codenames)
        # Quem estava no grupo apagado precisa ser colocado de novo.
        self.assertFalse(novo.user_set.exists())


class BrandImageValidationTests(TestCase):
    def imagem(self, largura, altura, nome="imagem.png"):
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGB", (largura, altura), "red").save(buffer, format="PNG")
        return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/png")

    def formulario(self, **arquivos):
        from django.forms.models import model_to_dict
        from website.admin import SiteConfigForm

        config = SiteConfig.get_solo()
        dados = {k: v for k, v in model_to_dict(config).items()
                 if v is not None and k not in ("logo", "favicon", "og_image", "home_about_photo")}
        # O banco de teste não tem o programa do slug padrão, e essa regra não é o assunto aqui.
        dados["featured_program_slug"] = ""
        return SiteConfigForm(data=dados, files=arquivos, instance=config)

    def test_square_favicon_is_accepted(self):
        self.assertTrue(self.formulario(favicon=self.imagem(256, 256)).is_valid())

    def test_non_square_favicon_is_refused_with_the_real_size(self):
        form = self.formulario(favicon=self.imagem(300, 200))

        self.assertFalse(form.is_valid())
        self.assertIn("300 x 200", form.errors["favicon"][0])
        self.assertIn("quadrado", form.errors["favicon"][0])

    def test_tiny_favicon_is_refused(self):
        self.assertIn("pequeno demais", self.formulario(favicon=self.imagem(16, 16)).errors["favicon"][0])

    def test_share_image_with_the_right_proportion_is_accepted(self):
        self.assertTrue(self.formulario(og_image=self.imagem(1200, 630)).is_valid())
        self.assertTrue(self.formulario(og_image=self.imagem(800, 420)).is_valid())

    def test_share_image_too_small_or_too_square_is_refused(self):
        self.assertIn("pequena demais", self.formulario(og_image=self.imagem(400, 210)).errors["og_image"][0])
        self.assertIn("proporção", self.formulario(og_image=self.imagem(1000, 1000)).errors["og_image"][0])
        self.assertIn("proporção", self.formulario(og_image=self.imagem(1200, 300)).errors["og_image"][0])

    def test_logo_has_no_size_requirement(self):
        self.assertTrue(self.formulario(logo=self.imagem(40, 400)).is_valid())

    def test_saving_without_new_images_does_not_measure_anything(self):
        with mock.patch("website.admin.get_image_dimensions") as medir:
            self.assertTrue(self.formulario().is_valid())

        medir.assert_not_called()


@SEM_MANIFESTO
class AdminLoginRedirectTests(TestCase):
    def test_login_without_next_goes_to_the_admin(self):
        get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")

        resposta = self.client.post("/admin/login/", {"username": "root", "password": "senha-de-teste"})

        self.assertRedirects(resposta, "/admin/", fetch_redirect_response=False)


@SEM_MANIFESTO
class MarkdownPreviewWidgetTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(self.admin)

    @override_settings(FRONTEND_URL="https://exemplo.com.br/")
    def test_article_page_has_the_preview_with_the_saved_images(self):
        artigo = Article.objects.create(title="A", description="d")
        from website.models import ArticleImage
        ArticleImage.objects.create(article=artigo, number=1, image="articles/x.png", caption="Legenda 1")

        pagina = self.client.get(f"/admin/website/article/{artigo.pk}/change/").content.decode()

        self.assertIn('data-url="https://exemplo.com.br/previa"', pagina)
        self.assertIn('data-modo="artigo"', pagina)
        self.assertIn("Legenda 1", pagina)
        self.assertIn("markdown_preview.js", pagina)

    @override_settings(FRONTEND_URL="https://exemplo.com.br")
    def test_each_markdown_field_uses_its_own_style(self):
        programa = Program.objects.create(slug="p", label="P", description="d")

        config = self.client.get("/admin/website/siteconfig/1/change/").content.decode()
        prog = self.client.get(f"/admin/website/program/{programa.pk}/change/").content.decode()

        self.assertIn('data-modo="politica"', config)
        self.assertIn('data-modo="programa"', prog)

    @override_settings(FRONTEND_URL="")
    def test_without_the_site_address_the_field_has_no_preview_button(self):
        artigo = Article.objects.create(title="A", description="d")

        pagina = self.client.get(f"/admin/website/article/{artigo.pk}/change/").content.decode()

        self.assertNotIn("md-previa__botao", pagina)
        self.assertIn('name="content"', pagina)


class TrajectoryMigrationTests(TransactionTestCase):
    """A trajetória deixou de ser um JSON no membro e virou linhas (migrations 0021 a 0023)."""

    ANTES = ("website", "0021_etapas_da_trajetoria_e_nomes")
    DEPOIS = ("website", "0022_copia_trajetoria_para_etapas")

    def _estado(self, alvo):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate([alvo])
        return MigrationExecutor(connection).loader.project_state([alvo]).apps

    def tearDown(self):
        # Devolve o banco ao estado final para os testes seguintes.
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_json_trajectory_is_copied_and_malformed_entries_are_skipped(self):
        antigo = self._estado(self.ANTES)
        Member = antigo.get_model("website", "Member")
        membro = Member.objects.create(
            name="Ana", entry_date=date(2024, 2, 1),
            trajetoria=[
                {"semestre": "2025.1", "cargo": "Membro"},
                {"semestre": "2024.2", "cargo": "Trainee"},
                {"semestre": "2024.2", "cargo": "Trainee"},  # repetida
                {"semestre": "2026", "cargo": "Diretora"},  # semestre fora do padrão
                {"semestre": "2025.2"},  # sem cargo
                "texto solto",  # não é um objeto
            ],
        )
        Member.objects.create(name="Bia", entry_date=date(2024, 2, 1), trajetoria=[])

        novo = self._estado(self.DEPOIS)
        etapas = novo.get_model("website", "MemberTrajectory").objects.filter(member_id=membro.pk).order_by("semester")

        self.assertEqual([(e.semester, e.role) for e in etapas], [("2024.2", "Trainee"), ("2025.1", "Membro")])
        self.assertEqual(novo.get_model("website", "MemberTrajectory").objects.count(), 2)

    def test_migrating_back_restores_the_json_in_semester_order(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        membro = Member.objects.create(name="Ana", entry_date=date(2024, 2, 1))
        membro.trajectory_steps.create(semester="2025.1", role="Membro")
        membro.trajectory_steps.create(semester="2024.2", role="Trainee")

        antigo = self._estado(self.ANTES)

        restaurado = antigo.get_model("website", "Member").objects.get(pk=membro.pk)
        self.assertEqual(
            restaurado.trajetoria,
            [{"semestre": "2024.2", "cargo": "Trainee"}, {"semestre": "2025.1", "cargo": "Membro"}],
        )


class TrajectoryTests(TestCase):
    def setUp(self):
        self.membro = Member.objects.create(name="Ana", entry_date=date(2024, 2, 1))

    def test_profile_api_keeps_the_same_format_in_semester_order(self):
        self.membro.trajectory_steps.create(semester="2025.2", role="Presidente")
        self.membro.trajectory_steps.create(semester="2024.1", role="Trainee")

        dados = APIClient().get(f"/api/members/{self.membro.pk}/").data

        self.assertEqual(
            [dict(e) for e in dados["trajetoria"]],
            [{"semestre": "2024.1", "cargo": "Trainee"}, {"semestre": "2025.2", "cargo": "Presidente"}],
        )

    def test_member_without_steps_has_an_empty_list(self):
        self.assertEqual(APIClient().get(f"/api/members/{self.membro.pk}/").data["trajetoria"], [])

    def test_semester_must_follow_the_pattern(self):
        from website.models import MemberTrajectory

        for invalido in ("2026", "2026.3", "26.1", "2026-1", "semestre"):
            with self.assertRaises(ValidationError, msg=invalido):
                MemberTrajectory(member=self.membro, semester=invalido, role="Trainee").full_clean()
        MemberTrajectory(member=self.membro, semester="2026.1", role="Trainee").full_clean()

    def test_the_same_step_cannot_be_repeated(self):
        from website.models import MemberTrajectory

        self.membro.trajectory_steps.create(semester="2026.1", role="Trainee")

        with self.assertRaises(ValidationError):
            MemberTrajectory(member=self.membro, semester="2026.1", role="Trainee").full_clean()

    def test_profile_query_count_does_not_grow_with_the_steps(self):
        for i in range(1, 6):
            self.membro.trajectory_steps.create(semester=f"202{i}.1", role="Membro")

        with CaptureQueriesContext(connection) as poucas:
            APIClient().get(f"/api/members/{self.membro.pk}/")
        for i in range(1, 6):
            self.membro.trajectory_steps.create(semester=f"202{i}.2", role="Membro")
        with CaptureQueriesContext(connection) as muitas:
            APIClient().get(f"/api/members/{self.membro.pk}/")

        self.assertEqual(len(poucas), len(muitas))


class FlushTests(TransactionTestCase):
    def test_flush_recreates_the_texts_and_the_editors_group(self):
        from django.contrib.auth.models import Group
        from django.core.management import call_command

        SiteText.objects.all().delete()

        call_command("flush", interactive=False, verbosity=0)

        self.assertGreater(SiteText.objects.count(), 100)
        self.assertTrue(Group.objects.filter(name="Editores").exists())


@SEM_MANIFESTO
class AdminLayoutTests(TestCase):
    def test_admin_pages_load_the_project_stylesheet(self):
        usuario = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(usuario)

        pagina = self.client.get("/admin/").content.decode()

        self.assertIn("website/admin.css", pagina)

    def test_models_have_a_portuguese_singular_name(self):
        from django.apps import apps

        for modelo in apps.get_app_config("website").get_models():
            nome = str(modelo._meta.verbose_name)
            self.assertTrue(nome[0].isupper(), f"{modelo.__name__}: nome no singular em inglês ou sem maiúscula ({nome!r})")


class SelectionProcessDuplicateTests(TestCase):
    def setUp(self):
        from website.models import (
            PreparationMaterial, PreparationMaterialItem, SelectionProcessRequirement,
            SelectionProcessStage, SelectionProcessStep,
        )

        self.original = SelectionProcess.objects.create(
            title="PS 2026.1", is_active=True, registrations_open=True, registration_url="https://forms.example/ps-2026-1",
        )
        SelectionProcessStage.objects.create(process=self.original, label="Inscrição", date="1 a 10 de março", order=1)
        SelectionProcessStep.objects.create(
            process=self.original, number="01", title="Dinâmica", description="Em grupo", duration="60 min",
            tips="Escute\nSintetize", image="process/steps/x.png", order=1,
        )
        SelectionProcessRequirement.objects.create(process=self.original, text="Ser aluno do Insper", order=1)
        material = PreparationMaterial.objects.create(process=self.original, title="Case", order=1)
        PreparationMaterialItem.objects.create(material=material, text="Livro A", order=1)
        PreparationMaterialItem.objects.create(material=material, text="Livro B", order=2)

    def test_copy_has_everything_but_starts_inactive_and_closed(self):
        copia = self.original.duplicate()

        self.assertEqual(copia.title, "PS 2026.1 (cópia)")
        self.assertFalse(copia.is_active)
        self.assertFalse(copia.registrations_open)
        self.assertEqual(copia.registration_url, "")
        self.assertEqual([(e.label, e.date) for e in copia.stages.all()], [("Inscrição", "1 a 10 de março")])
        passo = copia.steps.get()
        self.assertEqual((passo.title, passo.tips, passo.image.name), ("Dinâmica", "Escute\nSintetize", "process/steps/x.png"))
        self.assertEqual([r.text for r in copia.requirements.all()], ["Ser aluno do Insper"])
        self.assertEqual([i.text for i in copia.materials.get().items.all()], ["Livro A", "Livro B"])

    def test_original_stays_untouched_and_active(self):
        self.original.duplicate()

        self.original.refresh_from_db()
        self.assertTrue(self.original.is_active)
        self.assertTrue(self.original.registrations_open)
        self.assertEqual(self.original.stages.count(), 1)
        self.assertEqual(SelectionProcess.objects.count(), 2)

    def test_copy_is_independent_from_the_original(self):
        copia = self.original.duplicate()
        copia.stages.all().delete()

        self.assertEqual(self.original.stages.count(), 1)

    def test_a_failure_in_the_middle_leaves_no_half_copy(self):
        with mock.patch("website.models.PreparationMaterialItem.objects.create", side_effect=RuntimeError("falhou")):
            with self.assertRaises(RuntimeError):
                self.original.duplicate()

        self.assertEqual(SelectionProcess.objects.count(), 1)


@SEM_MANIFESTO
class AdminBulkActionsTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(self.admin)

    def acao(self, modelo, nome, ids):
        return self.client.post(f"/admin/website/{modelo}/", {"action": nome, "_selected_action": ids}, follow=True)

    def test_publish_and_unpublish_articles_in_bulk(self):
        a = Article.objects.create(title="A", description="d", published=False, date=date(2026, 1, 1))
        b = Article.objects.create(title="B", description="d", published=False)

        resposta = self.acao("article", "publicar", [a.pk, b.pk])

        a.refresh_from_db(); b.refresh_from_db()
        self.assertTrue(a.published and b.published)
        self.assertContains(resposta, "2 artigo(s) publicado(s)")
        self.assertContains(resposta, "sem data de publicação")

        self.acao("article", "despublicar", [a.pk])
        a.refresh_from_db()
        self.assertFalse(a.published)

    def test_duplicate_action_in_the_list_and_on_the_edit_page(self):
        processo = SelectionProcess.objects.create(title="PS", is_active=True)

        self.acao("selectionprocess", "duplicar", [processo.pk])
        self.assertEqual(SelectionProcess.objects.filter(title="PS (cópia)").count(), 1)

        resposta = self.client.get(f"/admin/website/selectionprocess/{processo.pk}/change/")
        self.assertContains(resposta, "Duplicar este processo")

    def test_user_without_add_permission_cannot_duplicate(self):
        from django.contrib.auth.models import Permission

        usuario = get_user_model().objects.create_user("lê", "l@example.com", "senha-de-teste", is_staff=True)
        usuario.user_permissions.add(*Permission.objects.filter(codename__in=["view_selectionprocess", "change_selectionprocess"]))
        self.client.force_login(usuario)
        processo = SelectionProcess.objects.create(title="PS", is_active=True)

        self.acao("selectionprocess", "duplicar", [processo.pk])

        self.assertEqual(SelectionProcess.objects.count(), 1)


class ImageSizeLimitTests(TestCase):
    def arquivo(self, bytes_):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile("foto.png", b"x" * bytes_, content_type="image/png")

    def test_new_upload_above_the_limit_is_refused_with_the_size_in_the_message(self):
        from django.db.models.fields.files import FieldFile
        from website.fields import valida_tamanho_da_imagem

        novo = FieldFile(None, Member._meta.get_field("photo"), "foto.png")
        novo.file = self.arquivo(6 * 1024 * 1024)
        novo._committed = False

        with self.assertRaises(ValidationError) as erro:
            valida_tamanho_da_imagem(novo)

        self.assertIn("6,0 MB", erro.exception.messages[0])
        self.assertIn("limite é 5 MB", erro.exception.messages[0])

    def test_new_upload_within_the_limit_is_accepted(self):
        from django.db.models.fields.files import FieldFile
        from website.fields import valida_tamanho_da_imagem

        novo = FieldFile(None, Member._meta.get_field("photo"), "foto.png")
        novo.file = self.arquivo(1024)
        novo._committed = False

        valida_tamanho_da_imagem(novo)

    def test_stored_image_is_never_measured(self):
        from website.fields import valida_tamanho_da_imagem

        guardada = mock.Mock(_committed=True)
        type(guardada).size = mock.PropertyMock(side_effect=AssertionError("não deveria consultar o armazenamento"))

        valida_tamanho_da_imagem(guardada)

    @override_settings(MAX_IMAGE_UPLOAD_MB=1)
    def test_the_limit_comes_from_the_settings(self):
        from django.db.models.fields.files import FieldFile
        from website.fields import valida_tamanho_da_imagem

        novo = FieldFile(None, Member._meta.get_field("photo"), "foto.png")
        novo.file = self.arquivo(2 * 1024 * 1024)
        novo._committed = False

        with self.assertRaises(ValidationError):
            valida_tamanho_da_imagem(novo)

    def test_the_admin_form_refuses_a_large_real_image(self):
        import io
        import os
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        from website.admin import MemberForm

        buffer = io.BytesIO()
        Image.frombytes("RGB", (1600, 1600), os.urandom(1600 * 1600 * 3)).save(buffer, format="PNG")
        self.assertGreater(buffer.tell(), 5 * 1024 * 1024)
        form = MemberForm(
            data={"name": "Ana", "entry_date": "2024-02-01", "projects": []},
            files={"photo": SimpleUploadedFile("foto.png", buffer.getvalue(), content_type="image/png")},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("limite é 5 MB", form.errors["photo"][0])

    def test_migrations_still_see_a_plain_image_field(self):
        from django.core.management import call_command

        # Se o campo mudasse de caminho nas migrations, isto geraria uma migration nova.
        call_command("makemigrations", "--check", "--dry-run", verbosity=0)


@SEM_MANIFESTO
class DelayNoticeTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.client.force_login(self.admin)
        from website.models import Statistic
        self.estatistica = Statistic.objects.create(value="10", description="membros", order=1)

    def salvar(self):
        return self.client.post(
            f"/admin/website/statistic/{self.estatistica.pk}/change/",
            {"value": "12", "description": "membros", "order": "1", "_continue": "1"}, follow=True,
        )

    @override_settings(API_CACHE_SECONDS=60)
    def test_saving_warns_about_the_delay(self):
        self.assertContains(self.salvar(), "em até 1 minuto")

    @override_settings(API_CACHE_SECONDS=120)
    def test_the_time_follows_the_setting(self):
        self.assertContains(self.salvar(), "em até 2 minutos")

    @override_settings(API_CACHE_SECONDS=0)
    def test_no_warning_when_the_cache_is_off(self):
        self.assertNotContains(self.salvar(), "em até")

    @override_settings(API_CACHE_SECONDS=60)
    def test_saving_a_whole_list_gives_one_warning_only(self):
        from website.models import Directorate

        Directorate.objects.all().delete()
        a, b = (Directorate.objects.create(name=n, order=i) for i, n in enumerate(["Alfa", "Beta"], 1))
        dados = {"form-TOTAL_FORMS": "2", "form-INITIAL_FORMS": "2", "form-MIN_NUM_FORMS": "0",
                 "form-MAX_NUM_FORMS": "1000", "_save": "Salvar",
                 "form-0-id": str(a.pk), "form-0-order": "2", "form-1-id": str(b.pk), "form-1-order": "1"}

        resposta = self.client.post("/admin/website/directorate/", dados, follow=True)

        self.assertEqual(resposta.content.decode().count("em até 1 minuto"), 1)

    def test_users_and_groups_do_not_get_the_notice(self):
        from django.contrib import admin
        from website.admin import AvisoDeAtrasoMixin

        for modelo in (get_user_model(), __import__("django.contrib.auth.models", fromlist=["Group"]).Group):
            self.assertNotIsInstance(admin.site._registry[modelo], AvisoDeAtrasoMixin)


class PasswordAndSessionPolicyTests(TestCase):
    """O login do /admin não limita tentativas; a defesa é a senha longa e a sessão curta."""

    def test_passwords_need_at_least_twelve_characters(self):
        from django.contrib.auth.password_validation import validate_password

        with self.assertRaises(ValidationError) as erro:
            validate_password("Onze-chars1")  # 11 caracteres
        self.assertTrue(any("12 caracteres" in m for m in erro.exception.messages))

        validate_password("Doze-chars-ok")  # 13 caracteres, não é comum nem só números

    def test_common_and_numeric_passwords_are_still_refused(self):
        from django.contrib.auth.password_validation import CommonPasswordValidator, validate_password

        # Uma senha comum que já passa do mínimo de 12 caracteres, tirada da lista do próprio Django.
        comum = next(s for s in sorted(CommonPasswordValidator().passwords) if len(s) >= 12 and not s.isdigit())

        for fraca in (comum, "123456789012345"):
            with self.assertRaises(ValidationError, msg=fraca):
                validate_password(fraca)

    def test_session_expires_after_twelve_hours_without_use(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 12 * 60 * 60)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)


@SEM_MANIFESTO
class ActionPermissionTests(TestCase):
    """Toda ação em lote do projeto exige uma permissão; quem só pode ler não consegue executá-la."""

    def test_every_custom_bulk_action_declares_the_permission_it_needs(self):
        from django.contrib import admin

        sem_permissao = []
        for modelo, modelo_admin in admin.site._registry.items():
            if modelo._meta.app_label != "website":
                continue
            for nome in modelo_admin.actions:
                if not getattr(getattr(modelo_admin, nome), "allowed_permissions", None):
                    sem_permissao.append(f"{modelo.__name__}.{nome}")

        self.assertEqual(sem_permissao, [])

    def test_a_read_only_user_cannot_archive_members_or_restore_texts(self):
        from django.contrib.auth.models import Permission
        from website.models import SiteText

        leitor = get_user_model().objects.create_user("leitor", "l@example.com", "senha-de-teste", is_staff=True)
        leitor.user_permissions.add(*Permission.objects.filter(codename__in=["view_member", "view_project", "view_sitetext"]))
        self.client.force_login(leitor)
        membro = Member.objects.create(name="Ana", entry_date=date(2024, 2, 1))
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        texto = SiteText.objects.get(key="equipe.titulo")
        SiteText.objects.filter(pk=texto.pk).update(value="Editado")

        self.client.post("/admin/website/member/", {"action": "arquivar", "_selected_action": [membro.pk]})
        self.client.post("/admin/website/project/", {"action": "arquivar", "_selected_action": [projeto.pk]})
        self.client.post("/admin/website/sitetext/", {"action": "restaurar", "_selected_action": [texto.pk]})

        membro.refresh_from_db(); projeto.refresh_from_db(); texto.refresh_from_db()
        self.assertIsNone(membro.exit_date)
        self.assertTrue(projeto.is_active)
        self.assertEqual(texto.value, "Editado")

    def test_the_editors_group_can_still_use_the_actions(self):
        from django.contrib.auth.models import Group

        editora = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste", is_staff=True)
        editora.groups.add(Group.objects.get(name="Editores"))
        self.client.force_login(editora)
        membro = Member.objects.create(name="Ana", entry_date=date(2024, 2, 1))

        self.client.post("/admin/website/member/", {"action": "arquivar", "_selected_action": [membro.pk]})

        membro.refresh_from_db()
        self.assertIsNotNone(membro.exit_date)


@SEM_MANIFESTO
class SeedDataTests(TestCase):
    """Dados de exemplo do ambiente local (seed_mock_data): completos, fictícios e sem duplicar."""

    @classmethod
    def setUpClass(cls):
        import tempfile

        # As configurações precisam valer antes de super(), que é quem chama setUpTestData.
        pasta = tempfile.TemporaryDirectory()
        cls.addClassCleanup(pasta.cleanup)
        cls.enterClassContext(override_settings(MEDIA_ROOT=pasta.name, DEBUG=True))
        cls.pasta_de_midia = pasta.name
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command

        call_command("seed_mock_data", stdout=mock.Mock())

    def arquivos_de_midia(self):
        return sorted(str(p) for p in Path(self.pasta_de_midia).rglob("*") if p.is_file())

    # --- o que ele cria

    def test_creates_the_whole_site(self):
        from website.models import Directorate, Partner, Position, PreparationMaterial, ProgramCase, Statistic

        self.assertEqual(Member.objects.count(), 16)
        self.assertEqual(Partner.objects.count(), 8)
        self.assertEqual(Program.objects.count(), 5)
        self.assertEqual(Project.objects.count(), 7)
        self.assertEqual(Article.objects.count(), 7)
        self.assertEqual(SelectionProcess.objects.count(), 2)
        self.assertEqual(ProgramCase.objects.count(), 6)
        self.assertEqual(Statistic.objects.count(), 4)
        self.assertEqual(Directorate.objects.count(), 5)
        self.assertEqual(Position.objects.count(), 9)
        self.assertEqual(PreparationMaterial.objects.count(), 2)

    def test_the_four_real_programs_keep_their_real_names_and_the_featured_slug_exists(self):
        nomes = list(Program.objects.filter(is_active=True).order_by("order").values_list("label", flat=True))

        self.assertEqual(nomes, ["Jornada do Consultor", "Pedagógico", "Escola de Mentores", "Departamento de Alumni"])
        self.assertEqual(SiteConfig.get_solo().featured_program_slug, "jornada-do-consultor")
        self.assertTrue(Program.objects.filter(slug="jornada-do-consultor", is_active=True).exists())

    def test_site_configuration_texts_are_not_touched(self):
        padrao = SiteConfig._meta.get_field("home_hero_title").default

        self.assertEqual(SiteConfig.get_solo().home_hero_title, padrao)
        self.assertEqual(NavItem.objects.filter(label="Nossa Equipe", area="menu").count(), 1)

    # --- idempotência

    def test_running_again_does_not_duplicate_anything(self):
        from django.core.management import call_command
        from website.models import MemberTrajectory, ProgramContentBlock

        antes = {m.__name__: m.objects.count() for m in (
            Member, Article, Project, Program, SelectionProcess, NavItem, MemberTrajectory, ProgramContentBlock)}
        arquivos = self.arquivos_de_midia()

        call_command("seed_mock_data", stdout=mock.Mock())

        depois = {m.__name__: m.objects.count() for m in (
            Member, Article, Project, Program, SelectionProcess, NavItem, MemberTrajectory, ProgramContentBlock)}
        self.assertEqual(antes, depois)
        self.assertEqual(arquivos, self.arquivos_de_midia())

    def test_running_again_restores_an_edited_example_and_removes_a_stale_child(self):
        from django.core.management import call_command
        from website.models import MemberTrajectory

        helena = Member.objects.get(name="Helena Prado")
        Member.objects.filter(pk=helena.pk).update(hours=1)
        MemberTrajectory.objects.create(member=helena, semester="2030.1", role="Cargo que o seed não conhece")

        call_command("seed_mock_data", stdout=mock.Mock())

        helena.refresh_from_db()
        self.assertEqual(helena.hours, 460)
        self.assertFalse(helena.trajectory_steps.filter(semester="2030.1").exists())

    # --- casos de borda

    def test_edge_cases_are_present(self):
        from website.models import DirectorateMembership, Partner, ProgramCase

        sem_logo_nem_site = Partner.objects.get(name="Horizonte Educação")
        self.assertFalse(sem_logo_nem_site.logo_url)
        self.assertIsNone(sem_logo_nem_site.site)
        self.assertFalse(Partner.objects.get(name="Antiga Parceira Ltda").is_active)
        self.assertFalse(Program.objects.get(slug="programa-em-reformulacao").is_active)
        self.assertEqual(Program.objects.get(slug="departamento-de-alumni").badge, "")
        self.assertFalse(ProgramCase.objects.filter(is_active=False).get().is_active)

        mateus = Member.objects.get(name="Mateus Ribeiro")
        self.assertIsNone(mateus.email)
        self.assertIsNone(mateus.linkedin)
        self.assertFalse(mateus.trajectory_steps.exists())
        self.assertEqual(Member.objects.filter(exit_date__isnull=False).count(), 2)
        self.assertGreater(max(len(m.name) for m in Member.objects.all()), 50)
        duas = Member.objects.get(name="Isabela Fontes")
        self.assertEqual(DirectorateMembership.objects.filter(member=duas).count(), 2)

        self.assertFalse(Article.objects.get(title="Rascunho ainda não publicado").published)
        self.assertIsNone(Article.objects.get(title="Transformação digital em PMEs: barreiras e alavancas").slug)
        self.assertEqual(Article.objects.get(slug="entrevista-com-uma-mentora").content, "")
        self.assertGreater(max(len(a.title) for a in Article.objects.all()), 120)

        self.assertFalse(Project.objects.get(title="Projeto piloto descontinuado").is_active)
        um_dia = Project.objects.get(title="Visita técnica a uma consultoria parceira")
        self.assertEqual(um_dia.start_date, um_dia.end_date)
        self.assertIsNone(um_dia.program)
        minimo = Project.objects.get(title="Projeto mínimo, sem parceiros nem programa")
        self.assertFalse(minimo.partners.exists() or minimo.members.exists() or minimo.timeline_events.exists())
        self.assertIsNone(Project.objects.get(title="Estratégia de entrada em novo mercado").end_date)

        self.assertEqual(NavItem.objects.get(label="Eventos (em breve)").is_active, False)
        self.assertEqual(NavItem.objects.get(label="Código no GitHub").area, "rodape")

    def test_the_public_api_hides_what_is_hidden(self):
        api = APIClient()

        nomes = [m["name"] for m in api.get("/api/members/").data]
        self.assertNotIn("Carolina Mendonça", nomes)  # ex-membro
        self.assertEqual(len(nomes), 14)
        self.assertNotIn("programa-em-reformulacao", [p["slug"] for p in api.get("/api/programs/").data])
        self.assertEqual(api.get("/api/programs/programa-em-reformulacao/").status_code, 404)
        self.assertNotIn("Projeto piloto descontinuado", [p["title"] for p in api.get("/api/projects/").data])
        self.assertNotIn("Rascunho ainda não publicado", [a["title"] for a in api.get("/api/articles/").data])
        self.assertNotIn("Antiga Parceira Ltda", [p["name"] for p in api.get("/api/partners/").data])
        self.assertEqual(len(api.get("/api/program-cases/").data), 5)  # um case está oculto

        processo = api.get("/api/selection-process/").data
        self.assertEqual(processo["title"], "Processo Seletivo ICC 2026.2")
        self.assertTrue(processo["registrations_open"])

        menu = [i["label"] for i in api.get("/api/site-config/").data["nav_items"]]
        self.assertIn("Código no GitHub", menu)
        self.assertNotIn("Eventos (em breve)", menu)

    def test_the_ex_member_profile_is_still_reachable(self):
        carolina = Member.objects.get(name="Carolina Mendonça")

        resposta = APIClient().get(f"/api/members/{carolina.pk}/")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual([e["semestre"] for e in resposta.data["trajetoria"]], ["2022.2", "2023.1", "2024.1", "2024.2"])

    # --- conteúdo fictício

    def test_everything_points_to_example_com_and_nothing_is_marked_as_a_sample(self):
        from website.models import Partner, ProgramCase

        for membro in Member.objects.all():
            for valor in (membro.email, membro.linkedin):
                if valor:
                    self.assertIn("example.com", valor, membro.name)
        enderecos = (
            [p.site for p in Partner.objects.all()] + [p.signup_url for p in Program.objects.all()]
            + [a.link for a in Article.objects.all()] + [c.publication_url for c in ProgramCase.objects.all()]
            + [s.registration_url for s in SelectionProcess.objects.all()]
        )
        for endereco in filter(None, enderecos):
            self.assertTrue(endereco.startswith("https://example.com"), endereco)
        titulos = [a.title for a in Article.objects.all()] + [p.title for p in Project.objects.all()]
        self.assertFalse([t for t in titulos if "[Exemplo]" in t])

    def test_the_example_data_respects_the_models_rules(self):
        from website.models import MemberTrajectory, ProgramComponent

        for modelo in (Member, Article, Project, Program, SelectionProcess, NavItem, MemberTrajectory, ProgramComponent):
            for objeto in modelo.objects.all():
                objeto.full_clean()
        self.assertLessEqual(max(len(m.biography) for m in Member.objects.all()), 200)

    # --- imagens

    def test_sample_images_are_valid_small_and_cover_the_numbered_ones_in_articles(self):
        import re
        from PIL import Image

        arquivos = self.arquivos_de_midia()
        self.assertGreater(len(arquivos), 30)
        for caminho in arquivos:
            self.assertLess(Path(caminho).stat().st_size, 1024 * 1024, caminho)
            with Image.open(caminho) as imagem:
                imagem.verify()

        for artigo in Article.objects.all():
            for numero in re.findall(r"!\[\]\(imagem-(\d+)\)", artigo.content):
                self.assertTrue(artigo.images.filter(number=int(numero)).exists(), f"{artigo.title}: imagem-{numero}")

    def test_placeholder_text_has_no_accented_glyphs_the_font_cannot_draw(self):
        import io
        from PIL import Image
        from website.management.commands.seed_mock_data import placeholder

        com_acento = placeholder("Capacitação semanal em sala", (600, 400), (30, 64, 110))
        sem_acento = placeholder("Capacitacao semanal em sala", (600, 400), (30, 64, 110))

        # Com o acento removido antes de desenhar, as duas imagens ficam idênticas (nenhum quadrado "tofu").
        self.assertEqual(Image.open(io.BytesIO(com_acento.read())).tobytes(), Image.open(io.BytesIO(sem_acento.read())).tobytes())

    def test_some_entities_are_deliberately_without_an_image(self):
        self.assertFalse(Member.objects.get(name="Davi Lacerda").photo)
        self.assertTrue(Member.objects.get(name="Helena Prado").photo)
        self.assertFalse(Article.objects.get(title="Transformação digital em PMEs: barreiras e alavancas").image)
        self.assertTrue(Article.objects.get(slug="precificacao-dinamica-no-varejo").image)

    # --- admin com os dados de exemplo

    def test_every_admin_page_opens_with_the_example_data(self):
        from django.contrib import admin

        usuario = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste-123")
        self.client.force_login(usuario)

        for modelo in admin.site._registry:
            if modelo._meta.app_label != "website":
                continue
            base = f"/admin/website/{modelo._meta.model_name}/"
            self.assertIn(self.client.get(base, follow=True).status_code, (200,), base)
            objeto = modelo.objects.first()
            if objeto is not None:
                self.assertEqual(self.client.get(f"{base}{objeto.pk}/change/").status_code, 200, base)


@SEM_MANIFESTO
class SeedCommandSafetyTests(TestCase):
    """As travas do seed_mock_data: só roda com DEBUG, sem Cloudinary pula as imagens e o setup_dev só semeia um banco vazio."""

    def setUp(self):
        import tempfile

        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        for contexto in (override_settings(MEDIA_ROOT=pasta.name, DEBUG=True), mock.patch.dict("os.environ")):
            contexto.__enter__()
            self.addCleanup(contexto.__exit__, None, None, None)
        __import__("os").environ.pop("DATABASE_URL", None)

    def semear(self, **opcoes):
        from django.core.management import call_command

        call_command("seed_mock_data", stdout=mock.Mock(), **opcoes)

    def test_it_refuses_to_run_without_debug(self):
        from django.core.management.base import CommandError

        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError):
                self.semear()

    def test_with_remote_storage_it_skips_the_images_and_still_works(self):
        from website.models import ArticleImage, ProjectImage

        with mock.patch("website.management.commands.seed_mock_data.default_storage", mock.Mock()):
            self.semear()

        self.assertEqual(Member.objects.count(), 16)
        self.assertFalse(Member.objects.exclude(photo="").exists())
        self.assertEqual(ArticleImage.objects.count(), 0)
        self.assertEqual(ProjectImage.objects.count(), 0)
        self.assertEqual(list(Path(settings.MEDIA_ROOT).rglob("*.png")), [])

    def test_setup_dev_seeds_only_when_there_are_no_members(self):
        from django.core.management import call_command

        call_command("setup_dev", stdout=mock.Mock())
        self.assertTrue(get_user_model().objects.filter(username="admin").exists())
        self.assertEqual(Member.objects.count(), 16)

        Member.objects.filter(name="Beatriz Salgado").delete()  # não participa de nenhum case
        call_command("setup_dev", stdout=mock.Mock())
        self.assertEqual(Member.objects.count(), 15)  # já havia membros: não semeia de novo


@SEM_MANIFESTO
class PermissionLevelsTests(TestCase):
    """Dois níveis: administrador (superusuário) e editor (grupo Editores). A estrutura do site é só do administrador."""

    def setUp(self):
        from django.contrib.auth.models import Group

        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste-123")
        self.editor = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste-123", is_staff=True)
        self.editor.groups.add(Group.objects.get(name="Editores"))
        self.url = "/admin/website/siteconfig/1/change/"

    def pagina(self, usuario):
        self.client.force_login(usuario)
        return self.client.get(self.url).content.decode()

    def test_the_administrator_sees_every_tab_and_the_menu_and_benefits_lists(self):
        pagina = self.pagina(self.admin)

        for campo in ("site_name", "logo", "privacy_text", "email", "home_hero_title"):
            self.assertIn(f'name="{campo}"', pagina, campo)
        self.assertIn("nav_items-TOTAL_FORMS", pagina)
        self.assertIn("partner_benefits-TOTAL_FORMS", pagina)

    def test_the_editor_does_not_see_brand_privacy_menu_or_benefits(self):
        pagina = self.pagina(self.editor)

        for campo in ("site_name", "site_description", "logo", "favicon", "og_image", "privacy_text", "privacy_updated"):
            self.assertNotIn(f'name="{campo}"', pagina, campo)
        self.assertNotIn("nav_items-TOTAL_FORMS", pagina)
        self.assertNotIn("partner_benefits-TOTAL_FORMS", pagina)
        # O que é conteúdo continua editável.
        for campo in ("email", "home_hero_title", "mission", "team_lead"):
            self.assertIn(f'name="{campo}"', pagina, campo)

    def test_an_editor_cannot_change_the_brand_even_by_sending_the_fields(self):
        from django.forms.models import model_to_dict

        config = SiteConfig.get_solo()
        dados = {k: v for k, v in model_to_dict(config).items()
                 if v is not None and k not in ("logo", "favicon", "og_image", "home_about_photo")}
        dados.update({"featured_program_slug": "", "email": "novo@example.com",
                      "site_name": "Nome trocado", "privacy_text": "Texto trocado"})
        self.client.force_login(self.editor)

        resposta = self.client.post(self.url, dados)

        self.assertEqual(resposta.status_code, 302)
        config.refresh_from_db()
        self.assertEqual(config.email, "novo@example.com")  # o que ele pode mudar, mudou
        self.assertEqual(config.site_name, "Liga Insper Consulting Club")
        self.assertNotEqual(config.privacy_text, "Texto trocado")

    def test_the_administrator_can_change_the_brand(self):
        from django.forms.models import model_to_dict

        config = SiteConfig.get_solo()
        dados = {k: v for k, v in model_to_dict(config).items()
                 if v is not None and k not in ("logo", "favicon", "og_image", "home_about_photo")}
        dados.update({"featured_program_slug": "", "site_name": "Nome novo"})
        # As listas da página (menu e benefícios) trazem o próprio formulário de controle.
        dados.update({"nav_items-TOTAL_FORMS": "0", "nav_items-INITIAL_FORMS": "0",
                      "nav_items-MIN_NUM_FORMS": "0", "nav_items-MAX_NUM_FORMS": "1000",
                      "partner_benefits-TOTAL_FORMS": "0", "partner_benefits-INITIAL_FORMS": "0",
                      "partner_benefits-MIN_NUM_FORMS": "0", "partner_benefits-MAX_NUM_FORMS": "1000"})
        self.client.force_login(self.admin)

        resposta = self.client.post(self.url, dados)

        self.assertEqual(resposta.status_code, 302)
        config.refresh_from_db()
        self.assertEqual(config.site_name, "Nome novo")

    def test_changing_the_brand_reminds_the_administrator_to_publish_the_frontend(self):
        from django.contrib import admin

        modelo_admin = admin.site._registry[SiteConfig]
        requisicao = mock.Mock(user=self.admin)

        with mock.patch.object(modelo_admin, "message_user") as aviso:
            modelo_admin.save_model(requisicao, SiteConfig.get_solo(), mock.Mock(changed_data=["site_name"]), True)
            textos = " ".join(str(chamada.args[1]) for chamada in aviso.call_args_list)
        self.assertIn("Manual Deploy", textos)

        with mock.patch.object(modelo_admin, "message_user") as aviso:
            modelo_admin.save_model(requisicao, SiteConfig.get_solo(), mock.Mock(changed_data=["email"]), True)
            textos = " ".join(str(chamada.args[1]) for chamada in aviso.call_args_list)
        self.assertNotIn("Manual Deploy", textos)


@SEM_MANIFESTO
class AdminListThumbnailTests(TestCase):
    """As listas de projetos, programas e artigos mostram a imagem, sem uma consulta por linha."""

    def setUp(self):
        from website.models import ProjectImage

        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste-123")
        self.client.force_login(self.admin)
        self.projeto = Project.objects.create(title="Com imagem", description="d", start_date=date(2025, 1, 1))
        ProjectImage.objects.create(project=self.projeto, image="projects/images/segunda.png", order=2)
        ProjectImage.objects.create(project=self.projeto, image="projects/images/primeira.png", order=1)
        Project.objects.create(title="Sem imagem", description="d", start_date=date(2025, 1, 1))
        Article.objects.create(title="Com capa", description="r", slug="com-capa", image="articles/capa.png")
        Article.objects.create(title="Sem capa", description="r", slug="sem-capa")

    def test_project_list_shows_the_first_image_by_order(self):
        pagina = self.client.get("/admin/website/project/").content.decode()

        self.assertIn("primeira.png", pagina)
        self.assertNotIn("segunda.png", pagina)

    def test_article_list_shows_the_cover(self):
        pagina = self.client.get("/admin/website/article/").content.decode()

        self.assertIn("articles/capa.png", pagina)

    def test_program_list_renders(self):
        Program.objects.create(label="Programa", slug="programa", description="d", icon="categories/icone.png")

        pagina = self.client.get("/admin/website/program/").content.decode()

        self.assertIn("categories/icone.png", pagina)

    def test_project_list_does_not_query_images_row_by_row(self):
        for i in range(8):
            Project.objects.create(title=f"Extra {i}", description="d", start_date=date(2025, 1, 1))

        with CaptureQueriesContext(connection) as consultas:
            self.client.get("/admin/website/project/")

        consultas_de_imagens = [q for q in consultas if "website_projectimage" in q["sql"]]
        self.assertEqual(len(consultas_de_imagens), 1)

