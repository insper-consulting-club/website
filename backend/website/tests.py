from datetime import date

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import connection
from pathlib import Path
from unittest import mock

import requests
from django.test import override_settings
from django.utils import translation
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from website.models import (
    Article, Member, Partner, PartnerCategory, Program, ProgramCase,
    NavItem, ProgramComponent, ProgramContentBlock, Project, SelectionProcess, SiteConfig, SiteText,
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


class FrontendDeployTests(TestCase):
    def test_changing_a_field_that_goes_into_the_html_asks_for_a_deploy(self):
        config = SiteConfig.get_solo()
        config.site_name = "Outro nome"

        with mock.patch("website.models.dispara_deploy_do_frontend") as dispara:
            with self.captureOnCommitCallbacks(execute=True):
                config.save()

        dispara.assert_called_once_with()

    def test_changing_any_other_field_does_not_ask_for_a_deploy(self):
        config = SiteConfig.get_solo()
        config.email = "novo@example.com"

        with mock.patch("website.models.dispara_deploy_do_frontend") as dispara:
            with self.captureOnCommitCallbacks(execute=True):
                config.save()

        dispara.assert_not_called()

    def test_saving_without_changes_does_not_ask_for_a_deploy(self):
        config = SiteConfig.get_solo()

        with mock.patch("website.models.dispara_deploy_do_frontend") as dispara:
            with self.captureOnCommitCallbacks(execute=True):
                config.save()

        dispara.assert_not_called()

    def test_creating_the_first_record_does_not_ask_for_a_deploy(self):
        SiteConfig.objects.all().delete()

        with mock.patch("website.models.dispara_deploy_do_frontend") as dispara:
            with self.captureOnCommitCallbacks(execute=True):
                SiteConfig.get_solo()

        dispara.assert_not_called()

    @override_settings(RENDER_FRONTEND_DEPLOY_HOOK="")
    def test_without_the_hook_nothing_is_called(self):
        from website.deploy_hook import dispara_deploy_do_frontend

        with mock.patch("website.deploy_hook.requests.post") as post:
            self.assertFalse(dispara_deploy_do_frontend(sincrono=True))

        post.assert_not_called()

    @override_settings(RENDER_FRONTEND_DEPLOY_HOOK="https://api.render.com/deploy/srv-x?key=segredo")
    def test_with_the_hook_it_posts_to_the_address(self):
        from website.deploy_hook import dispara_deploy_do_frontend

        with mock.patch("website.deploy_hook.requests.post") as post:
            post.return_value.status_code = 200
            self.assertTrue(dispara_deploy_do_frontend(sincrono=True))

        post.assert_called_once_with("https://api.render.com/deploy/srv-x?key=segredo", timeout=10)

    @override_settings(RENDER_FRONTEND_DEPLOY_HOOK="https://api.render.com/deploy/srv-x?key=segredo")
    def test_a_failure_is_logged_without_the_secret_and_never_raised(self):
        from website.deploy_hook import dispara_deploy_do_frontend

        erro = requests.ConnectionError("falha em https://api.render.com/deploy/srv-x?key=segredo")
        with mock.patch("website.deploy_hook.requests.post", side_effect=erro):
            with self.assertLogs("website.deploy_hook", level="WARNING") as log:
                dispara_deploy_do_frontend(sincrono=True)

        texto = "\n".join(log.output)
        self.assertIn("ConnectionError", texto)
        self.assertNotIn("segredo", texto)


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
