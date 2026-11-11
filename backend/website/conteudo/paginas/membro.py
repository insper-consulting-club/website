from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="membro", titulo="Perfil de um membro", caminho="/equipe",
    textos=(
        Texto("membro.voltar", "Perfil", "Link para voltar à Equipe", "Voltar para a equipe", raro=True),
        Texto("membro.nao_encontrado_titulo", "Quando o perfil não existe", "Título", "Membro não encontrado", raro=True),
        Texto("membro.nao_encontrado_texto", "Quando o perfil não existe", "Texto", "O perfil procurado não existe ou foi removido.", raro=True),
        Texto("membro.trajetoria", "Perfil", "Título da trajetória da pessoa", "Trajetória no ICC", raro=True),
        Texto("membro.atual", "Perfil", "Marca da etapa atual na trajetória", "Atual", raro=True),
    ),
)
