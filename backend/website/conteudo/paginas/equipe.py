from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="equipe", titulo="Equipe", caminho="/equipe",
    textos=(
        Texto("equipe.eyebrow", "Cabeçalho da página", "Palavra pequena acima do título", "Membros"),
        Texto("equipe.titulo", "Cabeçalho da página", "Título (também é o nome da aba do navegador)", "Nossa Equipe"),
        Texto("equipe.abertura", "Cabeçalho da página", "Texto logo abaixo do título", "Conheça os membros que fazem parte da Liga Insper Consulting Club"),
        Texto("equipe.vazio", "Lista de membros", "Mensagem quando não há nenhum membro", "Nenhum membro cadastrado no momento.", raro=True),
        Texto("equipe.contagem_um", "Lista de membros", "Contagem de uma diretoria com 1 membro", "{n} membro", raro=True),
        Texto("equipe.contagem_varios", "Lista de membros", "Contagem de uma diretoria com mais de 1 membro", "{n} membros", raro=True),
        Texto("equipe.outros", "Lista de membros", "Nome do grupo de quem não está em nenhuma diretoria", "Outros"),
    ),
)
