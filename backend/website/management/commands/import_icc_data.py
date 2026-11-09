import json
import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from website.models import (
    ProgramComponent,
    Program,
    Directorate,
    DirectorateMembership,
    Position,
    Partner,
    PartnerCategory,
    ProgramCase,
    ProgramCaseParticipant,
    Member,
)

# A pasta site-data fica na raiz do repositório e não é versionada (tem dados
# pessoais dos membros). No Docker ela é montada em /site-data, que é o mesmo
# BASE_DIR.parent / "site-data" visto de dentro do container.
DEFAULT_DIR = Path(settings.BASE_DIR).parent / "site-data"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".svg")

# Programa ao qual os cases do icc.json pertencem; é o mesmo slug que o
# frontend usa no link "Ver os cases" da página de Projetos.
CASES_PROGRAM = "Jornada do Consultor"


def _power(cargo):
    """
    Prioridade de exibição do cargo (ver Position.power). A Home mostra
    como liderança quem tem prioridade até 2. Só é usada ao criar o cargo: se
    o admin mudar depois, a importação não sobrescreve.
    """
    cargo = cargo.lower()
    if cargo.startswith("presidente"):
        return 0
    if cargo.startswith("vice"):
        return 1
    if cargo.startswith("diretor"):
        return 2
    if cargo.startswith("coordenador"):
        return 3
    if cargo.startswith("trainee"):
        return 5
    return 4


def _find_image(folder, slug):
    """
    Procura a imagem pelo id/slug: 'bain' casa com 'bain-company', para que os
    arquivos possam ter nomes curtos sem depender do nome completo da empresa.
    """
    if not folder.is_dir():
        return None
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if path.stem.startswith("placeholder"):
            continue
        if slug == path.stem or slug.startswith(path.stem + "-"):
            return path
    return None


