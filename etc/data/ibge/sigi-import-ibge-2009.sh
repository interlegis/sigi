#!/bin/sh

arquivo_csv=""

# Caso a variavel _DEBUG nao tenha sido preparada externamente,
# assumir que o default é sem DEBUG
if [ -z "${_DEBUG}" ]
then
	_DEBUG="0"
fi

# Default verboso
if [ -z "${_VERBOSE}" ]
then
	_VERBOSE="1"
fi

PrintDebug( )
{
	# para a mensagem ser mostrada, _DEBUG deve ser configurada
	# e o valor deve ser diferente de "0"
	if [ -n "${_DEBUG}" -a "${_DEBUG}" -ne "0" ]
	then
		echo "$@"
	fi
}

PrintHelp( )
{
	PrintDebug `basename "${0}"` " -- importa tabelas de cidades do IBGE"
	PrintDebug "Opcoes aceitas:"
	PrintDebug "	arquivo_csv=[caminho]"
	PrintDebug "		informa o caminho para o arquivo no formato 2009"
	PrintDebug "	_DEBUG=[debug]"
	PrintDebug "		0 para nao mostrar mensagens, 1 para mostrar"
}

PrintMessage( )
{
	# para a mensagem NAO ser mostrada, _VERBOSE deve ser configurada
	# e o valor deve ser "0"
	if [ -z "${_VERBOSE}" -o "${_VERBOSE}" -ne "0" ]
	then
		echo "$@"
	fi
}

while [ "${#}" -gt 0 ]
do
	if echo "${1}" | grep "=" 2>&1 > /dev/null
	then
		PrintDebug "Argumento de configuracao: \"${1}\""
		eval "${1}"
	else
		PrintDebug "Argumento desconhecido: \"${1}\""
		PrintHelp
		exit 1
	fi

	shift
done

if [ -z "${arquivo_csv}" ]
then
	PrintDebug "ERRO: informe o arquivo de importacao."
	PrintHelp
	exit 2
fi

if [ ! -f "${arquivo_csv}" ]
then
	PrintDebug "ERRO: o arquivo de importacao nao existe ou nao pode ser acessado (\"${arquivo_csv}\")."
	PrintHelp
	exit 3
fi

if [ ! -r "${arquivo_csv}" ]
then
	PrintDebug "ERRO: o arquivo de importacao nao pode ser lido (\"${arquivo_csv}\")."
	PrintHelp
	exit 4
fi

# filtrar o arquivo original para area de trabalho, por
# UF, Mesorregiao, Microrregiao, Municipio e depois executar
# os scripts Python para atualização do banco

nome_base=sigi_ibge_import
niveis="uf macrorregiao microrregiao municipio"
for nivel in $niveis
do
	eval "arquivo_${nivel}=/tmp/${nome_base}.${nivel}.csv"
done

# arquivo_uf=/tmp/${nome_base}.uf.csv
# arquivo_macrorregiao=/tmp/${nome_base}.macrorregiao.csv
# arquivo_microrregiao=/tmp/${nome_base}.microrregiao.csv
# arquivo_municipio=/tmp/${nome_base}.municipio.csv

exec 3< "${arquivo_csv}" 4> "${arquivo_uf}" 5> "${arquivo_macrorregiao}" 6> "${arquivo_microrregiao}" 7> "${arquivo_municipio}"

lnum=0

PrintMessage "Iniciando leitura dos dados..."

read linha <&3
while read linha <&3
do
	lnum=$(($lnum + 1))
	if [ $(($lnum % 100)) -eq 0 ]
	then
		PrintMessage -n "${lnum} "
	fi
	echo "$linha" | cut -s -d, -f1,2 >&4
	echo "$linha" | cut -s -d, -f1,3,4 >&5
	echo "$linha" | cut -s -d, -f1,3,5,6 >&6
	echo "$linha" | cut -s -d, -f1,3,5,7,8 >&7
	if [ "${lnum}" -ge 1000 ]
	then
		break
	fi
done

PrintMessage "\n${lnum} registros processados"

# fecha os descritores de saida
exec 4>&- 5>&- 6>&- 7>&-

for nivel in $niveis
do
	eval "arq_in=/tmp/${nome_base}.${nivel}.csv"
	eval "arq_out=/tmp/${nome_base}.${nivel}.csv.tmp"
	sort < $arq_in > $arq_out
	uniq < $arq_out > $arq_in
	rm $arq_out
done

ifs="$IFS"
IFS="
"
for l in `wc -l /tmp/${nome_base}*`
do
	PrintDebug $l
done
IFS="$ifs"

# Processar arquivos: INSERT ou UPDATE no banco

