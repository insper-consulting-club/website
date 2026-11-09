from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="contato", titulo="Contato", caminho="/contato",
    textos=(
        Texto("contato.titulo", "Página", "Título (também é o nome da aba do navegador)", "Contato"),
        Texto("contato.abertura", "Página", "Texto logo abaixo do título", "Entre em contato com o Insper Consulting Club", campo_da_api="contact_lead"),
        Texto("contato.canais_titulo", "Página", "Título da lista de canais", "Canais oficiais"),
    ),
)
