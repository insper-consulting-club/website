from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="privacidade", titulo="Política de Privacidade", caminho="/politica-de-privacidade",
    textos=(
        Texto("privacidade.titulo", "Página", "Título (também é o nome da aba do navegador)", "Política de Privacidade"),
        Texto("privacidade.erro", "Página", "Aviso quando o texto da política não carrega", "Não foi possível exibir a política agora. Para qualquer dúvida sobre o tratamento dos seus dados, escreva para o e-mail abaixo.", tipo="longo", raro=True),
    ),
)
