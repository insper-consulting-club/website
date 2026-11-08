import json

from django.conf import settings
from unfold.widgets import UnfoldAdminTextareaWidget


class MarkdownPreviewWidget(UnfoldAdminTextareaWidget):
    """
    Campo de texto em Markdown com botão de prévia. A prévia é a página /previa do
    site (frontend), aberta num iframe, para mostrar o texto exatamente como será
    publicado. Sem FRONTEND_URL, o campo aparece sem prévia.

    modo: "artigo", "politica" ou "programa", o estilo que o site aplica ao texto.
    imagens: lista de {"number", "image_url", "caption"}, para ![](imagem-N) nos artigos.
    """
    template_name = "website/widgets/markdown_preview.html"

    class Media:
        js = ("website/markdown_preview.js",)

    def __init__(self, modo="artigo", imagens=None, attrs=None):
        super().__init__(attrs)
        self.modo = modo
        self.imagens = imagens or []

    def get_context(self, name, value, attrs):
        contexto = super().get_context(name, value, attrs)
        base = settings.FRONTEND_URL.rstrip("/")
        contexto["widget"].update({
            "previa_url": f"{base}/previa" if base else "",
            "modo": self.modo,
            "imagens_json": json.dumps(self.imagens),
        })
        return contexto
