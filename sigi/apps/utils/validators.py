# -*- coding: utf8 -*-

def valida_data(data_inicio, data_final):
    """Função responsável por validar se o intervalo das
    datas estão erradas, ou seja, se a data de início está
    maior ou igual a data final.

    Caso seja maior ou igual retornará ``True``, caso contrário
    retornará ``False``.
    """
    if data_inicio >= data_final:
        return True
    else:
        return False

