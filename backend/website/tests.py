from datetime import date

from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from pathlib import Path
from unittest import mock

from django.test import override_settings
from django.utils import timezone, translation
from django.test import TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from website.models import (
    Article, ArticleAuthor, ArticleImage, Member, Partner, PartnerCategory, Program, ProgramCase,
    Directorate, NavItem, PaginaDoSite, ProgramComponent, ProgramContentBlock, Project, SecaoDaHome, SelectionProcess,
    SiteConfig, SiteText,
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
        self.current = Member.objects.create(name="Ana")
        self.former = Member.objects.create(name="Bruno", is_active=False)

    def test_list_hides_archived_members(self):
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

    def test_partner_lists_only_active_finished_projects_and_sends_no_counts(self):
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

        self.assertEqual([p["title"] for p in response.data["projects"]], ["Concluído"])
        self.assertNotIn("projects_count", response.data)
        self.assertNotIn("completed_projects_count", response.data)

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
        self.assertEqual(len(by_name["P7"]["projects"]), 1)
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
        self.assertEqual(response.data["texts"]["home.hero_titulo"], "O futuro consultor começa no ICC")
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


@SEM_MANIFESTO
class NavItemTests(TestCase):
    def test_migrations_create_exactly_the_default_menu_and_benefits(self):
        from website.conteudo_padrao import BENEFICIOS_PADRAO, NAV_ITEMS_PADRAO
        from website.models import PartnerBenefit

        itens = list(NavItem.objects.values_list("label", "area", "page", "order"))
        beneficios = list(PartnerBenefit.objects.values_list("title", "description", "order"))

        # conteudo_padrao.py tem de ser o que um banco novo recebe.
        self.assertEqual(itens, NAV_ITEMS_PADRAO)
        self.assertEqual(beneficios, BENEFICIOS_PADRAO)

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
        # O que se edita toda semana vem primeiro; a configuração do site e o acesso ficam no fim.
        from config.navigation import navegacao

        usuario = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        requisicao = mock.Mock(user=usuario)

        grupos = navegacao(requisicao)

        self.assertEqual(
            [g["title"] for g in grupos],
            ["Artigos", "Equipe", "Parceiros", "Programas e projetos", "Processo seletivo", "Site", "Acesso"],
        )
        itens = [i["title"] for g in grupos for i in g["items"]]
        self.assertEqual(len(itens), 18)  # 15 modelos do site, mais Usuários, Grupos e Atividade recente
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
        membro = Member.objects.create(name="M")

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
        # O cronograma do projeto é ordenado por data (os participantes do case, por papel e nome, não têm campo de ordem).
        fora = {"ProjectTimelineEventInline"}
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

        for esperado in ("change_article", "add_article", "view_member", "change_siteconfig", "change_paginadosite", "change_secaodahome",
                         "delete_projectimage", "view_position", "add_position"):
            self.assertIn(esperado, codenames)
        for proibido in ("delete_article", "delete_member", "delete_project", "add_siteconfig", "delete_siteconfig",
                         "add_paginadosite", "delete_paginadosite", "add_secaodahome", "delete_secaodahome", "change_position", "delete_position", "view_user", "change_user", "view_group",
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
        self.grupo.permissions.remove(Permission.objects.get(codename="change_paginadosite"))

        self.assertFalse(sincroniza_grupo_editores(apps, apps.get_app_config("website")))

        self.assertIn("delete_article", self.codenames())
        self.assertNotIn("change_paginadosite", self.codenames())

    def test_an_old_group_gets_the_permission_of_the_new_texts_screen(self):
        from django.apps import apps
        from django.contrib.auth.models import Permission
        from website.editors_group import sincroniza_grupo_editores

        # Um grupo de antes da tela nova: podia alterar textos pela lista antiga e não tem a permissão da página.
        self.grupo.permissions.remove(*Permission.objects.filter(codename__in=["change_paginadosite", "view_paginadosite"]))
        self.grupo.permissions.add(Permission.objects.get(codename="change_sitetext"))

        self.assertFalse(sincroniza_grupo_editores(apps, apps.get_app_config("website")))

        self.assertIn("change_paginadosite", self.codenames())
        self.assertIn("view_paginadosite", self.codenames())

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
                 if v is not None and k not in ("logo", "favicon", "og_image", "home_about_photo", "home_hidden_sections")}
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
        membro = Member.objects.create(name="Ana")
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
        self.membro = Member.objects.create(name="Ana")

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
        a = Article.objects.create(title="A", description="d", published=False, date=date(2026, 1, 1), institutional=True)
        b = Article.objects.create(title="B", description="d", published=False, institutional=True)

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
            data={"name": "Ana", "projects": []},
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
        from website.models import PaginaDoSite, SiteText

        leitor = get_user_model().objects.create_user("leitor", "l@example.com", "senha-de-teste", is_staff=True)
        leitor.user_permissions.add(*Permission.objects.filter(codename__in=["view_member", "view_project", "view_paginadosite"]))
        self.client.force_login(leitor)
        membro = Member.objects.create(name="Ana")
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        texto = SiteText.objects.get(key="equipe.titulo")
        SiteText.objects.filter(pk=texto.pk).update(value="Editado")
        pagina = PaginaDoSite.objects.get(slug="equipe")

        self.client.post("/admin/website/member/", {"action": "arquivar", "_selected_action": [membro.pk]})
        self.client.post("/admin/website/project/", {"action": "arquivar", "_selected_action": [projeto.pk]})
        self.client.post("/admin/website/paginadosite/", {"action": "restaurar_originais", "_selected_action": [pagina.pk]})

        membro.refresh_from_db(); projeto.refresh_from_db(); texto.refresh_from_db()
        self.assertTrue(membro.is_active)
        self.assertTrue(projeto.is_active)
        self.assertEqual(texto.value, "Editado")

    def test_the_editors_group_can_still_use_the_actions(self):
        from django.contrib.auth.models import Group

        editora = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste", is_staff=True)
        editora.groups.add(Group.objects.get(name="Editores"))
        self.client.force_login(editora)
        membro = Member.objects.create(name="Ana")

        self.client.post("/admin/website/member/", {"action": "arquivar", "_selected_action": [membro.pk]})

        membro.refresh_from_db()
        self.assertFalse(membro.is_active)


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
        from website.conteudo import PADRAO

        self.assertEqual(SiteText.objects.get(key="home.hero_titulo").value, PADRAO["home.hero_titulo"])
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
        Member.objects.filter(pk=helena.pk).update(linkedin="https://exemplo.com/outro")
        MemberTrajectory.objects.create(member=helena, semester="2030.1", role="Cargo que o seed não conhece")

        call_command("seed_mock_data", stdout=mock.Mock())

        helena.refresh_from_db()
        self.assertEqual(helena.linkedin, "https://example.com/linkedin/helena-prado")
        self.assertFalse(helena.trajectory_steps.filter(semester="2030.1").exists())

    # --- casos de borda

    def test_edge_cases_are_present(self):
        from website.models import DirectorateMembership, Partner, ProgramCase

        sem_logo_nem_site = Partner.objects.get(name="Horizonte Educação")
        self.assertFalse(sem_logo_nem_site.logo_url)
        self.assertIsNone(sem_logo_nem_site.site)
        self.assertFalse(Partner.objects.get(name="Antiga Parceira Ltda").is_active)
        self.assertFalse(Program.objects.get(slug="programa-em-reformulacao").is_active)
        self.assertFalse(ProgramCase.objects.filter(is_active=False).get().is_active)

        mateus = Member.objects.get(name="Mateus Ribeiro")
        self.assertIsNone(mateus.linkedin)
        self.assertFalse(mateus.trajectory_steps.exists())
        self.assertEqual(Member.objects.filter(is_active=False).count(), 2)
        self.assertGreater(max(len(m.name) for m in Member.objects.all()), 50)
        duas = Member.objects.get(name="Isabela Fontes")
        self.assertEqual(DirectorateMembership.objects.filter(member=duas).count(), 2)

        self.assertFalse(Article.objects.get(title="Rascunho ainda não publicado").published)
        self.assertIsNone(Article.objects.get(title="Transformação digital em PMEs: barreiras e alavancas").slug)
        self.assertTrue(Article.objects.get(slug="entrevista-com-uma-mentora").institutional)
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
            if membro.linkedin:
                self.assertIn("example.com", membro.linkedin, membro.name)
        enderecos = (
            [p.site for p in Partner.objects.all()] + [p.signup_url for p in Program.objects.all()]
            + [c.publication_url for c in ProgramCase.objects.all()]
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

        for campo in ("site_name", "logo", "privacy_text", "email", "home_about_photo_alt"):
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
        for campo in ("email", "home_about_photo_alt", "featured_program_slug"):
            self.assertIn(f'name="{campo}"', pagina, campo)

    def test_an_editor_cannot_change_the_brand_even_by_sending_the_fields(self):
        from django.forms.models import model_to_dict

        config = SiteConfig.get_solo()
        dados = {k: v for k, v in model_to_dict(config).items()
                 if v is not None and k not in ("logo", "favicon", "og_image", "home_about_photo", "home_hidden_sections")}
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
                 if v is not None and k not in ("logo", "favicon", "og_image", "home_about_photo", "home_hidden_sections")}
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



class AdminJavaScriptTranslationTests(TestCase):
    """O seletor de duas listas (permissões de um grupo) usa frases que não dependem do gênero."""

    def test_two_list_selector_phrases_do_not_depend_on_gender(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste-123"))
        texto = self.client.get("/admin/jsi18n/").content.decode()

        self.assertIn("Escolher tudo em %s", texto)
        self.assertIn("Remover tudo de %s", texto)
        self.assertNotIn("Escolher todos %s", texto)
        self.assertNotIn("Remover todos %s", texto)


@SEM_MANIFESTO
class AdminPortugueseTextsTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste-123"))

    def test_permissions_are_listed_in_portuguese(self):
        for url in ("/admin/auth/group/add/", "/admin/auth/user/1/change/"):
            pagina = self.client.get(url).content.decode()

            self.assertNotIn("Can add", pagina, url)
            self.assertNotIn("Can view", pagina, url)
            self.assertIn("Conteúdo do site | Artigo | Pode adicionar", pagina, url)
            self.assertIn("Conteúdo do site | Artigo | Pode alterar", pagina, url)
            self.assertIn("Conteúdo do site | Artigo | Pode excluir", pagina, url)
            self.assertIn("Conteúdo do site | Artigo | Pode ver", pagina, url)

    def test_permission_labels_are_unique_and_tell_apart_similar_models(self):
        import re

        pagina = self.client.get("/admin/auth/group/add/").content.decode()
        rotulos = [r for r in re.findall(r"<option[^>]*>([^<]+)</option>", pagina) if " | " in r]

        self.assertGreater(len(rotulos), 50)
        self.assertEqual(len(rotulos), len(set(rotulos)), "há permissões com o mesmo nome na lista")
        self.assertIn("Conteúdo do site | Bloco de conteúdo do projeto | Pode alterar", rotulos)
        self.assertIn("Conteúdo do site | Bloco de conteúdo do programa | Pode alterar", rotulos)
        self.assertIn("Conteúdo do site | Item do material | Pode alterar", rotulos)

    def test_project_program_field_explains_what_empty_means(self):
        pagina = self.client.get("/admin/website/project/add/").content.decode()

        self.assertIn("Deixe vazio para ele aparecer em", pagina)

    def test_user_form_uses_corrected_django_sentences(self):
        pagina = self.client.get("/admin/auth/user/1/change/").content.decode()

        self.assertIn("Indica que o usuário consegue acessar este site de administração.", pagina)
        self.assertIn("Os grupos a que este usuário pertence.", pagina)

    def test_fields_have_portuguese_names(self):
        from django.apps import apps

        sem_nome = []
        for modelo in apps.get_app_config("website").get_models():
            for campo in modelo._meta.get_fields():
                if not campo.concrete or campo.auto_created or campo.primary_key:
                    continue
                # Sem verbose_name, o Django usa o nome do campo em inglês (ex.: "title").
                if str(campo.verbose_name) == campo.name.replace("_", " "):
                    sem_nome.append(f"{modelo.__name__}.{campo.name}")
        self.assertEqual(sem_nome, [])


class ErrorPagesTests(TestCase):
    """Em produção (DEBUG desligado), as páginas de erro do Django saem em português."""

    def test_not_found_page_is_in_portuguese(self):
        resposta = self.client.get("/endereco-que-nao-existe/")

        self.assertEqual(resposta.status_code, 404)
        self.assertContains(resposta, "Página não encontrada", status_code=404)
        self.assertNotContains(resposta, "The requested resource", status_code=404)

    @SEM_MANIFESTO
    def test_forbidden_page_is_in_portuguese(self):
        editor = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste-123", is_staff=True)
        self.client.force_login(editor)

        resposta = self.client.get("/admin/auth/user/")

        self.assertContains(resposta, "Sem permissão", status_code=403)

    def test_server_error_and_bad_request_pages_are_in_portuguese(self):
        from django.test import RequestFactory
        from django.views.defaults import bad_request, server_error

        requisicao = RequestFactory().get("/")

        self.assertIn("Erro no servidor", server_error(requisicao).content.decode())
        self.assertIn("Requisição inválida", bad_request(requisicao, Exception()).content.decode())


@SEM_MANIFESTO
class DjangoMessagesInPortugueseTests(TestCase):
    """Correções de gramática e de termos em inglês nas mensagens padrão do Django."""

    def setUp(self):
        from django.utils import translation

        translation.activate("pt-br")
        self.addCleanup(translation.deactivate)

    def test_invalid_login_message(self):
        import re

        resposta = self.client.post("/admin/login/", {"username": "x", "password": "y"})

        texto = " ".join(re.sub(r"<[^>]+>", " ", resposta.content.decode()).split())
        self.assertIn("Confira o usuário e a senha", texto)
        self.assertNotIn("entre com", texto)

    def test_validators_use_the_right_preposition(self):
        from django import forms
        from django.core.exceptions import ValidationError
        from django.core.validators import MaxValueValidator, MinValueValidator

        with self.assertRaises(ValidationError) as minimo:
            MinValueValidator(5)(1)
        with self.assertRaises(ValidationError) as maximo:
            MaxValueValidator(5)(9)
        with self.assertRaises(ValidationError) as email:
            forms.EmailField().clean("sem-arroba")

        self.assertEqual(minimo.exception.messages, ["Certifique-se de que este valor seja maior ou igual a 5."])
        self.assertEqual(maximo.exception.messages, ["Certifique-se de que este valor seja menor ou igual a 5."])
        self.assertEqual(email.exception.messages, ["Informe um endereço de e-mail válido."])

    def test_form_error_banner_and_formset_messages_are_singular_and_plural(self):
        from django.utils.translation import ngettext

        erro, erros = "Please correct the error below.", "Please correct the errors below."
        self.assertEqual(ngettext(erro, erros, 1), "Corrija o erro abaixo.")
        self.assertEqual(ngettext(erro, erros, 2), "Corrija os erros abaixo.")
        maximo, maximos = "Please submit at most %(num)d form.", "Please submit at most %(num)d forms."
        self.assertEqual(ngettext(maximo, maximos, 1) % {"num": 1}, "Envie no máximo 1 formulário.")
        self.assertEqual(ngettext(maximo, maximos, 3) % {"num": 3}, "Envie no máximo 3 formulários.")

    def test_action_warning_in_javascript_catalog(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste-123"))

        texto = self.client.get("/admin/jsi18n/").content.decode()

        self.assertIn("de novo.", texto)
        self.assertNotIn("de rodar", texto)


@SEM_MANIFESTO
class AdminAdvancedSectionTests(TestCase):
    """Os campos que quase nunca mudam ficam numa seção recolhida, depois dos de uso diário."""

    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste-123"))

    def posicoes(self, url, visiveis, avancados):
        pagina = self.client.get(url).content.decode()
        marco = pagina.index("Avançado")
        for campo in visiveis:
            self.assertLess(pagina.index(f'name="{campo}"'), marco, f"{campo} deveria estar antes de Avançado")
        for campo in avancados:
            self.assertGreater(pagina.index(f'name="{campo}"'), marco, f"{campo} deveria estar em Avançado")
        return pagina

    def test_article_form_keeps_only_daily_fields_visible(self):
        self.posicoes(
            "/admin/website/article/add/",
            visiveis=["title", "slug", "institutional", "topics", "description", "content", "published", "date", "image"],
            avancados=["order"],
        )

    def test_partner_program_and_case_forms(self):
        self.posicoes("/admin/website/partner/add/", ["name", "logo_url", "category", "is_active"], ["order"])
        self.posicoes("/admin/website/program/add/", ["label", "slug", "signup_url", "is_active"], ["order"])
        self.posicoes("/admin/website/programcase/add/", ["program", "semester", "title", "is_active"], ["order"])

    def test_advanced_section_opens_by_itself_when_a_field_has_an_error(self):
        sem_erro = self.client.get("/admin/website/article/add/").content.decode()

        com_erro = self.client.post(
            "/admin/website/article/add/",
            {"title": "T", "description": "d", "order": "abc"},
        ).content.decode()

        self.assertIn("número inteiro", com_erro)
        self.assertLess(com_erro.count("<details"), sem_erro.count("<details"))


@SEM_MANIFESTO
class MemberArchiveTests(TestCase):
    """O membro que sai é arquivado com a caixa "Exibir na equipe", como parceiros, programas e cases."""

    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste"))

    def test_member_is_shown_by_default_and_archived_members_keep_their_data(self):
        membro = Member.objects.create(name="Ana")
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        membro.projects.add(projeto)
        membro.trajectory_steps.create(semester="2025.1", role="Membro")

        self.assertTrue(membro.is_active)
        Member.objects.filter(pk=membro.pk).update(is_active=False)

        membro.refresh_from_db()
        self.assertEqual(list(membro.projects.all()), [projeto])
        self.assertEqual(membro.trajectory_steps.count(), 1)

    def test_archive_and_reactivate_actions(self):
        membro = Member.objects.create(name="Ana")

        self.client.post("/admin/website/member/", {"action": "arquivar", "_selected_action": [membro.pk]})
        membro.refresh_from_db()
        self.assertFalse(membro.is_active)

        self.client.post("/admin/website/member/", {"action": "reativar", "_selected_action": [membro.pk]})
        membro.refresh_from_db()
        self.assertTrue(membro.is_active)

    def test_status_filter_separates_current_members_from_alumni(self):
        Member.objects.create(name="Ana")
        Member.objects.create(name="Bruno", is_active=False)

        atuais = self.client.get("/admin/website/member/?situacao=atual").content.decode()
        ex = self.client.get("/admin/website/member/?situacao=ex").content.decode()

        self.assertIn("Ana", atuais)
        self.assertNotIn("Bruno", atuais)
        self.assertIn("Bruno", ex)
        self.assertNotIn("Ana", ex)

    def test_archived_member_still_appears_in_the_project_team_api(self):
        ex = Member.objects.create(name="Bruno", is_active=False)
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        ex.projects.add(projeto)

        resposta = self.client.get(f"/api/projects/{projeto.pk}/")

        self.assertEqual([m["name"] for m in resposta.data["members"]], ["Bruno"])


class MemberActiveMigrationTests(TransactionTestCase):
    """Migration 0026: quem tinha data de saída fica desmarcado em "Exibir na equipe"."""

    ANTES = ("website", "0025_remove_campos_sem_uso_e_padroniza_nomes")
    DEPOIS = ("website", "0026_membro_ativo")

    def _estado(self, alvo):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        MigrationExecutor(connection).migrate([alvo])
        return MigrationExecutor(connection).loader.project_state([alvo]).apps

    def tearDown(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_members_with_exit_date_become_archived_and_the_rest_stay_active(self):
        antigo = self._estado(self.ANTES)
        Member = antigo.get_model("website", "Member")
        Member.objects.create(name="Ana")
        Member.objects.create(name="Bruno", exit_date=date(2025, 7, 15))

        novo = self._estado(self.DEPOIS)
        Member = novo.get_model("website", "Member")

        self.assertTrue(Member.objects.get(name="Ana").is_active)
        self.assertFalse(Member.objects.get(name="Bruno").is_active)

    def test_migrating_back_gives_archived_members_a_date(self):
        novo = self._estado(self.DEPOIS)
        novo.get_model("website", "Member").objects.create(name="Bruno", is_active=False)
        novo.get_model("website", "Member").objects.create(name="Ana")

        antigo = self._estado(self.ANTES)
        Member = antigo.get_model("website", "Member")

        self.assertIsNotNone(Member.objects.get(name="Bruno").exit_date)
        self.assertIsNone(Member.objects.get(name="Ana").exit_date)


def png_pequeno(nome="x.png"):
    import io

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), (200, 30, 30)).save(buffer, format="PNG")
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/png")


@SEM_MANIFESTO
class AdminQuickWinsTests(TestCase):
    """Melhorias de uso do admin: consultas, numeração das imagens, equipe, componentes, ambiente."""

    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste")
        self.client.force_login(self.admin)

    # --- consultas repetidas

    def test_partner_list_does_not_query_the_category_row_by_row(self):
        categoria = PartnerCategory.objects.create(title="Tech")

        def criar(n):
            for i in range(n):
                Partner.objects.create(name=f"P{n}-{i}", description="d", logo_url="l.png", category=categoria)

        criar(2)
        with CaptureQueriesContext(connection) as poucas:
            self.client.get("/admin/website/partner/")
        criar(8)
        with CaptureQueriesContext(connection) as muitas:
            self.client.get("/admin/website/partner/")

        self.assertEqual(len(poucas), len(muitas))

    # --- numeração das imagens do artigo

    def test_image_without_number_gets_the_next_free_one_of_its_article(self):
        artigo = Article.objects.create(title="A", description="d", slug="a")
        outro = Article.objects.create(title="B", description="d", slug="b")

        primeira = ArticleImage.objects.create(article=artigo, image="articles/1.png")
        segunda = ArticleImage.objects.create(article=artigo, image="articles/2.png")
        do_outro = ArticleImage.objects.create(article=outro, image="articles/3.png")

        self.assertEqual((primeira.number, segunda.number, do_outro.number), (1, 2, 1))

    def test_admin_numbers_new_blank_rows_without_repeating_a_typed_number(self):
        import shutil
        import tempfile

        from django.forms.models import model_to_dict

        # Os arquivos enviados vão para uma pasta temporária, nunca para a pasta de mídia do projeto.
        pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, pasta, ignore_errors=True)
        configuracao = self.settings(MEDIA_ROOT=pasta)
        configuracao.enable()
        self.addCleanup(configuracao.disable)

        artigo = Article.objects.create(
            title="A", description="d", slug="a", published=True, date=date(2026, 1, 1), institutional=True,
        )
        dados = {k: v for k, v in model_to_dict(artigo).items() if v is not None and k != "image"}
        dados.update({
            "article_authors-TOTAL_FORMS": "0", "article_authors-INITIAL_FORMS": "0",
            "article_authors-MIN_NUM_FORMS": "0", "article_authors-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "3", "images-INITIAL_FORMS": "0", "images-MIN_NUM_FORMS": "0", "images-MAX_NUM_FORMS": "1000",
            "images-0-number": "", "images-0-image": png_pequeno("a.png"), "images-0-caption": "primeira",
            "images-1-number": "", "images-1-image": png_pequeno("b.png"), "images-1-caption": "segunda",
            "images-2-number": "2", "images-2-image": png_pequeno("c.png"), "images-2-caption": "digitada",
        })

        resposta = self.client.post(f"/admin/website/article/{artigo.pk}/change/", dados)

        self.assertEqual(resposta.status_code, 302)
        numeros = {i.caption: i.number for i in artigo.images.all()}
        self.assertEqual(numeros["digitada"], 2)
        self.assertEqual(sorted(numeros.values()), [2, 3, 4])

    def test_each_saved_image_shows_a_snippet_to_copy(self):
        artigo = Article.objects.create(title="A", description="d", slug="a")
        ArticleImage.objects.create(article=artigo, image="articles/1.png")

        pagina = self.client.get(f"/admin/website/article/{artigo.pk}/change/").content.decode()

        self.assertIn("![](imagem-1)", pagina)
        self.assertIn("copiar-trecho", pagina)
        self.assertIn("Aparece depois de salvar", pagina)

    # --- equipe do projeto

    def test_project_team_is_edited_in_the_project_and_not_in_the_member(self):
        projeto_pagina = self.client.get("/admin/website/project/add/").content.decode()
        membro_pagina = self.client.get("/admin/website/member/add/").content.decode()

        self.assertIn('name="members"', projeto_pagina)
        self.assertNotIn('name="projects"', membro_pagina)

    def test_saving_a_project_with_a_team_shows_it_in_the_api_and_in_the_member(self):
        ana = Member.objects.create(name="Ana")
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        from django.forms.models import model_to_dict

        dados = {k: v for k, v in model_to_dict(projeto).items() if v is not None}
        dados.update({
            "members": [ana.pk], "partners": [],
            "images-TOTAL_FORMS": "0", "images-INITIAL_FORMS": "0", "images-MIN_NUM_FORMS": "0", "images-MAX_NUM_FORMS": "1000",
            "timeline_events-TOTAL_FORMS": "0", "timeline_events-INITIAL_FORMS": "0",
            "timeline_events-MIN_NUM_FORMS": "0", "timeline_events-MAX_NUM_FORMS": "1000",
            "content_blocks-TOTAL_FORMS": "0", "content_blocks-INITIAL_FORMS": "0",
            "content_blocks-MIN_NUM_FORMS": "0", "content_blocks-MAX_NUM_FORMS": "1000",
        })

        resposta = self.client.post(f"/admin/website/project/{projeto.pk}/change/", dados)

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(list(ana.projects.all()), [projeto])
        api = APIClient().get(f"/api/projects/{projeto.pk}/")
        self.assertEqual([m["name"] for m in api.data["members"]], ["Ana"])

    # --- componentes do programa

    def test_components_are_a_tab_of_the_program_and_have_no_page_of_their_own(self):
        programa = Program.objects.create(label="G", slug="g", description="d")

        pagina = self.client.get(f"/admin/website/program/{programa.pk}/change/").content.decode()
        sozinha = self.client.get("/admin/website/programcomponent/")
        menu = self.client.get("/admin/").content.decode()

        self.assertIn("components-TOTAL_FORMS", pagina)
        self.assertEqual(sozinha.status_code, 404)
        self.assertNotIn("Componentes dos programas", menu)

    # --- programa em destaque

    def test_featured_program_is_chosen_from_a_list_of_programs(self):
        Program.objects.create(label="Jornada do Consultor", slug="jornada-do-consultor", description="d")
        Program.objects.create(label="Pedagógico", slug="pedagogico", description="d")

        pagina = self.client.get("/admin/website/siteconfig/1/change/").content.decode()

        self.assertIn('<select name="featured_program_slug"', pagina)
        self.assertIn('value="pedagogico"', pagina)
        self.assertIn("Pedagógico", pagina)

    def test_an_old_featured_slug_without_program_stays_visible(self):
        SiteConfig.objects.filter(pk=1).update(featured_program_slug="programa-que-sumiu")

        pagina = self.client.get("/admin/website/siteconfig/1/change/").content.decode()

        self.assertIn("programa-que-sumiu (programa não encontrado)", pagina)

    # --- código compartilhado

    def test_ordered_tabs_share_the_same_drag_behaviour(self):
        from django.contrib import admin
        from website import admin as site_admin

        for classe in (site_admin.ProjectImageInline, site_admin.ProgramContentBlockInline, site_admin.NavItemInline):
            self.assertEqual(classe.ordering_field, "order")
            self.assertTrue(classe.hide_ordering_field)
            self.assertTrue(classe.tab)



class TeamAndComponentsMigrationTests(TransactionTestCase):
    """Migration 0027: a equipe passa para o projeto, e componente sem programa deixa de existir."""

    ANTES = ("website", "0026_membro_ativo")
    DEPOIS = ("website", "0027_equipe_no_projeto_e_componentes_no_programa")

    def _estado(self, alvo):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        MigrationExecutor(connection).migrate([alvo])
        return MigrationExecutor(connection).loader.project_state([alvo]).apps

    def tearDown(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_teams_are_copied_to_the_project_side(self):
        antigo = self._estado(self.ANTES)
        Member, Project = antigo.get_model("website", "Member"), antigo.get_model("website", "Project")
        ana, bia = Member.objects.create(name="Ana"), Member.objects.create(name="Bia")
        p1 = Project.objects.create(title="P1", description="d", start_date=date(2025, 1, 1))
        p2 = Project.objects.create(title="P2", description="d", start_date=date(2025, 1, 1))
        ana.projects.add(p1, p2)
        bia.projects.add(p1)

        novo = self._estado(self.DEPOIS)
        Project = novo.get_model("website", "Project")

        self.assertEqual(sorted(m.name for m in Project.objects.get(title="P1").members.all()), ["Ana", "Bia"])
        self.assertEqual([m.name for m in Project.objects.get(title="P2").members.all()], ["Ana"])

    def test_teams_are_copied_back_when_the_migration_is_undone(self):
        novo = self._estado(self.DEPOIS)
        Member, Project = novo.get_model("website", "Member"), novo.get_model("website", "Project")
        ana = Member.objects.create(name="Ana")
        projeto = Project.objects.create(title="P", description="d", start_date=date(2025, 1, 1))
        projeto.members.add(ana)

        antigo = self._estado(self.ANTES)
        Member = antigo.get_model("website", "Member")

        self.assertEqual([p.title for p in Member.objects.get(name="Ana").projects.all()], ["P"])

    def test_components_without_a_program_are_removed_and_the_others_stay(self):
        antigo = self._estado(self.ANTES)
        Program = antigo.get_model("website", "Program")
        Componente = antigo.get_model("website", "ProgramComponent")
        programa = Program.objects.create(label="G", slug="g", description="d")
        Componente.objects.create(title="Com programa", description="d", program=programa)
        Componente.objects.create(title="Órfão", description="d", program=None)

        novo = self._estado(self.DEPOIS)
        Componente = novo.get_model("website", "ProgramComponent")

        self.assertEqual([c.title for c in Componente.objects.all()], ["Com programa"])


@SEM_MANIFESTO
class AdminSmallImprovementsTests(TestCase):
    """Ordem da lista de membros, cargo criado por editor, validações, atividade recente e participantes."""

    def setUp(self):
        from django.contrib.auth.models import Group

        self.admin = get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste")
        self.editor = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste", is_staff=True)
        self.editor.groups.add(Group.objects.get(name="Editores"))

    # --- 1: ordem da lista de membros

    def test_member_list_shows_the_team_first_and_in_alphabetical_order(self):
        Member.objects.create(name="Zélia")
        Member.objects.create(name="Bruno", is_active=False)
        Member.objects.create(name="Ana")
        self.client.force_login(self.admin)

        pagina = self.client.get("/admin/website/member/").content.decode()

        ordem = [pagina.index(nome) for nome in ("Ana", "Zélia", "Bruno")]
        self.assertEqual(ordem, sorted(ordem))

    # --- 2: cargo criado por um editor

    def test_editor_can_create_a_position_but_not_choose_its_priority(self):
        from website.models import Position

        self.client.force_login(self.editor)
        pagina = self.client.get("/admin/website/position/add/").content.decode()
        self.assertIn('name="title"', pagina)
        self.assertNotIn('name="power"', pagina)

        resposta = self.client.post("/admin/website/position/add/", {"title": "Analista de Dados", "power": "0"})

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Position.objects.get(title="Analista de Dados").power, 4)

    def test_editor_cannot_change_an_existing_position_and_administrator_chooses_priority(self):
        from website.models import Position

        cargo = Position.objects.create(title="Presidente", power=0)
        self.client.force_login(self.editor)

        self.assertEqual(self.client.post(f"/admin/website/position/{cargo.pk}/change/", {"title": "X"}).status_code, 403)

        self.client.force_login(self.admin)
        self.assertIn('name="power"', self.client.get("/admin/website/position/add/").content.decode())

    def test_migration_gives_the_existing_editors_group_the_new_permission(self):
        import importlib

        from django.apps import apps
        from django.contrib.auth.models import Group, Permission

        grupo = Group.objects.get(name="Editores")
        permissao = Permission.objects.get(codename="add_position", content_type__app_label="website")
        grupo.permissions.remove(permissao)

        importlib.import_module("website.migrations.0028_cargo_novo_e_semestre_do_case") \
            .permitir_criar_cargo_aos_editores(apps, None)

        self.assertIn(permissao, grupo.permissions.all())

    # --- 3: validações

    def test_case_semester_must_follow_the_pattern(self):
        from django.core.exceptions import ValidationError

        programa = Program.objects.create(label="G", slug="g", description="d")
        for invalido in ("2026", "2026.3", "26.1", "primeiro"):
            caso = ProgramCase(program=programa, semester=invalido, area="a", theme="t")
            with self.assertRaises(ValidationError, msg=invalido):
                caso.full_clean()
        ProgramCase(program=programa, semester="2026.1", area="a", theme="t").full_clean()

    def test_project_cannot_end_before_it_starts(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError) as erro:
            Project(title="P", description="d", start_date=date(2026, 5, 1), end_date=date(2026, 4, 30)).full_clean()

        self.assertIn("end_date", erro.exception.message_dict)
        Project(title="P", description="d", start_date=date(2026, 5, 1), end_date=date(2026, 5, 1)).full_clean()

    # --- 4: atividade recente

    def test_administrator_sees_who_changed_what_and_editor_does_not(self):
        self.client.force_login(self.editor)
        self.client.post("/admin/website/position/add/", {"title": "Analista de Dados"})

        self.assertEqual(self.client.get("/admin/admin/logentry/").status_code, 403)

        self.client.force_login(self.admin)
        pagina = self.client.get("/admin/admin/logentry/").content.decode()

        self.assertIn("Atividade recente", pagina)
        self.assertIn("Analista de Dados", pagina)
        self.assertIn("editora", pagina)

    def test_activity_page_is_read_only(self):
        self.client.force_login(self.admin)

        self.assertEqual(self.client.get("/admin/admin/logentry/add/").status_code, 403)

    # --- 5: participantes do case

    def test_case_participants_keep_their_saved_order_and_can_be_dragged(self):
        from website import admin as site_admin
        from website.models import ProgramCaseParticipant

        programa = Program.objects.create(label="G", slug="g", description="d")
        caso = ProgramCase.objects.create(program=programa, semester="2026.1", area="a", theme="t")
        for nome, papel, ordem in (("Zélia", "integrante", 1), ("Ana", "integrante", 2), ("Luiz", "mentor", 1)):
            ProgramCaseParticipant.objects.create(
                case=caso, member=Member.objects.create(name=nome), role=papel, order=ordem,
            )

        api = APIClient().get("/api/program-cases/").data

        # A ordem cadastrada é respeitada (Zélia antes de Ana), com os mentores depois dos integrantes.
        self.assertEqual([p["name"] for p in api[0]["participants"]], ["Zélia", "Ana", "Luiz"])
        self.assertEqual(site_admin.ProgramCaseParticipantInline.ordering_field, "order")
        self.assertTrue(site_admin.ProgramCaseParticipantInline.hide_ordering_field)


class ContentRegistryTests(TestCase):
    """O registro de conteúdo (website/conteudo/) é a fonte dos textos editáveis."""

    def test_keys_and_page_slugs_are_unique_and_pages_are_not_empty(self):
        from website.conteudo import PAGINAS

        chaves = [t.chave for p in PAGINAS for t in p.textos]
        self.assertEqual(len(chaves), len(set(chaves)))
        self.assertEqual(len(chaves), 149)
        self.assertEqual(len({p.slug for p in PAGINAS}), len(PAGINAS))
        for pagina in PAGINAS:
            self.assertTrue(pagina.textos, pagina.slug)
            self.assertTrue(pagina.caminho.startswith("/"), pagina.slug)

    def test_every_text_is_described_and_has_a_section(self):
        from website.conteudo import PAGINAS

        for pagina in PAGINAS:
            for texto in pagina.textos:
                self.assertTrue(texto.rotulo.strip() and texto.secao.strip(), texto.chave)
                # Só um texto opcional pode ter o original vazio (o aviso da Home começa sem nada).
                self.assertTrue(texto.padrao.strip() or texto.opcional, texto.chave)

    def test_keys_start_with_the_name_the_frontend_uses_for_their_page(self):
        from website.conteudo import PAGINAS

        for pagina in PAGINAS:
            for texto in pagina.textos:
                self.assertRegex(texto.chave, r"^[a-z_]+\.[a-z_0-9]+$", texto.chave)

    def test_compatibility_layer_keeps_the_old_shape_and_order(self):
        from website.conteudo import PAGINAS
        from website.site_texts import GRUPOS, PADRAO, TEXTOS

        self.assertEqual([t[0] for t in TEXTOS], [t.chave for p in PAGINAS for t in p.textos])
        self.assertEqual(GRUPOS, [p.titulo for p in PAGINAS])
        self.assertEqual(PADRAO["equipe.titulo"], "Nossa Equipe")

    def test_long_texts_get_a_multiline_field_and_short_ones_do_not(self):
        from website.conteudo import POR_CHAVE

        self.assertTrue(POR_CHAVE["privacidade.erro"][1].e_longo)
        self.assertFalse(POR_CHAVE["equipe.titulo"][1].e_longo)

    def test_every_key_the_frontend_asks_for_exists_in_the_registry(self):
        import re
        from pathlib import Path

        from website.conteudo import POR_CHAVE

        pasta = Path(__file__).resolve().parents[2] / "frontend" / "src"
        pedidas = set()
        for arquivo in pasta.rglob("*.tsx"):
            pedidas |= set(re.findall(r'\bt\("([a-z_]+\.[a-z_0-9]+)"\)', arquivo.read_text(encoding="utf-8")))

        self.assertGreater(len(pedidas), 100)
        self.assertEqual(sorted(pedidas - set(POR_CHAVE)), [], "o frontend usa uma chave que o registro não tem")

    def test_sync_creates_the_pages_in_site_order_and_removes_the_ones_that_left(self):
        from website.conteudo import PAGINAS
        from website.models import PaginaDoSite
        from website.site_texts import sincroniza_paginas

        PaginaDoSite.objects.create(slug="pagina-antiga", title="Antiga", path="/", order=99)
        PaginaDoSite.objects.filter(slug="home").update(title="Nome velho", order=50)

        sincroniza_paginas()

        self.assertEqual(list(PaginaDoSite.objects.values_list("slug", flat=True)), [p.slug for p in PAGINAS])
        self.assertEqual(PaginaDoSite.objects.get(slug="home").title, "Home")

    def test_sync_moves_texts_to_the_renamed_page_without_touching_their_value(self):
        SiteText.objects.filter(key="projetos.titulo").update(group="Projetos", value="Editado pelo ICC")

        from website.site_texts import sincroniza_textos

        sincroniza_textos()

        texto = SiteText.objects.get(key="projetos.titulo")
        self.assertEqual(texto.group, "Projetos (lista)")
        self.assertEqual(texto.value, "Editado pelo ICC")


@SEM_MANIFESTO
class TextosDoSiteAdminTests(TestCase):
    """A tela "Textos do site": uma página por vez, com as seções dela."""

    def setUp(self):
        from django.contrib.auth.models import Group

        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.editor = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste", is_staff=True)
        self.editor.groups.add(Group.objects.get(name="Editores"))
        self.client.force_login(self.admin)
        self.home = PaginaDoSite.objects.get(slug="home")
        self.url = f"/admin/website/paginadosite/{self.home.pk}/change/"

    def dados(self, slug="home", **mudancas):
        """O formulário completo de uma página, com o valor atual de cada texto e as mudanças pedidas (por chave)."""
        from website.admin import nome_do_campo
        from website.conteudo import POR_SLUG

        valores = dict(SiteText.objects.values_list("key", "value"))
        dados = {nome_do_campo(t.chave): valores[t.chave] for t in POR_SLUG[slug].textos}
        dados.update({nome_do_campo(chave.replace("__", ".")): valor for chave, valor in mudancas.items()})
        return dados

    # --- a lista de páginas

    def test_list_shows_the_pages_in_site_order_with_counts(self):
        from website.conteudo import PAGINAS

        resposta = self.client.get("/admin/website/paginadosite/")

        self.assertEqual([p.slug for p in resposta.context["cl"].result_list], [p.slug for p in PAGINAS])
        self.assertIn("Textos do site", resposta.content.decode())

    def test_add_and_delete_are_blocked(self):
        self.assertEqual(self.client.get("/admin/website/paginadosite/add/").status_code, 403)
        self.assertEqual(self.client.get(f"/admin/website/paginadosite/{self.home.pk}/delete/").status_code, 403)

    # --- o formulário de uma página

    def test_page_form_groups_texts_by_section_with_plain_labels(self):
        pagina = self.client.get(self.url).content.decode()

        for secao in ("Apresentação", "Quem somos", "Missão", "Programas", "Chamada final"):
            self.assertIn(secao, pagina)
        self.assertIn("Botão principal, logo abaixo da frase de apresentação", pagina)
        self.assertIn('name="t__home__hero_botao_principal"', pagina)
        self.assertIn('value="Seja membro"', pagina)

    def test_rare_messages_are_collapsed_in_their_own_block(self):
        pagina = PaginaDoSite.objects.get(slug="equipe")

        html = self.client.get(f"/admin/website/paginadosite/{pagina.pk}/change/").content.decode()

        self.assertIn("Mensagens e estados raros (3)", html)
        self.assertIn("<details", html)

    def test_long_texts_use_a_textarea(self):
        pagina = PaginaDoSite.objects.get(slug="privacidade")

        html = self.client.get(f"/admin/website/paginadosite/{pagina.pk}/change/").content.decode()

        self.assertIn("<textarea", html)
        self.assertIn('name="t__privacidade__erro"', html)

    def test_saving_changes_only_what_was_edited_and_the_api_follows(self):
        resposta = self.client.post(self.url, self.dados(home__membros_titulo="Quem faz o clube"))

        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Quem faz o clube")
        self.assertEqual(SiteText.objects.get(key="home.parceiros_titulo").value, "Empresas que confiam no nosso trabalho")
        self.assertEqual(APIClient().get("/api/site-config/").data["texts"]["home.membros_titulo"], "Quem faz o clube")

    def test_a_text_cannot_be_left_empty(self):
        resposta = self.client.post(self.url, self.dados(home__membros_titulo=""))

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Quem constrói o clube")

    def test_editing_must_keep_the_placeholders(self):
        projeto = PaginaDoSite.objects.get(slug="projetos")
        url = f"/admin/website/paginadosite/{projeto.pk}/change/"

        recusado = self.client.post(url, self.dados("projetos", projetos__cases_titulo_varios="Cases do programa"))
        self.assertEqual(recusado.status_code, 200)
        self.assertIn("Mantenha no texto", recusado.content.decode())
        self.assertEqual(SiteText.objects.get(key="projetos.cases_titulo_varios").value, "{programa}: {n} cases")

        aceito = self.client.post(url, self.dados("projetos", projetos__cases_titulo_varios="{n} cases em {programa}"))
        self.assertEqual(aceito.status_code, 302)
        self.assertEqual(SiteText.objects.get(key="projetos.cases_titulo_varios").value, "{n} cases em {programa}")

    # --- editado, original e restaurar

    def test_an_edited_text_shows_the_mark_the_original_and_a_restore_button(self):
        limpo = self.client.get(self.url).content.decode()
        self.assertNotIn("texto-editado", limpo)

        SiteText.objects.filter(key="home.membros_titulo").update(value="Quem faz o clube")
        editado = self.client.get(self.url).content.decode()

        self.assertEqual(editado.count('class="texto-editado"'), 1)
        self.assertIn("Quem constrói o clube", editado)
        self.assertIn("Restaurar o original", editado)

    def test_restore_action_brings_every_text_of_the_selected_pages_back(self):
        SiteText.objects.filter(key="home.membros_titulo").update(value="Editado 1")
        SiteText.objects.filter(key="home.parceiros_titulo").update(value="Editado 2")
        SiteText.objects.filter(key="equipe.titulo").update(value="Editado 3")

        self.client.post("/admin/website/paginadosite/", {"action": "restaurar_originais", "_selected_action": [self.home.pk]})

        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Quem constrói o clube")
        self.assertEqual(SiteText.objects.get(key="home.parceiros_titulo").value, "Empresas que confiam no nosso trabalho")
        self.assertEqual(SiteText.objects.get(key="equipe.titulo").value, "Editado 3")  # outra página: não foi marcada

    def test_status_filter_separates_pages_with_edited_texts(self):
        SiteText.objects.filter(key="equipe.titulo").update(value="Editado")

        editadas = self.client.get("/admin/website/paginadosite/?situacao=editados").content.decode()
        originais = self.client.get("/admin/website/paginadosite/?situacao=originais").content.decode()

        self.assertIn("Equipe", editadas)
        self.assertNotIn("Parceiros", editadas.split("Equipe")[-1][:50])
        self.assertNotIn(">Equipe<", originais)
        self.assertIn("Parceiros", originais)

    # --- busca

    def test_search_finds_pages_by_what_the_text_says_and_shows_the_matches(self):
        resposta = self.client.get("/admin/website/paginadosite/?q=Quem+constr%C3%B3i+o+clube")

        slugs = [p.slug for p in resposta.context["cl"].result_list]
        self.assertIn("home", slugs)
        self.assertNotIn("artigos", slugs)
        self.assertIn("Textos encontrados", resposta.content.decode())

    def test_search_ignores_accents_and_looks_at_the_description_and_the_edited_value(self):
        achou_missao = self.client.get("/admin/website/paginadosite/?q=missao").content.decode()
        self.assertIn("Home", achou_missao)

        SiteText.objects.filter(key="rodape.admin").update(value="Painel interno")
        achou_valor = self.client.get("/admin/website/paginadosite/?q=painel+interno").content.decode()
        self.assertIn("Rodapé", achou_valor)

    # --- permissões e ver no site

    def test_an_editor_can_edit_texts_but_not_add_or_delete(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.dados(home__membros_titulo="Quem faz o clube")).status_code, 302)
        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Quem faz o clube")
        self.assertEqual(self.client.get("/admin/website/paginadosite/add/").status_code, 403)

    def test_a_viewer_cannot_change_texts(self):
        from django.contrib.auth.models import Permission

        leitor = get_user_model().objects.create_user("leitor", "l@example.com", "senha-de-teste", is_staff=True)
        leitor.user_permissions.add(Permission.objects.get(codename="view_paginadosite"))
        self.client.force_login(leitor)

        self.client.post(self.url, self.dados(home__membros_titulo="Quem faz o clube"))

        self.assertEqual(SiteText.objects.get(key="home.membros_titulo").value, "Quem constrói o clube")

    def test_view_on_site_points_to_the_page_of_the_texts(self):
        from django.contrib import admin

        from website.admin import PaginaDoSiteAdmin

        with self.settings(FRONTEND_URL="https://exemplo.com.br"):
            modelo_admin = PaginaDoSiteAdmin(PaginaDoSite, admin.site)
            self.assertEqual(modelo_admin.view_on_site(PaginaDoSite.objects.get(slug="equipe")), "https://exemplo.com.br/equipe")
            self.assertEqual(modelo_admin.view_on_site(self.home), "https://exemplo.com.br/")

    def test_menu_entry_is_textos_do_site_for_editors_too(self):
        from config.navigation import navegacao

        requisicao = mock.Mock(user=get_user_model().objects.get(pk=self.editor.pk))

        itens = [i["title"] for g in navegacao(requisicao) for i in g["items"]]

        self.assertIn("Textos do site", itens)


