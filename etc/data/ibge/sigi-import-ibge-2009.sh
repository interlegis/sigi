#!/bin/sh

arquivo_csv=""
limite=0

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
	PrintMessage `basename "${0}"` " -- importa tabelas de cidades do IBGE"
	PrintMessage "Opcoes aceitas:"
	PrintMessage "	arquivo_csv=[caminho]"
	PrintMessage "		informa o caminho para o arquivo no formato 2009"
	PrintMessage "	limite=N"
	PrintMessage "		determina a quantidade maxima de registros de entrada processados"
	PrintMessage "	_VERBOSE=[verbose]"
	PrintMessage "		0 para nao mostrar mensagens, 1 para mostrar"
	PrintMessage "	_DEBUG=[debug]"
	PrintMessage "		0 para nao mostrar mensagens de depuracao, 1 para mostrar"
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

# Processar os argumentos passados pela linha de comando. Devem estar no
# formato de atribuicao de variaveis em Shell, ou entao devem ser atribuidos
# e exportados pelo processo chamador. Caso na expressao [var]=[valor] exista
# separadores, todo o argumento deve estar entre aspas: "[var]=[valor]"
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

####################################
# Secao de validacao de parametros
if [ -z "${arquivo_csv}" ]
then
	PrintMessage "ERRO: informe o arquivo de importacao."
	PrintHelp
	exit 2
fi

if [ ! -f "${arquivo_csv}" ]
then
	PrintMessage "ERRO: o arquivo de importacao nao existe ou nao pode ser acessado (\"${arquivo_csv}\")."
	PrintHelp
	exit 3
fi

if [ ! -r "${arquivo_csv}" ]
then
	PrintMessage "ERRO: o arquivo de importacao nao pode ser lido (\"${arquivo_csv}\")."
	PrintHelp
	exit 4
fi

# filtrar o arquivo original para area de trabalho, por
# UF, Mesorregiao, Microrregiao, Municipio e depois executar
# os scripts Python para atualização do banco.
# O formato do arquivo obtido do IBGE e' CSV com as seguintes colunas:
#
# 1: "UF"
# 2: "Nome_UF"
# 3: "MesorregiãoGeográfica"
# 4: "MesorregiãoGeográfica_Nome"
# 5: "MicrorregiãoGeográfica"
# 6: "MicrorregiãoGeográfica_Nome"
# 7: "Município"
# 8: "Município_Nome"
# 9: "Distrito"
# 10: "Distrito_Nome"
# 11: "Subdistrito"
# 12: "Subdistrito_Nome"

nome_base=sigi_ibge_import
niveis="uf mesorregiao microrregiao municipio"
for nivel in $niveis
do
	eval "arquivo_${nivel}=/tmp/${nome_base}.${nivel}.csv"
done

exec 3< "${arquivo_csv}" 4> "${arquivo_uf}" 5> "${arquivo_mesorregiao}" 6> "${arquivo_microrregiao}" 7> "${arquivo_municipio}"

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
	# extrair o codigo da regiao a partir do codigo da UF
	# e criar o novo campo 1 com o codigo da regiao
	codregiao=`echo "$linha" | cut -b2-2`
	linha="\"${codregiao}\",$linha"
	# UFs: cod_regiao,cod_uf,nome_uf
	#	-- a sigla por enquanto devera ser adicionada manualmente
	echo "$linha" | cut -s -d, -f1,2,3 >&4
	# Mesorregiao: cod_regiao,cod_uf,cod_mesorregiao,nome_mesorregiao
	echo "$linha" | cut -s -d, -f1,2,4,5 >&5
	# Microrregiao: cod_regiao,cod_uf,cod_mesorregiao,cod_microrregiao,nome_microrregiao
	echo "$linha" | cut -s -d, -f1,2,4,6,7 >&6
	# Municipio: cod_regiao,cod_uf,cod_mesorregiao,cod_microrregiao,cod_municipio,nome_municipio
	# 7> "${arquivo_municipio}"
	echo "$linha" | cut -s -d, -f1,2,4,6,8,9 >&7
	if [ -n "${limite}" -a "${limite}" -gt 0 -a "${lnum}" -ge "${limite}" ]
	then
		break
	fi
done

PrintMessage "\n${lnum} registros processados"

# fecha os descritores de saida
exec 3<&- 4>&- 5>&- 6>&- 7>&-

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