class Command(BaseCommand):
    help = (
        "Importa os dados reais do ICC (site-data/icc.json e as fotos em "
        "site-data/members e site-data/partners). Pode ser rodado mais de uma "
        "vez: atualiza os registros existentes em vez de duplicar."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir", type=Path, default=DEFAULT_DIR,
            help=f"Pasta com o icc.json e as fotos (padrão: {DEFAULT_DIR}).",
        )
        parser.add_argument(
            "--atualizar-fotos", action="store_true",
            help="Substitui fotos e logos já cadastrados. Sem isso, só preenche quem está sem imagem.",
        )

    def handle(self, *args, **options):
        base = options["dir"]
        json_path = base / "icc.json"
        if not json_path.is_file():
            raise CommandError(
                f"Não encontrei {json_path}. Peça a pasta site-data a alguém do time "
                "e coloque-a na raiz do repositório."
            )

        # Importando no banco de produção sem Cloudinary, as imagens iriam
        # para o disco desta máquina e o site no ar ficaria com links quebrados.
        if os.environ.get("DATABASE_URL") and not settings.CLOUDINARY_STORAGE["CLOUD_NAME"]:
            raise CommandError(
                "DATABASE_URL definida sem CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET. "
                "Passe também as variáveis do Cloudinary para as fotos irem para a nuvem."
            )

        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)

        self.base = base
        self.replace_images = options["atualizar_fotos"]
        self.images_saved = 0

        with transaction.atomic():
            people = data["pessoas"]["registro"]
            members, current_ids = self._import_members(people, data["membros"]["diretorias"])
            partners = self._import_partners(data["parceiros"])
            programs = self._import_programs(data["projetos"]["iniciativas"])
            cases = self._import_cases(data["projetos"]["iniciativas"], people, members, programs)
            archived = self._archive_former_members(people, current_ids)

        self.stdout.write(self.style.SUCCESS(
            f"Importação concluída: {len(current_ids)} membros atuais, "
            f"{len(members) - len(current_ids)} ex-membros citados em cases, "
            f"{len(partners)} parceiros, {len(programs)} programas, {cases} cases, "
            f"{self.images_saved} imagens enviadas."
        ))
        if archived:
            self.stdout.write(f"Marcados como ex-membros: {', '.join(archived)}.")

    # ---------- Membros e diretorias ----------

    def _import_members(self, people, directorates):
        members = {}
        current_ids = []
        memberships = {}

        for order, item in enumerate(directorates):
            directorate, _ = Directorate.objects.update_or_create(
                name=item["nome"], defaults={"order": order},
            )
            for member_order, entry in enumerate(item["membros"]):
                person_id = entry["id"]
                if person_id not in members:
                    # O primeiro cargo listado (na ordem das diretorias) é o
                    # principal; os demais aparecem só como vínculo extra.
                    members[person_id] = self._save_member(person_id, people[person_id], entry["cargo"])
                    current_ids.append(person_id)
                memberships.setdefault(person_id, []).append(directorate.id)
                DirectorateMembership.objects.update_or_create(
                    member=members[person_id], directorate=directorate,
                    defaults={"cargo": entry["cargo"], "order": member_order},
                )

        # Quem mudou de diretoria no icc.json deixa de aparecer na antiga.
        for person_id, directorate_ids in memberships.items():
            members[person_id].directorate_memberships.exclude(
                directorate_id__in=directorate_ids
            ).delete()

        return members, current_ids

    def _save_member(self, person_id, person, cargo, active=True):
        trajetoria = person.get("trajetoria", [])
        defaults = {"name": person["nome"]}
        if cargo:
            position, _ = Position.objects.get_or_create(
                title=cargo, defaults={"power": _power(cargo)},
            )
            defaults["position"] = position
        if active:
            defaults["is_active"] = True

        # O LinkedIn é o identificador estável: todo mundo no icc.json tem um,
        # e nome pode ser corrigido pelo admin sem gerar um membro duplicado.
        member = Member.objects.filter(linkedin=person["linkedin"]).first()
        if member is None:
            member = Member(
                linkedin=person["linkedin"],
                is_active=active,
            )
        for field, value in defaults.items():
            setattr(member, field, value)
        self._attach_image(member, "photo", self.base / "members", person_id)
        member.save()
        self._save_trajectory(member, trajetoria)
        return member

    @staticmethod
    def _save_trajectory(member, trajetoria):
        """A trajetória do icc.json substitui a que estava cadastrada."""
        etapas = {
            (str(e.get("semestre", "")).strip(), str(e.get("cargo", "")).strip())
            for e in trajetoria
        }
        member.trajectory_steps.all().delete()
        for semestre, cargo in sorted(etapas):
            if semestre and cargo:
                member.trajectory_steps.create(semester=semestre, role=cargo)

    def _archive_former_members(self, people, current_ids):
        """
        Quem está no registro de pessoas mas ficou sem diretoria saiu do
        clube: é arquivado (some da Equipe) em vez de ser apagado,
        para continuar aparecendo nos cases antigos.
        """
        archived = []
        for person_id, person in people.items():
            if person_id in current_ids:
                continue
            updated = Member.objects.filter(
                linkedin=person["linkedin"], is_active=True,
            ).update(is_active=False)
            if updated:
                archived.append(person["nome"])
        return archived

    # ---------- Parceiros ----------

    def _import_partners(self, partners):
        saved = []
        for order, item in enumerate(partners):
            category, _ = PartnerCategory.objects.get_or_create(title=item["categoria"])
            partner = Partner.objects.filter(name=item["nome"]).first() or Partner(name=item["nome"], contato="")
            partner.description = item["descricao"]
            partner.category = category
            partner.site = item.get("site")
            partner.order = order
            self._attach_image(partner, "logo_url", self.base / "partners", slugify(item["nome"]))
            partner.save()
            saved.append(partner)
        return saved

    # ---------- Programas e cases ----------

    def _import_programs(self, initiatives):
        programs = {}
        for order, item in enumerate(initiatives):
            highlights = list(item.get("beneficios", []))
            if item.get("fastPass"):
                highlights.append(item["fastPass"])
            program, _ = Program.objects.update_or_create(
                slug=slugify(item["nome"]),
                defaults={
                    "label": item["nome"],
                    "subtitle": item.get("tipo", ""),
                    "description": item["descricao"],
                    "highlights": "\n".join(highlights),
                    "signup_url": item.get("inscricao", ""),
                    "order": order,
                },
            )
            # Os componentes viram as atividades do programa, exibidas em
            # "Como funciona" na página do projeto.
            for component in item.get("componentes", []):
                ProgramComponent.objects.update_or_create(
                    program=program, title=component["nome"],
                    defaults={"description": component["descricao"]},
                )
            programs[item["nome"]] = program
        return programs

    def _import_cases(self, initiatives, people, members, programs):
        count = 0
        for item in initiatives:
            for order, case_data in enumerate(item.get("cases", [])):
                case, _ = ProgramCase.objects.update_or_create(
                    program=programs[item["nome"]],
                    semester=case_data["semestre"],
                    title=case_data.get("nome", ""),
                    defaults={
                        "area": case_data["area"],
                        "theme": case_data["tema"],
                        "panel": "\n".join(case_data.get("bancaAvaliadora", [])),
                        "award": case_data["vencedores"].get("premiacao", ""),
                        "publication_url": case_data.get("instagramPost", ""),
                        "order": case_data.get("ordem", order),
                    },
                )
                winners = case_data["vencedores"]
                participants = [(pid, ProgramCaseParticipant.Role.INTEGRANTE) for pid in winners["equipe"]]
                if winners.get("mentor"):
                    participants.append((winners["mentor"], ProgramCaseParticipant.Role.MENTOR))

                for p_order, (person_id, role) in enumerate(participants):
                    if person_id not in members:
                        # Ex-membro citado só no case: cadastrado já com data
                        # de saída, para ter perfil sem aparecer na Equipe.
                        members[person_id] = self._save_member(
                            person_id, people[person_id], cargo=None, active=False,
                        )
                    ProgramCaseParticipant.objects.update_or_create(
                        case=case, member=members[person_id],
                        defaults={"role": role, "order": p_order},
                    )
                count += 1
        return count

    # ---------- Imagens ----------

    def _attach_image(self, instance, field_name, folder, slug):
        field = getattr(instance, field_name)
        if field and not self.replace_images:
            return
        path = _find_image(folder, slug)
        if path is None:
            return
        with path.open("rb") as f:
            field.save(f"{slug}{path.suffix.lower()}", File(f), save=False)
        self.images_saved += 1
