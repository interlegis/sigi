------------------------------------------------------------------------------------
-- Correção dos dados do município de Campo Grande/RN, que chamava-se Augusto Severo --
-- e que, por força de lei municipal, passou a denominar-se Campo Grande e ainda     --
-- permanece com o nome antigo na base de dados do IBGE.                             --
---------------------------------------------------------------------------------------

select * from contatos_municipio
where codigo_ibge like '240130%'

/* ---------------------------- RESULT SET --------------------------------------------
codigo_ibge;codigo_mesorregiao;codigo_microrregiao;codigo_tse;nome;uf_id;is_capital;populacao;is_polo;latitude;longitude;search_text;data_criacao
240130;;;16250;"Campo Grande";24;f;9289;f;;;"Campo Grande Rio Grande do Norte";""
2401305;;;1625;"Augusto Severo";24;f;9194;f;;;"Augusto Severo Rio Grande do Norte";""
*/

delete from contatos_municipio
where codigo_ibge = 240130

update contatos_municipio
set codigo_tse = 16250,
    nome = 'Campo Grande',
    populacao = 9289,
    search_text = 'Campo Grande Rio Grande do Norte'
where codigo_ibge = 2401305

select * from contatos_unidadefederativa where codigo_ibge = 24
    