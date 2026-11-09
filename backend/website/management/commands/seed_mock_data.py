import io
import textwrap
import unicodedata
import zlib

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from website.models import (
    Article, ArticleAuthor, ArticleImage, Directorate, DirectorateMembership, Member, MemberTrajectory, NavItem,
    Partner, PartnerCategory, Position, PreparationMaterial, PreparationMaterialItem, Program,
    ProgramCase, ProgramCaseParticipant, ProgramComponent, ProgramContentBlock, Project,
    ProjectContentBlock, ProjectImage, ProjectTimelineEvent, SelectionProcess,
    SelectionProcessRequirement, SelectionProcessStage, SelectionProcessStep, SiteConfig, Statistic,
)

from ._dados_de_exemplo import (
    ARTIGOS, CASES, CATEGORIAS_DE_PARCEIROS, DIRETORIAS, ESTATISTICAS, ITENS_DE_MENU, MEMBROS,
    PARCEIROS, POSICOES, PROCESSOS, PROGRAMAS, PROJETOS,
)

# Tons da marca e variações, para os placeholders não ficarem todos da mesma cor.
PALETA = [(120, 18, 28), (30, 64, 110), (30, 110, 82), (96, 30, 110), (110, 94, 30), (60, 60, 70), (150, 60, 30)]