@SEM_MANIFESTO
class PageTextsMovedFromConfigTests(TestCase):
    """Etapa B: os textos de página saíram dos campos da Configuração do site e vivem no registro."""

    ANTIGOS = (
        "home_hero_title", "home_statement", "home_about_title", "home_about_title_highlight", "home_about_text",
        "mission", "mission_how", "mission_goal", "home_cta_title", "footer_tagline", "team_lead", "partners_lead",
        "partners_benefits_title", "projects_lead", "articles_lead", "contact_lead", "process_lead",
        "process_closed_message",
    )

    def test_the_site_configuration_no_longer_has_the_page_texts(self):
        campos = {c.name for c in SiteConfig._meta.get_fields()}

        self.assertEqual(sorted(set(self.ANTIGOS) & campos), [])
        self.assertTrue({"email", "home_about_photo", "home_about_photo_alt", "featured_program_slug",
                         "privacy_text", "privacy_updated"} <= campos)

    def test_the_api_serves_the_page_texts_only_by_key(self):
        SiteText.objects.filter(key="home.hero_titulo").update(value="Editado pelo ICC")
        dados = APIClient().get("/api/site-config/").data

        self.assertEqual(dados["texts"]["home.hero_titulo"], "Editado pelo ICC")
        self.assertEqual(sorted(set(self.ANTIGOS) & set(dados)), [])
        self.assertIn("email", dados)

    def test_default_texts_are_what_the_site_always_had(self):
        from website.conteudo import PADRAO

        self.assertEqual(PADRAO["home.hero_titulo"], "O futuro consultor começa no ICC")
        self.assertEqual(PADRAO["rodape.frase"], "Mais do que um clube, somos um ambiente de formação para futuros consultores.")
        self.assertTrue(PADRAO["home.sobre_texto"].startswith("A Liga Insper Consulting Club é uma organização"))

    def test_the_moved_texts_appear_in_the_page_forms_and_long_ones_use_a_textarea(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste"))
        home = PaginaDoSite.objects.get(slug="home")

        html = self.client.get(f"/admin/website/paginadosite/{home.pk}/change/").content.decode()

        self.assertIn('name="t__home__hero_titulo"', html)
        self.assertIn('<textarea name="t__home__sobre_texto"', html)
        self.assertIn('<textarea name="t__home__missao_texto"', html)

    def test_the_optional_text_can_be_left_empty_and_a_required_one_cannot(self):
        from website.admin import nome_do_campo
        from website.conteudo import POR_SLUG

        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste"))
        home = PaginaDoSite.objects.get(slug="home")
        url = f"/admin/website/paginadosite/{home.pk}/change/"
        valores = dict(SiteText.objects.values_list("key", "value"))
        dados = {nome_do_campo(t.chave): valores[t.chave] for t in POR_SLUG["home"].textos}

        dados[nome_do_campo("home.sobre_titulo_destaque")] = ""
        self.assertEqual(self.client.post(url, dados).status_code, 302)
        self.assertEqual(SiteText.objects.get(key="home.sobre_titulo_destaque").value, "")

        dados[nome_do_campo("home.hero_titulo")] = ""
        self.assertEqual(self.client.post(url, dados).status_code, 200)

    def test_the_editor_edits_the_page_texts_in_the_texts_screen(self):
        from django.contrib.auth.models import Group

        editor = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste", is_staff=True)
        editor.groups.add(Group.objects.get(name="Editores"))
        self.client.force_login(editor)
        home = PaginaDoSite.objects.get(slug="home")

        self.assertContains(self.client.get(f"/admin/website/paginadosite/{home.pk}/change/"), "t__home__hero_titulo")


class PageTextsMigrationTests(TransactionTestCase):
    """Migration 0030: os campos da Configuração do site viram textos, e o caminho de volta funciona."""

    ANTES = ("website", "0029_paginas_de_textos")
    DEPOIS = ("website", "0030_textos_das_paginas_no_registro")

    def _estado(self, alvo):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        MigrationExecutor(connection).migrate([alvo])
        return MigrationExecutor(connection).loader.project_state([alvo]).apps

    def tearDown(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_edited_values_move_to_the_texts_and_the_untouched_ones_keep_the_original(self):
        antigo = self._estado(self.ANTES)
        SiteConfig = antigo.get_model("website", "SiteConfig")
        SiteConfig.objects.get_or_create(pk=1)  # um teste de transação anterior pode ter esvaziado o banco
        SiteConfig.objects.filter(pk=1).update(
            home_hero_title="Título do ICC", mission="Missão nova, bem mais longa " * 20, footer_tagline="",
        )

        novo = self._estado(self.DEPOIS)
        SiteText = novo.get_model("website", "SiteText")

        self.assertEqual(SiteText.objects.get(key="home.hero_titulo").value, "Título do ICC")
        self.assertEqual(SiteText.objects.get(key="home.missao_texto").value, "Missão nova, bem mais longa " * 20)
        self.assertEqual(SiteText.objects.get(key="rodape.frase").value, "")
        self.assertEqual(SiteText.objects.get(key="equipe.abertura").value,
                         "Conheça os membros que fazem parte da Liga Insper Consulting Club")
        self.assertFalse(hasattr(novo.get_model("website", "SiteConfig"), "home_hero_title"))

    def test_undoing_the_migration_puts_the_texts_back_in_the_fields(self):
        novo = self._estado(self.DEPOIS)
        novo.get_model("website", "SiteConfig").objects.get_or_create(pk=1)
        SiteText = novo.get_model("website", "SiteText")
        SiteText.objects.update_or_create(key="home.hero_titulo", defaults={"value": "Voltou", "group": "Home", "description": "x"})
        SiteText.objects.update_or_create(key="home.sobre_texto", defaults={"value": "Texto " * 100, "group": "Home", "description": "x"})
        SiteText.objects.update_or_create(key="equipe.titulo", defaults={"value": "Outro texto", "group": "Equipe", "description": "x"})

        antigo = self._estado(self.ANTES)
        config = antigo.get_model("website", "SiteConfig").objects.get(pk=1)

        self.assertEqual(config.home_hero_title, "Voltou")
        self.assertEqual(config.home_about_text, "Texto " * 100)
        self.assertEqual(config.team_lead, "Conheça os membros que fazem parte da Liga Insper Consulting Club")
        SiteText = antigo.get_model("website", "SiteText")
        self.assertFalse(SiteText.objects.filter(key="home.hero_titulo").exists())
        self.assertEqual(SiteText.objects.get(key="equipe.titulo").value, "Outro texto")


class HomeSectionsRegistryTests(TestCase):
    """As seções da Home que o editor mostra, esconde e reordena (SecaoDaHome)."""

    def test_a_new_database_has_every_section_in_the_registry_order_with_the_notice_hidden_first(self):
        from website.conteudo import SECOES_DA_HOME

        linhas = list(SecaoDaHome.objects.values_list("key", "visible"))

        self.assertEqual([k for k, _ in linhas], [s.chave for s in SECOES_DA_HOME])
        self.assertEqual(linhas[0], ("aviso", False))
        self.assertTrue(all(v for k, v in linhas if k != "aviso"))

    def test_registry_keys_are_unique(self):
        from website.conteudo import SECOES_DA_HOME

        chaves = [s.chave for s in SECOES_DA_HOME]

        self.assertEqual(len(chaves), len(set(chaves)))
        self.assertNotIn("topo", chaves)
        self.assertNotIn("apresentacao", chaves)

    def test_sync_keeps_what_the_editor_chose_and_puts_a_new_section_last(self):
        from website.site_texts import sincroniza_secoes
        import website.site_texts as modulo
        from website.conteudo.base import Secao

        SecaoDaHome.objects.filter(key="missao").update(visible=False, order=50)
        SecaoDaHome.objects.filter(key="programas").update(title="Nome velho")
        SecaoDaHome.objects.filter(key="aviso").update(button_url="https://exemplo.com.br")
        SecaoDaHome.objects.filter(key="parceiros").delete()
        original = modulo.SECOES_DA_HOME
        try:
            modulo.SECOES_DA_HOME = original + (Secao("novidade", "Novidade"),)
            sincroniza_secoes()
        finally:
            modulo.SECOES_DA_HOME = original

        missao = SecaoDaHome.objects.get(key="missao")
        self.assertEqual((missao.visible, missao.order), (False, 50))
        self.assertEqual(SecaoDaHome.objects.get(key="programas").title, "Programas")
        self.assertEqual(SecaoDaHome.objects.get(key="aviso").button_url, "https://exemplo.com.br")
        self.assertEqual(list(SecaoDaHome.objects.order_by("-order").values_list("key", flat=True))[:2], ["novidade", "parceiros"])
        self.assertTrue(SecaoDaHome.objects.get(key="parceiros").visible)

    def test_sync_removes_a_section_that_left_the_registry(self):
        SecaoDaHome.objects.create(key="antiga", title="Antiga", order=99)

        from website.site_texts import sincroniza_secoes

        sincroniza_secoes()

        self.assertFalse(SecaoDaHome.objects.filter(key="antiga").exists())

    # --- botão do aviso

    def test_the_button_goes_to_a_site_page_or_a_free_link_but_not_both(self):
        from django.core.exceptions import ValidationError

        secao = SecaoDaHome.objects.get(key="aviso")
        secao.button_page = "processo"
        secao.full_clean()
        self.assertEqual((secao.button_path, secao.button_external), ("/processo", False))

        secao.button_page, secao.button_url = "", "https://exemplo.com.br/edital"
        secao.full_clean()
        self.assertEqual((secao.button_path, secao.button_external), ("https://exemplo.com.br/edital", True))

        secao.button_page = "processo"
        with self.assertRaises(ValidationError):
            secao.full_clean()

        secao.button_page, secao.button_url = "", "edital"
        with self.assertRaises(ValidationError):
            secao.full_clean()

    # --- API

    def secoes_da_api(self):
        return APIClient().get("/api/site-config/").data["home_sections"]

    def test_api_lists_the_visible_sections_in_the_editor_order_without_the_hidden_notice(self):
        chaves = [s["key"] for s in self.secoes_da_api()]

        self.assertEqual(chaves, ["quem_somos", "estatisticas", "missao", "programas", "equipe", "parceiros", "chamada_final"])

    def test_hidden_sections_and_the_new_order_reach_the_api(self):
        SecaoDaHome.objects.filter(key="missao").update(visible=False)
        SecaoDaHome.objects.filter(key="chamada_final").update(order=0)

        chaves = [s["key"] for s in self.secoes_da_api()]

        self.assertEqual(chaves[0], "chamada_final")
        self.assertNotIn("missao", chaves)

    def test_the_notice_needs_to_be_on_and_to_have_text(self):
        SecaoDaHome.objects.filter(key="aviso").update(visible=True)
        self.assertNotIn("aviso", [s["key"] for s in self.secoes_da_api()])  # ligado, mas sem texto

        SiteText.objects.filter(key="home.aviso_texto").update(value="Inscrições abertas até sexta.")
        secoes = self.secoes_da_api()

        self.assertEqual(secoes[0], {"key": "aviso", "button_path": None, "button_external": False})

    def test_the_notice_button_comes_with_its_destination(self):
        SiteText.objects.filter(key="home.aviso_texto").update(value="Inscrições abertas.")
        SecaoDaHome.objects.filter(key="aviso").update(visible=True, button_page="processo")
        self.assertEqual(self.secoes_da_api()[0]["button_path"], "/processo")

        SecaoDaHome.objects.filter(key="aviso").update(button_page="", button_url="https://exemplo.com.br/edital")
        aviso = self.secoes_da_api()[0]

        self.assertEqual((aviso["button_path"], aviso["button_external"]), ("https://exemplo.com.br/edital", True))

    def test_the_notice_texts_start_empty(self):
        textos = APIClient().get("/api/site-config/").data["texts"]

        self.assertEqual((textos["home.aviso_titulo"], textos["home.aviso_texto"], textos["home.aviso_botao"]), ("", "", ""))


@SEM_MANIFESTO
class HomeSectionsAdminTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group

        self.admin = get_user_model().objects.create_superuser("root", "root@example.com", "senha-de-teste")
        self.editor = get_user_model().objects.create_user("editora", "e@example.com", "senha-de-teste", is_staff=True)
        self.editor.groups.add(Group.objects.get(name="Editores"))
        self.client.force_login(self.admin)
        self.aviso = SecaoDaHome.objects.get(key="aviso")
        self.missao = SecaoDaHome.objects.get(key="missao")

    def test_list_shows_the_sections_in_order_and_has_no_add_or_delete(self):
        resposta = self.client.get("/admin/website/secaodahome/")

        self.assertEqual([s.key for s in resposta.context["cl"].result_list], [s.key for s in SecaoDaHome.objects.all()])
        self.assertEqual(self.client.get("/admin/website/secaodahome/add/").status_code, 403)
        self.assertEqual(self.client.get(f"/admin/website/secaodahome/{self.missao.pk}/delete/").status_code, 403)

    def test_only_the_notice_form_has_the_button_fields(self):
        aviso = self.client.get(f"/admin/website/secaodahome/{self.aviso.pk}/change/").content.decode()
        missao = self.client.get(f"/admin/website/secaodahome/{self.missao.pk}/change/").content.decode()

        self.assertIn('name="button_page"', aviso)
        self.assertIn('name="button_url"', aviso)
        self.assertIn("Textos do site", aviso)
        self.assertNotIn('name="button_page"', missao)
        self.assertIn('name="visible"', missao)

    def test_hiding_a_section_in_the_form_reaches_the_api(self):
        self.client.post(f"/admin/website/secaodahome/{self.missao.pk}/change/", {})  # desmarcado: o campo não vem

        self.assertFalse(SecaoDaHome.objects.get(pk=self.missao.pk).visible)
        self.assertNotIn("missao", [s["key"] for s in APIClient().get("/api/site-config/").data["home_sections"]])

    def test_the_notice_form_saves_the_button_and_refuses_two_destinations(self):
        url = f"/admin/website/secaodahome/{self.aviso.pk}/change/"

        recusado = self.client.post(url, {"visible": "on", "button_page": "processo", "button_url": "https://x.com"})
        self.assertEqual(recusado.status_code, 200)
        self.assertFalse(SecaoDaHome.objects.get(pk=self.aviso.pk).visible)

        aceito = self.client.post(url, {"visible": "on", "button_page": "processo", "button_url": ""})
        self.assertEqual(aceito.status_code, 302)
        aviso = SecaoDaHome.objects.get(pk=self.aviso.pk)
        self.assertEqual((aviso.visible, aviso.button_page), (True, "processo"))

    def test_the_notice_texts_are_edited_in_the_home_texts_page_and_may_stay_empty(self):
        home = PaginaDoSite.objects.get(slug="home")

        html = self.client.get(f"/admin/website/paginadosite/{home.pk}/change/").content.decode()

        for chave in ("aviso_titulo", "aviso_texto", "aviso_botao"):
            self.assertIn(f'name="t__home__{chave}"', html)
        self.assertIn('<textarea name="t__home__aviso_texto"', html)

    def test_an_editor_can_change_the_sections_but_not_add_or_delete(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get("/admin/website/secaodahome/").status_code, 200)
        self.assertEqual(self.client.post(f"/admin/website/secaodahome/{self.missao.pk}/change/", {"visible": "on"}).status_code, 302)
        self.assertEqual(self.client.get("/admin/website/secaodahome/add/").status_code, 403)

    def test_an_old_editors_group_with_the_texts_permission_gets_the_sections_permission(self):
        from django.apps import apps
        from django.contrib.auth.models import Group, Permission
        from website.editors_group import sincroniza_grupo_editores

        grupo = Group.objects.get(name="Editores")
        grupo.permissions.remove(*Permission.objects.filter(codename__in=["change_secaodahome", "view_secaodahome"]))

        sincroniza_grupo_editores(apps, apps.get_app_config("website"))

        self.assertTrue(grupo.permissions.filter(codename="change_secaodahome").exists())

    def test_a_group_without_the_texts_permission_is_left_alone(self):
        from django.apps import apps
        from django.contrib.auth.models import Group, Permission
        from website.editors_group import sincroniza_grupo_editores

        grupo = Group.objects.get(name="Editores")
        grupo.permissions.remove(*Permission.objects.filter(codename__in=["change_paginadosite", "change_secaodahome", "view_secaodahome"]))

        sincroniza_grupo_editores(apps, apps.get_app_config("website"))

        self.assertFalse(grupo.permissions.filter(codename="change_secaodahome").exists())

    def test_original_of_an_empty_text_is_shown_as_empty(self):
        SiteText.objects.filter(key="home.aviso_titulo").update(value="Edital novo")
        home = PaginaDoSite.objects.get(slug="home")

        html = self.client.get(f"/admin/website/paginadosite/{home.pk}/change/").content.decode()

        self.assertIn("Original: <em>vazio</em>", html)


class ArticleAuthorModelTests(TestCase):
    """O autor é um nome, vinculado a um membro quando o editor o escolhe na lista (o model não adivinha pelo nome)."""

    def setUp(self):
        self.artigo = Article.objects.create(title="A", description="d")
        self.ana = Member.objects.create(name="Ana Silva")
        self.robert = Member.objects.create(name="Robert Lucas Jr", citation_name="Robert {Lucas Jr}")

    def autor(self, **dados):
        autor = ArticleAuthor(article=self.artigo, **dados)
        autor.clean()
        return autor

    def test_the_name_of_a_chosen_member_is_normalized_to_the_registered_one(self):
        autor = self.autor(member=self.ana, name="  ana SILVA ")

        self.assertEqual(autor.member, self.ana)
        self.assertEqual(autor.name, "Ana Silva")  # com vínculo, vale o nome do cadastro

    def test_the_citation_name_of_the_member_is_used_when_the_name_matches(self):
        for escrito in ("Robert Lucas Jr", "robert lucas jr", "Robert {Lucas Jr}"):
            autor = self.autor(member=self.robert, name=escrito)
            self.assertEqual(autor.name, "Robert {Lucas Jr}", escrito)
            self.assertEqual(autor.display_name, "Robert Lucas Jr", escrito)

    def test_choosing_the_member_without_a_name_fills_the_name(self):
        self.assertEqual(self.autor(member=self.ana).name, "Ana Silva")
        self.assertEqual(self.autor(member=self.robert).name, "Robert {Lucas Jr}")

    def test_a_name_alone_does_not_link_even_when_it_is_a_members_name(self):
        autor = self.autor(name="Ana Silva")

        self.assertIsNone(autor.member)
        self.assertEqual(autor.name, "Ana Silva")

    def test_an_outside_author_stays_without_a_member_and_keeps_the_braces(self):
        autor = self.autor(name="Maria {da Silva}")

        self.assertIsNone(autor.member)
        self.assertEqual((autor.name, autor.display_name), ("Maria {da Silva}", "Maria da Silva"))

    def test_a_different_name_for_a_chosen_member_is_kept(self):
        autor = self.autor(member=self.ana, name="A. Silva")

        self.assertEqual((autor.member, autor.name), (self.ana, "A. Silva"))

    def test_a_blank_author_is_refused(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            self.autor(name="  ")

    def test_unbalanced_braces_are_refused(self):
        from django.core.exceptions import ValidationError

        for nome in ("Robert {Lucas Jr", "Robert Lucas} Jr", "}{"):
            with self.assertRaises(ValidationError, msg=nome):
                self.autor(name=nome)

    def test_deleting_the_member_keeps_the_author_as_a_plain_name(self):
        autor = self.autor(member=self.ana)
        autor.save()

        self.ana.delete()
        autor.refresh_from_db()

        self.assertIsNone(autor.member)
        self.assertEqual(autor.name, "Ana Silva")


class ArticleAuthorsApiTests(TestCase):
    def setUp(self):
        self.ana = Member.objects.create(name="Ana Silva")
        self.antigo = Member.objects.create(name="Beto Souza", is_active=False)
        self.artigo = Article.objects.create(title="A", description="d", slug="a", published=True)
        for ordem, (nome, membro) in enumerate([("Beto Souza", self.antigo), ("Convidado {de Fora}", None), ("Ana Silva", self.ana)]):
            ArticleAuthor.objects.create(article=self.artigo, name=nome, member=membro, order=ordem)

    def test_list_and_detail_return_the_authors_in_order_with_member_and_profile(self):
        esperado = [
            {"name": "Beto Souza", "member_id": self.antigo.pk, "has_profile": False},  # arquivado: sem perfil
            {"name": "Convidado de Fora", "member_id": None, "has_profile": False},  # sem as chaves
            {"name": "Ana Silva", "member_id": self.ana.pk, "has_profile": True},
        ]

        self.assertEqual(APIClient().get("/api/articles/").data[0]["authors"], esperado)
        self.assertEqual(APIClient().get("/api/articles/a/").data["authors"], esperado)

    def test_an_institutional_article_has_a_single_author_the_club(self):
        Article.objects.filter(pk=self.artigo.pk).update(institutional=True)

        autores = APIClient().get("/api/articles/a/").data["authors"]

        self.assertEqual(autores, [{"name": "Insper Consulting Club", "member_id": None, "has_profile": False}])

    def test_the_old_fields_are_gone(self):
        dados = APIClient().get("/api/articles/a/").data

        self.assertNotIn("link", dados)
        self.assertNotIn("source", dados)

    def test_the_list_does_not_make_one_query_per_author(self):
        for i in range(5):
            artigo = Article.objects.create(title=f"B{i}", description="d", published=True)
            ArticleAuthor.objects.create(article=artigo, name="Ana Silva", member=self.ana)

        with self.assertNumQueries(3):  # artigos, autores e seus membros
            APIClient().get("/api/articles/")


@SEM_MANIFESTO
class ArticleAuthorsAdminTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste"))
        self.ana = Member.objects.create(name="Ana Silva")
        self.artigo = Article.objects.create(title="A", description="d", slug="a")
        self.url = f"/admin/website/article/{self.artigo.pk}/change/"

    def dados(self, autores=(), **extra):
        dados = {
            "title": "A", "slug": "a", "description": "d", "order": "0", "date": "2026-01-05",
            "article_authors-TOTAL_FORMS": str(len(autores)), "article_authors-INITIAL_FORMS": "0",
            "article_authors-MIN_NUM_FORMS": "0", "article_authors-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0", "images-INITIAL_FORMS": "0", "images-MIN_NUM_FORMS": "0", "images-MAX_NUM_FORMS": "1000",
        }
        for i, (nome, ordem, *membro) in enumerate(autores):
            dados.update({
                f"article_authors-{i}-name": nome, f"article_authors-{i}-order": str(ordem),
                f"article_authors-{i}-member": str(membro[0].pk) if membro else "",
            })
        dados.update(extra)
        return dados

    def test_the_form_has_the_authors_list_with_the_member_combobox_and_no_old_fields(self):
        html = self.client.get(self.url).content.decode()

        self.assertIn('name="article_authors-0-name"', html)
        self.assertIn('autor-combobox__input', html)
        self.assertIn('role="combobox"', html)
        self.assertIn('website/autor_combobox.js', html)
        self.assertRegex(html, r'<input type="hidden" name="article_authors-0-member"')  # o vínculo vem da escolha na lista
        self.assertNotIn("<datalist", html)
        self.assertIn('name="institutional"', html)
        for campo in ('name="authors"', 'name="link"', 'name="source"'):
            self.assertNotIn(campo, html)

    def test_the_combobox_carries_the_members_with_the_id_only_for_homonyms_and_marks_former_members(self):
        import json

        antiga = Member.objects.create(name="ana silva", is_active=False)
        html = self.client.get(self.url).content.decode()
        lista = html[html.index('data-membros="') + len('data-membros="'):]
        lista = lista[:lista.index('"')].replace("&quot;", '"')

        membros = {m["id"]: m for m in json.loads(lista)}

        self.assertEqual(membros[self.ana.pk]["rotulo"], f"Ana Silva (ID {self.ana.pk})")
        self.assertEqual(membros[antiga.pk]["rotulo"], f"ana silva (ID {antiga.pk})")
        self.assertEqual((membros[self.ana.pk]["nome"], membros[self.ana.pk]["ex"]), ("Ana Silva", False))
        self.assertTrue(membros[antiga.pk]["ex"])

    def test_the_chosen_member_links_and_a_typed_name_is_an_outside_author_even_when_it_matches_a_member(self):
        resposta = self.client.post(
            self.url, self.dados([("Ana Silva", 0, self.ana), ("Ana Silva", 1), ("Convidado {de Fora}", 2)], published="on"),
        )

        self.assertEqual(resposta.status_code, 302)
        autores = list(self.artigo.article_authors.order_by("order"))
        self.assertEqual(
            [(a.name, a.member) for a in autores],
            [("Ana Silva", self.ana), ("Ana Silva", None), ("Convidado {de Fora}", None)],
        )
        self.assertTrue(Article.objects.get(pk=self.artigo.pk).published)

    def test_a_homonym_is_told_apart_by_the_chosen_member(self):
        outra = Member.objects.create(name="Ana Silva", is_active=False)

        self.assertEqual(self.client.post(self.url, self.dados([("Ana Silva", 0, outra)])).status_code, 302)

        self.assertEqual(self.artigo.article_authors.get().member, outra)

    def test_an_unknown_member_id_is_refused(self):
        dados = self.dados([("Ana Silva", 0, self.ana)])
        dados["article_authors-0-member"] = "99999"

        self.assertEqual(self.client.post(self.url, dados).status_code, 200)
        self.assertFalse(self.artigo.article_authors.exists())

    def test_a_published_article_needs_an_author_or_to_be_institutional(self):
        recusado = self.client.post(self.url, self.dados(published="on"))
        self.assertEqual(recusado.status_code, 200)
        self.assertIn("precisa de ao menos um autor", recusado.content.decode())
        self.assertFalse(Article.objects.get(pk=self.artigo.pk).published)

        institucional = self.client.post(self.url, self.dados(published="on", institutional="on"))
        self.assertEqual(institucional.status_code, 302)

    def test_a_new_author_row_goes_to_the_end_when_it_was_not_dragged(self):
        ArticleAuthor.objects.create(article=self.artigo, name="Primeiro", order=0)
        ArticleAuthor.objects.create(article=self.artigo, name="Segundo", order=1)
        existentes = list(self.artigo.article_authors.all())
        dados = self.dados([("Primeiro", 0), ("Segundo", 1), ("Novo", 0)])
        dados["article_authors-INITIAL_FORMS"] = "2"
        for i, autor in enumerate(existentes):
            dados[f"article_authors-{i}-id"] = str(autor.pk)
            dados[f"article_authors-{i}-article"] = str(self.artigo.pk)

        self.assertEqual(self.client.post(self.url, dados).status_code, 302)

        self.assertEqual(list(self.artigo.article_authors.order_by("order").values_list("name", flat=True)), ["Primeiro", "Segundo", "Novo"])

    def test_a_draft_can_be_saved_without_authors(self):
        self.assertEqual(self.client.post(self.url, self.dados()).status_code, 302)

    def test_an_institutional_article_cannot_also_have_authors(self):
        resposta = self.client.post(self.url, self.dados([("Ana Silva", 0)], institutional="on"))

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("não tem autores individuais", resposta.content.decode())

    def test_a_name_with_open_braces_is_refused_in_the_form(self):
        resposta = self.client.post(self.url, self.dados([("Robert {Lucas Jr", 0)]))

        self.assertEqual(resposta.status_code, 200)
        self.assertIn("precisam abrir e fechar", resposta.content.decode())

    def test_publishing_from_the_list_also_needs_an_author(self):
        dados = {
            "form-TOTAL_FORMS": "1", "form-INITIAL_FORMS": "1", "form-MIN_NUM_FORMS": "0", "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(self.artigo.pk), "form-0-published": "on", "form-0-order": "0", "_save": "Salvar",
        }

        self.client.post("/admin/website/article/", dados)
        self.assertFalse(Article.objects.get(pk=self.artigo.pk).published)

        ArticleAuthor.objects.create(article=self.artigo, name="Ana Silva", member=self.ana)
        self.client.post("/admin/website/article/", dados)
        self.assertFalse(Article.objects.get(pk=self.artigo.pk).published)  # ainda sem data

        Article.objects.filter(pk=self.artigo.pk).update(date=date(2026, 1, 5))
        self.client.post("/admin/website/article/", dados)
        self.assertTrue(Article.objects.get(pk=self.artigo.pk).published)

    def test_the_publish_action_skips_articles_without_author(self):
        com = Article.objects.create(title="Com", description="d", institutional=True)
        resposta = self.client.post(
            "/admin/website/article/", {"action": "publicar", "_selected_action": [self.artigo.pk, com.pk]}, follow=True,
        )

        self.assertContains(resposta, "1 artigo(s) publicado(s)")
        self.assertContains(resposta, "não foram publicados por não terem autor")
        self.assertFalse(Article.objects.get(pk=self.artigo.pk).published)
        self.assertTrue(Article.objects.get(pk=com.pk).published)

    def test_the_list_shows_the_authors_and_the_search_finds_by_author(self):
        ArticleAuthor.objects.create(article=self.artigo, name="Convidado {de Fora}", order=0)

        resposta = self.client.get("/admin/website/article/?q=convidado")

        self.assertContains(resposta, "Convidado de Fora")
        self.assertEqual(len(resposta.context["cl"].result_list), 1)

    def test_the_member_list_labels_only_homonyms_and_only_with_the_id(self):
        from website.admin import rotulos_dos_membros

        atual = Member.objects.create(name="Beto Souza")
        arquivado = Member.objects.create(name="beto  souza", is_active=False)
        outro = Member.objects.create(name="BETO SOUZA")
        unico = Member.objects.create(name="Carla Dias")

        rotulos = rotulos_dos_membros()

        self.assertEqual(rotulos[self.ana.pk], "Ana Silva")
        self.assertEqual(rotulos[unico.pk], "Carla Dias")
        self.assertEqual(rotulos[atual.pk], f"Beto Souza (ID {atual.pk})")
        self.assertEqual(rotulos[arquivado.pk], f"beto  souza (ID {arquivado.pk})")  # arquivado ou não, só o ID
        self.assertEqual(rotulos[outro.pk], f"BETO SOUZA (ID {outro.pk})")
        self.assertEqual(len(set(rotulos.values())), len(rotulos))  # nunca duas linhas iguais

    def test_the_member_list_shows_the_id_column(self):
        html = self.client.get("/admin/website/member/").content.decode()

        self.assertIn("column-id", html)
        self.assertRegex(html, rf'field-id[^>]*>{self.ana.pk}</td>')

    def test_the_member_form_has_the_citation_name_in_the_advanced_section(self):
        html = self.client.get(f"/admin/website/member/{self.ana.pk}/change/").content.decode()

        self.assertIn('name="citation_name"', html)
        self.assertGreater(html.index('name="citation_name"'), html.index("Avançado"))


@SEM_MANIFESTO
class ArticleEditingHelpTests(TestCase):
    """O que ajuda quem edita: o que falta para publicar, a data de hoje ao publicar e a prévia da citação."""

    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("root", "r@example.com", "senha-de-teste"))
        self.artigo = Article.objects.create(title="Varejo hoje", description="d", slug="varejo")
        self.url = f"/admin/website/article/{self.artigo.pk}/change/"

    def dados(self, **extra):
        dados = {
            "title": "Varejo hoje", "slug": "varejo", "description": "d", "order": "0", "institutional": "on",
            "date": "2026-01-05",
            "article_authors-TOTAL_FORMS": "0", "article_authors-INITIAL_FORMS": "0",
            "article_authors-MIN_NUM_FORMS": "0", "article_authors-MAX_NUM_FORMS": "1000",
            "images-TOTAL_FORMS": "0", "images-INITIAL_FORMS": "0", "images-MIN_NUM_FORMS": "0", "images-MAX_NUM_FORMS": "1000",
        }
        dados.update(extra)
        return dados

    def pagina(self):
        return self.client.get(self.url).content.decode()

    def test_the_publication_date_is_required_in_the_form(self):
        sem_data = self.client.post(self.url, self.dados(date=""))
        self.assertEqual(sem_data.status_code, 200)
        self.assertIn("Este campo é obrigatório", sem_data.content.decode())

        self.assertEqual(self.client.post(self.url, self.dados(date="2026-01-05", published="on")).status_code, 302)
        self.assertEqual(Article.objects.get(pk=self.artigo.pk).date, date(2026, 1, 5))

    def test_a_new_article_has_no_checklist_yet(self):
        html = self.client.get("/admin/website/article/add/").content.decode()

        self.assertIn("Salve o rascunho para ver aqui o que falta", html)

    def test_the_checklist_asks_for_an_author_and_suggests_a_cover(self):
        html = self.pagina()

        self.assertIn("Falta ao menos um autor", html)
        self.assertIn("Sem imagem de capa", html)

    def test_the_checklist_is_happy_when_nothing_is_missing(self):
        Article.objects.filter(pk=self.artigo.pk).update(institutional=True, image="news/capa.png")

        self.assertIn("Tudo pronto para publicar", self.pagina())

    def test_the_checklist_points_at_images_the_text_asks_for_but_were_not_sent(self):
        Article.objects.filter(pk=self.artigo.pk).update(
            institutional=True, image="news/capa.png", content="Texto\n\n![](imagem-1)\n\n![legenda](imagem-2)",
        )
        ArticleImage.objects.create(article=self.artigo, number=1, image="articles/a.png")

        html = self.pagina()

        self.assertIn("pede a imagem 2", html)
        self.assertNotIn("pede a imagem 1", html)

    @override_settings(FRONTEND_URL="https://exemplo.com.br")
    def test_the_citation_preview_needs_an_author_and_shows_the_citations_with_todays_access_date(self):
        self.assertIn("Adicione ao menos um autor", self.pagina())

        ArticleAuthor.objects.create(article=self.artigo, name="Maria da Silva", order=0)
        Article.objects.filter(pk=self.artigo.pk).update(date=date(2026, 3, 4))
        html = self.pagina()

        self.assertIn("SILVA, Maria da", html)
        self.assertIn("@misc", html)
        self.assertNotIn("__DATA_DE_ACESSO", html)
        self.assertIn(f"Acesso em: {timezone.localdate().day} ", html)


    def test_the_form_has_the_markdown_toolbar_and_the_insert_button_for_saved_images(self):
        ArticleImage.objects.create(article=self.artigo, number=1, image="articles/a.png")

        html = self.pagina()

        acoes = (
            "negrito", "italico", "codigo", "secao", "subsecao", "subsubsecao", "lista", "numerada", "citacao",
            "link", "bloco", "tabela", "tabela-inserir", "divisoria", "formula", "tela",
        )
        for acao in acoes:
            self.assertIn(f'data-md="{acao}"', html)
        self.assertRegex(html, r'class="md-tabela__colunas" min="1" max="8"')
        self.assertNotIn('data-md="titulo"', html)  # "título" é o do artigo, que tem campo próprio; o ## é uma seção
        self.assertIn('class="inserir-trecho copiar-trecho" data-trecho="![](imagem-1)"', html)

    def test_the_topics_field_suggests_the_topics_already_used_without_repeating_spelling(self):
        import json

        Article.objects.create(title="B", description="d", slug="b", topics="Varejo, Estratégia")
        Article.objects.create(title="C", description="d", slug="c", topics="varejo, Carreira")
        Article.objects.create(title="D", description="d", slug="d", topics="Varejo")

        html = self.pagina()
        lista = html[html.index('data-temas="') + len('data-temas="'):]
        temas = json.loads(lista[:lista.index('"')].replace("&quot;", '"'))

        self.assertEqual(temas, ["Varejo", "Carreira", "Estratégia"])  # a grafia mais usada, do mais ao menos comum
        self.assertIn("temas-sugestoes__input", html)

    def test_the_unsaved_changes_warning_is_loaded_in_the_admin(self):
        self.assertIn("website/avisa_alteracoes.js", self.pagina())


    def test_the_image_list_shows_a_thumbnail_and_whether_the_text_uses_each_image(self):
        Article.objects.filter(pk=self.artigo.pk).update(institutional=True, content="Texto\n\n![](imagem-1)")
        ArticleImage.objects.create(article=self.artigo, number=1, image="articles/a.png")
        ArticleImage.objects.create(article=self.artigo, number=2, image="articles/b.png")

        html = self.pagina()

        self.assertIn("Usada no texto", html)
        self.assertIn("Ainda não usada no texto", html)
        self.assertIn('src="/media/articles/a.png"', html)

    def test_the_toolbar_has_the_image_picker_with_the_saved_images_and_the_save_button_for_full_screen(self):
        ArticleImage.objects.create(article=self.artigo, number=1, image="articles/a.png", caption="Gráfico")

        html = self.pagina()

        self.assertIn('data-md="imagem"', html)
        self.assertIn('class="md-imagens"', html)
        self.assertIn("&quot;number&quot;: 1", html[html.index('class="md-imagens"'):][:400])
        self.assertIn('data-md="salvar"', html)

    def test_the_list_filters_by_author_and_by_topic(self):
        ana = Member.objects.create(name="Ana Silva")
        outra = Article.objects.create(title="Outro", description="d", slug="outro", topics="varejo, Carreira")
        ArticleAuthor.objects.create(article=self.artigo, name="Ana Silva", member=ana)
        ArticleAuthor.objects.create(article=outra, name="Fulano {de Tal}")
        Article.objects.filter(pk=self.artigo.pk).update(topics="Varejo, Estratégia")
        resultado = lambda consulta: {a.pk for a in self.client.get(f"/admin/website/article/?{consulta}").context["cl"].result_list}  # noqa: E731

        self.assertEqual(resultado(f"autor=m{ana.pk}"), {self.artigo.pk})
        self.assertEqual(resultado("autor=nfulano+de+tal"), {outra.pk})
        self.assertEqual(resultado("tema=varejo"), {self.artigo.pk, outra.pk})  # "Varejo" e "varejo" são o mesmo tema
        self.assertEqual(resultado("tema=carreira"), {outra.pk})
        self.assertEqual(resultado("tema=estrategia"), {self.artigo.pk})

    def test_the_author_filter_lists_members_outsiders_and_the_institutional_option(self):
        ana = Member.objects.create(name="Ana Silva")
        ArticleAuthor.objects.create(article=self.artigo, name="Ana Silva", member=ana)
        ArticleAuthor.objects.create(article=self.artigo, name="Fulano {de Tal}")
        Article.objects.create(title="Inst", description="d", slug="inst", institutional=True)

        html = self.client.get("/admin/website/article/").content.decode()

        for texto in ("Ana Silva", "Fulano de Tal", "Insper Consulting Club (institucional)"):
            self.assertIn(texto, html)


class ArticleAuthorsMigrationTests(TransactionTestCase):
    """Migration 0032: o texto dos autores vira uma linha por autor, e o caminho de volta funciona."""

    ANTES = ("website", "0031_secoes_da_home")
    DEPOIS = ("website", "0032_autores_dos_artigos")

    def _estado(self, alvo):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        MigrationExecutor(connection).migrate([alvo])
        return MigrationExecutor(connection).loader.project_state([alvo]).apps

    def tearDown(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_authors_text_becomes_rows_linked_to_members_when_the_name_matches(self):
        antigo = self._estado(self.ANTES)
        Member, Article = antigo.get_model("website", "Member"), antigo.get_model("website", "Article")
        ana = Member.objects.create(name="Ana Silva")
        joao = Member.objects.create(name="Joao Souza")
        Member.objects.create(name="Dup Lo")
        Member.objects.create(name="dup lo")
        artigo = Article.objects.create(
            title="T", description="d", authors="Ana Silva, João Souza ,Fulano de Tal, Dup Lo", link="https://x.com", source="Rev",
        )

        novo = self._estado(self.DEPOIS)
        autores = list(novo.get_model("website", "ArticleAuthor").objects.filter(article_id=artigo.pk).order_by("order"))

        self.assertEqual([a.name for a in autores], ["Ana Silva", "João Souza", "Fulano de Tal", "Dup Lo"])
        self.assertEqual([a.member_id for a in autores], [ana.pk, joao.pk, None, None])  # o homônimo não é adivinhado
        self.assertEqual([a.order for a in autores], [0, 1, 2, 3])
        self.assertFalse(hasattr(novo.get_model("website", "Article"), "link"))

    def test_undoing_rebuilds_the_authors_text_without_braces(self):
        novo = self._estado(self.DEPOIS)
        Article, ArticleAuthor = novo.get_model("website", "Article"), novo.get_model("website", "ArticleAuthor")
        artigo = Article.objects.create(title="T", description="d")
        ArticleAuthor.objects.create(article=artigo, name="Robert {Lucas Jr}", order=1)
        ArticleAuthor.objects.create(article=artigo, name="Ana Silva", order=0)
        institucional = Article.objects.create(title="I", description="d", institutional=True)

        antigo = self._estado(self.ANTES)
        Article = antigo.get_model("website", "Article")

        self.assertEqual(Article.objects.get(title="T").authors, "Ana Silva, Robert Lucas Jr")
        self.assertEqual(Article.objects.get(pk=institucional.pk).authors, "Insper Consulting Club")
        self.assertEqual(Article.objects.get(title="T").link, "")


class CitationTests(TestCase):
    """As referências em BibTeX e em BibLaTeX."""

    def artigo(self, titulo="Precificação dinâmica no varejo", autores=("Maria da Silva",), **dados):
        dados.setdefault("date", date(2026, 3, 12))
        dados.setdefault("slug", "precificacao")
        artigo = Article.objects.create(title=titulo, description="d", published=True, **dados)
        for ordem, nome in enumerate(autores):
            ArticleAuthor.objects.create(article=artigo, name=nome, order=ordem)
        return Article.objects.prefetch_related("article_authors").get(pk=artigo.pk)

    # --- o sobrenome (só serve para a chave)

    def test_surname_follows_the_bibtex_rules(self):
        from website.citacao import sobrenome_bibtex

        casos = {
            "Maria da Silva": "Silva",
            "Maria da Silva Lima": "Silva Lima",
            "Robert {Lucas Jr}": "Lucas Jr",
            "{Maria Clara} {Souza Lima}": "Souza Lima",
            "Lucas, Jr., Robert": "Lucas",
            "Silva Lima, Maria": "Silva Lima",
            "da Silva, Maria": "Silva",
            "Ana Paula Souza Lima": "Lima",
            "Ana de la Fuente": "Fuente",
            "Madonna": "Madonna",
        }
        for nome, esperado in casos.items():
            self.assertEqual(sobrenome_bibtex(nome), esperado, nome)

    # --- a chave

    def test_key_is_the_first_authors_surname_the_year_and_the_first_meaningful_title_word(self):
        from website.citacao import chave_da_citacao

        self.assertEqual(chave_da_citacao(self.artigo()), "silva2026precificacao")
        self.assertEqual(chave_da_citacao(self.artigo("Uma análise: o que é Estratégia?", ["Robert {Lucas Jr}"], slug="x")), "lucasjr2026analise")
        self.assertEqual(chave_da_citacao(self.artigo("Ação e reação", ["José Ávila"], slug="y")), "avila2026acao")
        self.assertEqual(chave_da_citacao(self.artigo("100% de ganho com precificação", ["Ana Souza"], slug="n")), "souza2026ganho")  # número não serve

    def test_institutional_article_and_article_without_a_date(self):
        from website.citacao import chave_da_citacao

        self.assertEqual(chave_da_citacao(self.artigo(institutional=True, autores=(), slug="i")), "icc2026precificacao")
        self.assertEqual(chave_da_citacao(self.artigo(autores=["Ana Souza"], date=None, slug="sd")), "souzaprecificacao")

    def test_key_has_only_ascii_letters_and_digits(self):
        import re
        from website.citacao import chave_da_citacao

        chave = chave_da_citacao(self.artigo("¿Çürioso & _novo?", ["Zoë D’Ávila-Pérez"], slug="z"))

        self.assertRegex(chave, r"^[a-z0-9]+$")

    # --- escape

    def test_title_special_characters_are_escaped_in_one_pass(self):
        from website.citacao import escapa_latex

        self.assertEqual(escapa_latex("R&D 100% a_b #1 $5"), r"R\&D 100\% a\_b \#1 \$5")
        self.assertEqual(escapa_latex("{x} ~ ^"), r"\{x\} \textasciitilde{} \textasciicircum{}")
        self.assertEqual(escapa_latex("a\\b"), r"a\textbackslash{}b")  # as chaves que o escape cria não são escapadas de novo

    # --- as entradas

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_biblatex_entry(self):
        from website.citacao import biblatex

        artigo = self.artigo("Preço & valor", ["Maria da Silva", "Robert {Lucas Jr}"])

        self.assertEqual(biblatex(artigo), (
            "@online{silva2026preco,\n"
            "  author       = {Maria da Silva and Robert {Lucas Jr}},\n"
            "  title        = {Preço \\& valor},\n"
            "  organization = {Insper Consulting Club},\n"
            "  date         = {2026-03-12},\n"
            "  url          = {https://icc.example.com/artigos/precificacao},\n"
            "  urldate      = {__DATA_DE_ACESSO__},\n"
            "  langid       = {brazilian},\n"
            "}"
        ))

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_bibtex_entry(self):
        from website.citacao import bibtex

        artigo = self.artigo("PMEs e tecnologia", ["Maria da Silva"])

        self.assertEqual(bibtex(artigo), (
            "@misc{silva2026pmes,\n"
            "  author       = {Maria da Silva},\n"
            "  title        = {{PMEs e tecnologia}},\n"
            "  organization = {Insper Consulting Club},\n"
            "  year         = {2026},\n"
            "  month        = mar,\n"
            "  howpublished = {\\url{https://icc.example.com/artigos/precificacao}},\n"
            "  note         = {Acesso em: __DATA_DE_ACESSO__},\n"
            "}"
        ))

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_institutional_author_uses_double_braces_so_it_is_not_split_into_a_surname(self):
        from website.citacao import biblatex, bibtex

        artigo = self.artigo(institutional=True, autores=(), slug="i")

        for texto in (biblatex(artigo), bibtex(artigo)):
            self.assertIn("author       = {{Insper Consulting Club}},", texto)

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_an_article_without_authors_or_date_still_produces_a_valid_entry(self):
        from website.citacao import biblatex, bibtex

        artigo = self.artigo(autores=(), date=None, slug="r")

        self.assertIn("{{Insper Consulting Club}}", biblatex(artigo))
        self.assertNotRegex(biblatex(artigo), r"\n  date ")
        self.assertNotRegex(bibtex(artigo), r"\n  year ")
        self.assertNotRegex(bibtex(artigo), r"\n  month ")

    @override_settings(FRONTEND_URL="")
    def test_without_the_site_address_the_url_and_access_date_are_left_out(self):
        from website.citacao import biblatex, bibtex

        artigo = self.artigo()

        for texto in (biblatex(artigo), bibtex(artigo)):
            self.assertNotIn("url", texto.replace("urldate", "url"))
            self.assertNotIn("DATA_DE_ACESSO", texto)

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_a_slugless_article_is_cited_by_its_id(self):
        from website.citacao import biblatex

        artigo = self.artigo(slug=None)

        self.assertIn(f"https://icc.example.com/artigos/{artigo.pk}", biblatex(artigo))

    # --- nomes

    def test_names_are_split_the_way_bibtex_reads_them(self):
        from website.citacao import analisa_nome

        casos = {
            "Maria da Silva": ("Maria", "da", "Silva", ""),
            "Maria da Silva Lima": ("Maria", "da", "Silva Lima", ""),
            "Ana Paula Souza Lima": ("Ana Paula Souza", "", "Lima", ""),
            "Robert {Lucas Jr}": ("Robert", "", "Lucas Jr", ""),
            "{Maria Clara} {Souza Lima}": ("Maria Clara", "", "Souza Lima", ""),
            "Lucas, Jr., Robert": ("Robert", "", "Lucas", "Jr."),
            "da Silva, Maria": ("Maria", "da", "Silva", ""),
            "Ludwig van Beethoven": ("Ludwig", "van", "Beethoven", ""),
            "Madonna": ("", "", "Madonna", ""),
        }
        for nome, (primeiro, von, sobrenome, sufixo) in casos.items():
            analisado = analisa_nome(nome)
            self.assertEqual((analisado.nome, analisado.von, analisado.sobrenome, analisado.sufixo), (primeiro, von, sobrenome, sufixo), nome)

    # --- ABNT e APA: o texto que o biblatex-abnt e o biblatex-apa imprimem para as mesmas entradas

    URL = "https://icc.example.com/artigos/"

    def amostra(self, slug):
        casos = {
            "um": ("Precificação dinâmica no varejo brasileiro: um estudo de caso", ["Maria da Silva"], False, date(2026, 3, 12)),
            "dois": ("Preço e valor", ["Maria da Silva", "Robert {Lucas Jr}"], False, date(2026, 3, 12)),
            "quatro": ("Como escolher a ferramenta certa para priorizar projetos",
                       ["Ana Paula Souza Lima", "Beto Souza", "Carla Dias", "Davi Nunes"], False, date(2026, 5, 20)),
            "inst": ("Relatório anual do clube", [], True, date(2026, 6, 2)),
            "semdata": ("Texto sem data de publicação", ["Maria da Silva"], False, None),
        }
        titulo, autores, institucional, data = casos[slug]
        return self.artigo(titulo, autores, slug=slug, date=data, institutional=institucional)

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_abnt_matches_what_biblatex_abnt_prints(self):
        from website.citacao import abnt

        esperado = {
            "um": "SILVA, Maria da. Precificação dinâmica no varejo brasileiro: um estudo de caso. Insper Consulting Club. 12 mar. 2026.",
            "dois": "SILVA, Maria da; LUCAS JR, Robert. Preço e valor. Insper Consulting Club. 12 mar. 2026.",
            "quatro": "LIMA, Ana Paula Souza et al. Como escolher a ferramenta certa para priorizar projetos. Insper Consulting Club. 20 maio 2026.",
            "inst": "INSPER CONSULTING CLUB. Relatório anual do clube. Insper Consulting Club. 2 jun. 2026.",
            "semdata": "SILVA, Maria da. Texto sem data de publicação. Insper Consulting Club.",
        }
        for slug, inicio in esperado.items():
            self.assertEqual(
                abnt(self.amostra(slug))["texto"],
                f"{inicio} Disponível em: {self.URL}{slug}. Acesso em: __DATA_DE_ACESSO_ABNT__.", slug,
            )

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_abnt_puts_the_title_in_bold_and_et_al_in_italic(self):
        from website.citacao import abnt

        citacao = abnt(self.amostra("quatro"))
        partes = citacao["partes"]

        self.assertEqual([p["t"] for p in partes if p["e"] == "b"], ["Como escolher a ferramenta certa para priorizar projetos."])
        self.assertEqual([p["t"] for p in partes if p["e"] == "i"], ["et al"])
        self.assertEqual("".join(p["t"] for p in partes), citacao["texto"])

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_apa_matches_biblatex_apa_except_for_two_deliberate_differences(self):
        from website.citacao import apa

        # Diferenças: a data sai "12 de março" (o biblatex-apa imprime "março 12", ordem do inglês) e o nome do site não
        # se repete quando o autor é o próprio clube (o que a APA 7 pede; o biblatex-apa repete). Sem data de acesso:
        # a APA só a pede em páginas que mudam, e o biblatex-apa só a imprime quando a entrada tem urldate.
        esperado = {
            "um": "da Silva, M. (2026, 12 de março). Precificação dinâmica no varejo brasileiro: um estudo de caso. Insper Consulting Club.",
            "dois": "da Silva, M., & Lucas Jr, R. (2026, 12 de março). Preço e valor. Insper Consulting Club.",
            "quatro": "Lima, A. P. S., Souza, B., Dias, C., & Nunes, D. (2026, 20 de maio). Como escolher a ferramenta certa para priorizar projetos. Insper Consulting Club.",
            "inst": "Insper Consulting Club. (2026, 2 de junho). Relatório anual do clube.",
            "semdata": "da Silva, M. (s.d.). Texto sem data de publicação. Insper Consulting Club.",
        }
        for slug, inicio in esperado.items():
            self.assertEqual(apa(self.amostra(slug))["texto"], f"{inicio} {self.URL}{slug}", slug)

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_apa_puts_only_the_title_in_italic(self):
        from website.citacao import apa

        partes = apa(self.amostra("um"))["partes"]

        self.assertEqual([p["t"] for p in partes if p["e"]], ["Precificação dinâmica no varejo brasileiro: um estudo de caso."])

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_a_title_that_ends_in_punctuation_does_not_get_a_second_period(self):
        from website.citacao import abnt, apa

        artigo = self.artigo("Vale a pena?", ["Ana Souza"], slug="p")

        self.assertIn("Vale a pena? Insper Consulting Club.", abnt(artigo)["texto"])
        self.assertIn("Vale a pena? Insper Consulting Club.", apa(artigo)["texto"])

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_apa_initials_keep_the_hyphen_of_compound_first_names(self):
        from website.citacao import apa

        artigo = self.artigo("T", ["Jean-Paul Sartre"], slug="s")

        self.assertTrue(apa(artigo)["texto"].startswith("Sartre, J.-P. ("))

    @override_settings(FRONTEND_URL="")
    def test_text_citations_leave_out_the_address_and_access_date_without_the_site_address(self):
        from website.citacao import abnt, apa

        artigo = self.artigo()

        self.assertNotIn("Disponível", abnt(artigo)["texto"])
        self.assertNotIn("http", apa(artigo)["texto"])

    # --- RIS

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_ris_entry(self):
        from website.citacao import ris

        self.assertEqual(ris(self.amostra("dois")), (
            "TY  - ELEC\n"
            "AU  - da Silva, Maria\n"
            "AU  - Lucas Jr, Robert\n"
            "TI  - Preço e valor\n"
            "PB  - Insper Consulting Club\n"
            "PY  - 2026\n"
            "DA  - 2026/03/12\n"
            "UR  - https://icc.example.com/artigos/dois\n"
            "Y2  - __DATA_DE_ACESSO_RIS__\n"
            "LA  - pt\n"
            "ER  - \n"
        ))
        self.assertIn("AU  - Insper Consulting Club\n", ris(self.amostra("inst")))

    # --- API

    @override_settings(FRONTEND_URL="https://icc.example.com")
    def test_the_detail_has_the_five_citations_in_order_and_the_list_does_not(self):
        artigo = self.artigo()

        detalhe = APIClient().get(f"/api/articles/{artigo.slug}/").data
        lista = APIClient().get("/api/articles/").data[0]

        self.assertEqual([c["id"] for c in detalhe["citations"]], ["abnt", "apa", "bibtex", "biblatex", "ris"])
        self.assertEqual([c["kind"] for c in detalhe["citations"]], ["texto", "texto", "codigo", "codigo", "codigo"])
        self.assertTrue(detalhe["citations"][2]["texto"].startswith("@misc{silva2026precificacao,"))
        self.assertTrue(detalhe["citations"][3]["texto"].startswith("@online{silva2026precificacao,"))
        self.assertNotIn("citations", lista)
        self.assertNotIn("bibtex", detalhe)
