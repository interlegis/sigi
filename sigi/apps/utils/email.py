# -*- coding: utf8 -*-

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def enviar_email(from_email, subject, template, tags):
    """Envia o email para o destinatário definido, a partir do template
    definido para ser renderizado. Os argumentos são:
        * from_email - Email do remetente
        * subject - Assunto da Mensagem
        * template - Template que será usado para gerar o corpo
        da mensagem
        * tags - Variáveis de contexto para ser renderizado no
        template.
    """
    if from_email is None:
        raise ValueError("Insira o email do remetente.")
    elif subject is None:
        raise ValueError("Insira o assunto da mensagem.")
    elif template is None:
        raise ValueError(u"Template da mensagem não encontrado")
    elif tags is None:
        raise ValueError("Insira o conteúdo da mensagem.")

    # Gerando a mensagem
    mensagem = render_to_string(template, tags)

    # Enviando a mensagem
    email = EmailMessage(settings.EMAIL_SUBJECT_PREFIX + " " + subject, mensagem,
        from_email, [from_email])
    email.send()
