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

def valida_periodo_data(di01, df01, di02, df02):
    """Função responsável por validar dois períodos de datas.
    Isso é usado para verificar se determinado servidor exerceu
    mais de uma função dentro de determinados períodos descritos
    abaixo:

    1 - A segunda função não pode ter exercido ao mesmo tempo que
    a primeira função. Exemplo:

        Primeiro Função: 01/05/2011 -- 01/11/2011
        Segundo Função: 01/05/2011 -- 01/11/2011

    2 - A segunda função não pode ter exercido, dentro do período
    da primeira função. Exemplo:

        Primeira Função: 01/05/2011 -- 01/11/2011
        Segunda Função: 02/05/2011 -- 30/10/2011
    """
    # Verificando a primeira situação
    if di01 == di02 and df01 == df02:
        return True
    else:
        return False

    # Verificando a segunda situação
    if di01 >= di02 or df01 <= df02:
        return True
    else:
        return False


