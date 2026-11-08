import logging
import threading

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def dispara_deploy_do_frontend(sincrono=False):
    """
    Pede ao Render que reconstrua o frontend. O site é estático: a descrição, a
    imagem de compartilhamento, o ícone e o logo entram no HTML durante o build,
    então uma mudança neles só aparece depois de um novo deploy.

    A chamada nunca interrompe quem salvou a configuração: sem a variável
    RENDER_FRONTEND_DEPLOY_HOOK, ou se o Render não responder, só se registra o
    aviso. O endereço do hook contém uma chave secreta e não vai para o log.
    """
    url = settings.RENDER_FRONTEND_DEPLOY_HOOK
    if not url:
        return False

    def chama():
        try:
            resposta = requests.post(url, timeout=10)
            if resposta.status_code >= 400:
                logger.warning("O Render recusou o pedido de deploy do frontend (HTTP %s).", resposta.status_code)
        except requests.RequestException as erro:
            # Só o tipo do erro: a mensagem de requests pode trazer o endereço.
            logger.warning("Não foi possível pedir o deploy do frontend (%s).", type(erro).__name__)

    if sincrono:
        chama()
    else:
        threading.Thread(target=chama, daemon=True).start()
    return True
