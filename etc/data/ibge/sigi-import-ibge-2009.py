import sys, csv

"""
"""

_root_dict = None

def getUFdict( root, ufid ):
	return( root[ ufid ] )

def getCidadesDict( macrodict, microid ):
	if macrodict = None:
		return( None )
	microdoct = macrodict[ '__children' ]
	if microdict = None:
		microdict = {}
		macrodict[ '__children' ] = microdict

def main( ):
	argc = len( sys.argv )
	arquivo = open( 'geoftp.ibge.gov.br/organizacao_territorial/divisao_territorial/2009/DTB_05_05_2009.csv', 'r' )
	# despreza o cabecalho
	arquivo.readline( )

	lnum=0
	csv_reader = csv.reader( arquivo, delimiter=',', quotechar='"' )
	for registro in csv_reader:
		if uf[ registro[ 0 ] ] = None:
			uf[ registro[ 0 ] ] = {}
			uf[ registro[ 0 ] ][ 'nome' ] = registro[ 1 ]
			uf[ registro[ 0 ] ][ 'macrorregioes' ] = {}
#		print "lnum: %s - %s" % ( lnum, registro )
		lnum = lnum + 1
		if lnum >= 10:
			break

if __name__ = "__main__":
	main( )
	dumpdicts( )

