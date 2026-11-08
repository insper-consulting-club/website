from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def valida_tamanho_da_imagem(arquivo):
    """
    Recusa imagens maiores que MAX_IMAGE_UPLOAD_MB (padrão: 5 MB), para proteger a cota do
    armazenamento de imagens. Só mede um envio novo: uma imagem já guardada não é consultada,
    porque medi-la custaria uma ida ao Cloudinary.
    """
    if getattr(arquivo, '_committed', True):
        return
    limite = settings.MAX_IMAGE_UPLOAD_MB * 1024 * 1024
    if arquivo.size > limite:
        tamanho = f'{arquivo.size / (1024 * 1024):.1f}'.replace('.', ',')
        raise ValidationError(
            f'A imagem tem {tamanho} MB, e o limite é {settings.MAX_IMAGE_UPLOAD_MB} MB. '
            'Reduza o tamanho ou comprima a imagem antes de enviar (fotos de celular costumam ser grandes demais).'
        )


class LimitedImageField(models.ImageField):
    """ImageField que confere o tamanho do arquivo. Para as migrations, continua sendo um ImageField."""
    default_validators = [*models.ImageField.default_validators, valida_tamanho_da_imagem]

    def deconstruct(self):
        nome, _caminho, args, kwargs = super().deconstruct()
        return nome, 'django.db.models.ImageField', args, kwargs