def placeholder(texto, tamanho, cor, iniciais=False):
    """Imagem PNG de exemplo: fundo colorido com o texto no centro (ou as iniciais, nas fotos)."""
    # A fonte embutida do Pillow não tem os glifos acentuados (apareceriam como quadrados).
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    largura, altura = tamanho
    imagem = Image.new("RGB", tamanho, cor)
    desenho = ImageDraw.Draw(imagem)
    claro = tuple(min(255, c + 45) for c in cor)
    desenho.rectangle([0, altura * 2 // 3, largura, altura], fill=claro)
    if iniciais:
        partes = [p for p in texto.split() if p[0].isalpha()]
        texto = "".join(p[0] for p in (partes[:1] + partes[-1:])).upper()
        fonte = ImageFont.load_default(size=max(24, largura // 3))
    else:
        texto = "\n".join(textwrap.wrap(texto, width=max(10, largura // 22)))
        fonte = ImageFont.load_default(size=max(14, largura // 20))
    desenho.multiline_text((largura / 2, altura / 2), texto, fill="white", font=fonte, anchor="mm", align="center")
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = (
        "Popula o banco local com dados de exemplo fictícios que cobrem todas as telas do site e do admin, "
        "inclusive rascunhos, itens ocultos, campos vazios e textos longos. Pode ser repetido: atualiza os "
        "registros de exemplo sem duplicá-los. Para recomeçar do zero, use `docker compose down -v`."
    )

    def handle(self, *args, **options):
        # Dados fictícios e imagens geradas: nunca em produção.
        if not settings.DEBUG:
            raise CommandError("seed_mock_data só roda em ambiente local (DEBUG=True).")

        # Com Cloudinary configurado, as imagens de exemplo iriam para o ambiente compartilhado.
        self.com_imagens = isinstance(default_storage, FileSystemStorage)
        if not self.com_imagens:
            self.stdout.write(self.style.WARNING("Armazenamento remoto detectado: as imagens de exemplo foram ignoradas."))

        posicoes = self._posicoes()
        diretorias = self._diretorias()
        membros = self._membros(posicoes, diretorias)
        parceiros = self._parceiros()
        programas = self._programas()
        self._estatisticas()
        projetos = self._projetos(programas, parceiros, membros)
        self._cases(programas, membros)
        artigos = self._artigos()
        self._processos()
        self._itens_de_menu()

        self.stdout.write(self.style.SUCCESS(
            f"Dados de exemplo prontos: {len(membros)} membros, {len(parceiros)} parceiros, {len(programas)} programas, "
            f"{len(projetos)} projetos, {len(artigos)} artigos e {len(PROCESSOS)} processos seletivos."
        ))

    # ------------------------------------------------------------------ ajudantes

    def _anexar(self, instancia, campo, rotulo, tamanho, iniciais=False, texto=None):
        """
        Gera e anexa a imagem de exemplo. O nome do arquivo é sempre o mesmo para o mesmo
        rótulo, e o arquivo anterior é substituído, então repetir o comando não acumula
        arquivos em disco. O rótulo identifica o arquivo (por isso inclui o dono); o texto
        escrito na imagem é só o que interessa ver, e por padrão é o próprio rótulo.
        """
        if not self.com_imagens:
            return
        cor = PALETA[zlib.crc32(rotulo.encode()) % len(PALETA)]
        nome = f"mock-{slugify(rotulo)[:70]}.png"
        arquivo = getattr(instancia, campo)
        caminho = arquivo.field.generate_filename(instancia, nome)
        if arquivo.storage.exists(caminho):
            arquivo.storage.delete(caminho)
        arquivo.save(nome, placeholder(texto or rotulo, tamanho, cor, iniciais), save=False)
        instancia.save(update_fields=[campo])

    def _sem_imagem(self, instancia, campo, vazio=None):
        """Deixa o campo de imagem vazio (caso de borda "sem foto")."""
        if getattr(instancia, campo):
            setattr(instancia, campo, vazio)
            instancia.save(update_fields=[campo])

    @staticmethod
    def _manter(queryset, ids):
        """Apaga os filhos que o seed não descreve mais, para o resultado bater com os dados."""
        queryset.exclude(pk__in=ids).delete()

    # ------------------------------------------------------------------ equipe

    def _posicoes(self):
        return {
            titulo: Position.objects.update_or_create(title=titulo, defaults={"power": poder})[0]
            for titulo, poder in POSICOES
        }

    def _diretorias(self):
        return {
            nome: Directorate.objects.update_or_create(name=nome, defaults={"order": ordem})[0]
            for nome, ordem in DIRETORIAS
        }

    def _membros(self, posicoes, diretorias):
        membros = {}
        for item in MEMBROS:
            slug = slugify(item["nome"])
            membro, _ = Member.objects.update_or_create(
                name=item["nome"],
                defaults={
                    "position": posicoes[item["cargo"]],
                    "is_active": item.get("ativo", True),
                    "linkedin": f"https://example.com/linkedin/{slug}" if item["contato"] else None,
                },
            )
            if item["foto"]:
                self._anexar(membro, "photo", item["nome"], (600, 600), iniciais=True)
            else:
                self._sem_imagem(membro, "photo")

            ids = [
                DirectorateMembership.objects.update_or_create(
                    member=membro, directorate=diretorias[diretoria], defaults={"cargo": cargo, "order": ordem},
                )[0].pk
                for ordem, (diretoria, cargo) in enumerate(item["vinculos"], start=1)
            ]
            self._manter(membro.directorate_memberships, ids)

            ids = [
                MemberTrajectory.objects.get_or_create(member=membro, semester=semestre, role=cargo)[0].pk
                for semestre, cargo in item["trajetoria"]
            ]
            self._manter(membro.trajectory_steps, ids)

            membros[item["nome"]] = membro
        return membros

    # ------------------------------------------------------------------ parceiros

    def _parceiros(self):
        categorias = {titulo: PartnerCategory.objects.get_or_create(title=titulo)[0] for titulo in CATEGORIAS_DE_PARCEIROS}
        parceiros = {}
        for item in PARCEIROS:
            parceiro, _ = Partner.objects.update_or_create(
                name=item["nome"],
                defaults={
                    "description": item["descricao"],
                    "category": categorias[item["categoria"]],
                    "site": item["site"] or None,
                    "is_active": item.get("ativo", True),
                    "order": item["ordem"],
                },
            )
            if item["logo"]:
                self._anexar(parceiro, "logo_url", item["nome"], (400, 240))
            else:
                self._sem_imagem(parceiro, "logo_url", vazio="")
            parceiros[item["nome"]] = parceiro
        return parceiros

    # ------------------------------------------------------------------ programas

    def _programas(self):
        programas = {}
        for item in PROGRAMAS:
            programa, _ = Program.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "label": item["nome"],
                    "subtitle": item["subtitulo"],
                    "description": item["descricao"],
                    "highlights": item["topicos"],
                    "signup_url": item["inscricao"],
                    "is_active": item.get("ativo", True),
                    "order": item["ordem"],
                },
            )
            if item.get("icone"):
                self._anexar(programa, "icon", item["nome"], (256, 256))
            else:
                self._sem_imagem(programa, "icon")

            ids = [
                ProgramComponent.objects.update_or_create(program=programa, title=titulo, defaults={"description": descricao})[0].pk
                for titulo, descricao in item["componentes"]
            ]
            self._manter(programa.components, ids)

            ids = []
            for ordem, (titulo, texto, posicao, legenda) in enumerate(item["blocos"], start=1):
                bloco, _ = ProgramContentBlock.objects.update_or_create(
                    program=programa, order=ordem,
                    defaults={"title": titulo, "text": texto, "image_align": posicao, "image_caption": legenda or ""},
                )
                if legenda:
                    self._anexar(bloco, "image", f"{item['nome']} {legenda}", (900, 560), texto=legenda)
                else:
                    self._sem_imagem(bloco, "image")
                ids.append(bloco.pk)
            self._manter(programa.content_blocks, ids)

            programas[item["slug"]] = programa
        return programas

    def _estatisticas(self):
        for valor, descricao, ordem in ESTATISTICAS:
            Statistic.objects.update_or_create(description=descricao, defaults={"value": valor, "order": ordem})

    # ------------------------------------------------------------------ projetos e cases

    def _projetos(self, programas, parceiros, membros):
        projetos = {}
        for item in PROJETOS:
            projeto, _ = Project.objects.update_or_create(
                title=item["titulo"],
                defaults={
                    "description": item["descricao"],
                    "program": programas[item["programa"]] if item["programa"] else None,
                    "start_date": item["inicio"],
                    "end_date": item["fim"],
                    "is_active": item.get("ativo", True),
                },
            )
            projeto.partners.set([parceiros[nome] for nome in item["parceiros"]])
            projeto.members.set([membros[nome] for nome in item["membros"]])

            # A imagem da galeria é obrigatória: sem armazenamento local, a galeria fica vazia.
            ids = []
            if self.com_imagens:
                for ordem, legenda in enumerate(item["imagens"], start=1):
                    foto, _ = ProjectImage.objects.update_or_create(project=projeto, order=ordem, defaults={"caption": legenda})
                    self._anexar(foto, "image", f"{item['titulo']} {legenda}", (1000, 600), texto=legenda)
                    ids.append(foto.pk)
            self._manter(projeto.images, ids)

            ids = [
                ProjectTimelineEvent.objects.update_or_create(
                    project=projeto, title=titulo, defaults={"date": data, "description": descricao, "order": ordem},
                )[0].pk
                for data, titulo, descricao, ordem in item["eventos"]
            ]
            self._manter(projeto.timeline_events, ids)

            ids = []
            for ordem, (titulo, texto, posicao, legenda) in enumerate(item["blocos"], start=1):
                bloco, _ = ProjectContentBlock.objects.update_or_create(
                    project=projeto, order=ordem,
                    defaults={"title": titulo, "text": texto, "image_align": posicao, "image_caption": legenda or ""},
                )
                if legenda:
                    self._anexar(bloco, "image", f"{item['titulo']} {legenda}", (900, 560), texto=legenda)
                else:
                    self._sem_imagem(bloco, "image")
                ids.append(bloco.pk)
            self._manter(projeto.content_blocks, ids)

            projetos[item["titulo"]] = projeto
        return projetos

    def _cases(self, programas, membros):
        for item in CASES:
            caso, _ = ProgramCase.objects.update_or_create(
                program=programas[item["programa"]], semester=item["semestre"], title=item["titulo"],
                defaults={
                    "area": item["area"], "theme": item["tema"], "panel": item["banca"], "award": item["premiacao"],
                    "publication_url": item["link"], "is_active": item.get("ativo", True), "order": item["ordem"],
                },
            )
            ids = [
                ProgramCaseParticipant.objects.update_or_create(
                    case=caso, member=membros[nome], defaults={"role": papel, "order": ordem},
                )[0].pk
                for nome, papel, ordem in item["participantes"]
            ]
            self._manter(caso.participants, ids)

    # ------------------------------------------------------------------ artigos

    def _artigos(self):
        artigos = []
        for item in ARTIGOS:
            artigo, _ = Article.objects.update_or_create(
                title=item["titulo"],
                defaults={
                    "slug": item["slug"] or None,
                    "institutional": item.get("institucional", False),
                    "topics": item["temas"],
                    "description": item["resumo"],
                    "content": item["conteudo"],
                    "date": item["data"],
                    "order": item["ordem"],
                    "published": item["publicado"],
                },
            )
            # Os autores: o nome que bate com um membro fica vinculado a ele, como no admin.
            artigo.article_authors.all().delete()
            for ordem, nome in enumerate(item["autores"]):
                autor = ArticleAuthor(article=artigo, name=nome, order=ordem)
                autor.clean()
                autor.save()
            if item["capa"]:
                self._anexar(artigo, "image", item["titulo"], (1200, 630))
            else:
                self._sem_imagem(artigo, "image")

            # A imagem do texto é obrigatória: sem armazenamento local, o ![](imagem-N) é omitido pelo site.
            ids = []
            if self.com_imagens:
                for numero, legenda in enumerate(item["imagens"], start=1):
                    figura, _ = ArticleImage.objects.update_or_create(article=artigo, number=numero, defaults={"caption": legenda})
                    self._anexar(figura, "image", f"{item['titulo']} {legenda}", (1000, 600), texto=legenda)
                    ids.append(figura.pk)
            self._manter(artigo.images, ids)
            artigos.append(artigo)
        return artigos

    # ------------------------------------------------------------------ processo seletivo

    def _processos(self):
        # O antigo vem primeiro: ativar o seguinte desativa os demais.
        for item in PROCESSOS:
            processo, _ = SelectionProcess.objects.update_or_create(
                title=item["titulo"],
                defaults={"is_active": item["ativo"], "registrations_open": item["abertas"], "registration_url": item["link"]},
            )
            ids = [
                SelectionProcessStage.objects.update_or_create(process=processo, label=nome, defaults={"date": data, "order": ordem})[0].pk
                for nome, data, ordem in item["datas"]
            ]
            self._manter(processo.stages, ids)

            ids = []
            for numero, titulo, descricao, duracao, dicas, ordem, icone in item["etapas"]:
                etapa, _ = SelectionProcessStep.objects.update_or_create(
                    process=processo, number=numero,
                    defaults={"title": titulo, "description": descricao, "duration": duracao, "tips": dicas, "order": ordem},
                )
                if icone:
                    self._anexar(etapa, "image", f"{item['titulo']} {titulo}", (256, 256), texto=titulo)
                else:
                    self._sem_imagem(etapa, "image")
                ids.append(etapa.pk)
            self._manter(processo.steps, ids)

            ids = []
            for texto, ordem, icone in item["requisitos"]:
                requisito, _ = SelectionProcessRequirement.objects.update_or_create(
                    process=processo, text=texto, defaults={"order": ordem},
                )
                if icone:
                    self._anexar(requisito, "icon", f"{item['titulo']} requisito {ordem}", (128, 128), texto=f"Req. {ordem}")
                else:
                    self._sem_imagem(requisito, "icon")
                ids.append(requisito.pk)
            self._manter(processo.requirements, ids)

            ids = []
            for titulo, itens, ordem in item["materiais"]:
                material, _ = PreparationMaterial.objects.update_or_create(process=processo, title=titulo, defaults={"order": ordem})
                itens_ids = [
                    PreparationMaterialItem.objects.update_or_create(material=material, text=texto, defaults={"order": posicao})[0].pk
                    for posicao, texto in enumerate(itens, start=1)
                ]
                self._manter(material.items, itens_ids)
                ids.append(material.pk)
            self._manter(processo.materials, ids)

    # ------------------------------------------------------------------ menu

    def _itens_de_menu(self):
        # Os itens padrão do menu vêm da migration e não são tocados: só se acrescentam
        # exemplos (um link externo só no rodapé e um item inativo).
        configuracao = SiteConfig.get_solo()
        for item in ITENS_DE_MENU:
            NavItem.objects.update_or_create(
                site_config=configuracao, label=item["texto"], area=item["area"],
                defaults={"page": "", "url": item["url"], "order": item["ordem"], "is_active": item["ativo"]},
            )
