# -*- coding: utf-8 -*-

#Este script recibe como parametro la ruta del archivo de entrada en argv[1].

#Para ejuctarlo:

# > python docToFeatures.py articulos/ARTICULOS/articulo_4.txt

#Al final, el script genera 4 archivos de salida:
#El archivo de salida de freeling con el etiquetaje morfosintactico y el codigo para mapear la carga de sentimiento de cada palabra despues de desambiguar el sentido.
#El archivo taggedFile.txt que es una version formateada de la salida anterior de freeling
#El archivo sentiTaggedFile.txt con el texto etiquetado morfosintacticamente y con carga de sentimiento habiendo desambiguado el sentido de cada palabra.
#El archivo outputFreelingParsed con el texto analizado sintacticamente

from __future__ import division

import os
import io
import sys
import re
import nltk.data
import nltk


#Methods

#Método para validar si una carga de sentimiento leida como string si corresponde a un numero en este caso decimal tipo float
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#Método para extraer las oraciones de un texto. Retorna una lista con cada oración en una posición.
def extract_sentences(input_file):
    #with io.open (input_file, "r", encoding='utf-8') as doc:	#Este es el orignal
    with io.open (input_file, "r", encoding='latin-1') as doc:	#Este se cambió para el corpus de reviews pero aún no lee los archivos bien.
        data = doc.read()
    
    tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
    sentences = tokenizer.tokenize(data)
    
    #for s in sentences:
        #print s
    return sentences

#######################################################################################################
#Trabajo futuro muy IMPORTANTE
#Extraer las entidades y los aspectos para refinar el análisis de sentimiento a nivel de documento
#######################################################################################################

print "\nRunning . . .\n"

entrada = sys.argv[1]		#Para pasar el archivo de entrada via linea de comandos

print "\nProcesando: "+entrada+"\n"

#Aqui se hace la desambiguacion de los sentidos usando freeling

print "\nDisambiguation . . .\n"

#Con la siguiente linea se genera la salida de freeling con la opcion tagged
os.system('analyze –f analyze -f /usr/local/share/freeling/config/es.cfg <' + entrada + '> outputFreeling.txt')

#Con la siguiente linea se genera la salida de freeling con la opcion parsed
os.system('analyze –f analyze -f /usr/local/share/freeling/config/es2.cfg <' + entrada + '> outputFreelingParsed.txt')

#Aqui se toma la salida de freeling y se lleva al formato -> word	tag	codigoSentiWordNet

print "\nFormatting Data . . .\n\n"

freelingFile = open("outputFreeling.txt", "r")
taggedFile = open("taggedFile.txt", "w")

id_frase = 0
for line in freelingFile:
	l = line.split(" ")
	if len(l) == 5:	#Esto es para evitar errores cuando hay doble saltos de linea que generan lineas vacias.
		word = l[0]	#Esta es la palabra a etiquetar y marcar con carga de sentimiento 
		#tag = temCod[-1] #Esta es la categoria gramatical poco especifica entregada por freeling cuando la palabra tiene carga de sentimiento en SentiWordnet
		tag = l[2]
		
		if len(l[4]) > 2:
			cod = l[4][0:8]	 #Este es el codigo para mapear con sentiwordnet
		else:
			cod = ""
		
		if cod != "":
			#print word + "\t" + tag + "\t" + cod
			taggedFile.write(word + "\t" + tag + "\t" + cod + '\t' + str(id_frase) + "\n")
		else:
			taggedFile.write(word + "\t" + tag + "\t" + "NoSentiTag" + '\t' + str(id_frase) + "\n")

		#Controlamos el id o número de la frase en la que aparece el token actual
		#cuando encuentra un punto, un signo de interrogación o uno de admiración cerrando finaliza oración e inicia una nueva.
		#Esto se puede mejorar con otros signos de puntuación que indican fin de oración, por ahora está hasta aquí el desarrollo.
		if tag == 'Fp' or tag == 'Fit' or tag == 'Fat': 
			id_frase += 1
			#print word + "\t" + tag + "\t" + str(id_frase) + "\t"


freelingFile.close()
taggedFile.close()

#Aquí se extraen las frases del documento
frases = extract_sentences(entrada)

'''
i = 0
for f in frases:
	print str(i) + "\t" + f
	i += 1
print "\n"
'''

#print len(frases)
#print frases[24]


#Aqui se hace el mapeo con SentiWordNet para obtener la carga de sentimiento de cada palabra del articulo

taggedFile = open("taggedFile.txt", "r")

mapFile = open("sentiTaggedFile.txt", "w")


#Se cuentan las palabras del artículo con el fin de delimitar las secciones intro, cuerpo y conclusiones (0 - 25% ; 26% - 75% ; 76% - 100%)
with open(entrada, 'r') as articuloOriginal:
   data=articuloOriginal.read().replace('\n', '')

NumPalabras = len(data.split(" "))
limIntro = (NumPalabras*25)/100
limCuerpo = (NumPalabras*75)/100

#print "Intro va de la 1 a la " + str(limIntro) + "\n"
#print "Cuerpo va de " + str(1+limIntro) +" hasta la " + str(limCuerpo) +"\n"
#print "Conclusiones van de " + str(1+limCuerpo) +" hasta la " + str(NumPalabras) +"\n"

cuentaPalabras = 0
#signosDePuntuacion = ['.', ',', ';', ':', '!', '¡', '?', '¿', '...', '"', '\'', '(', ')']

print "Tagging Data with Sentiment Tags . . .\n\n"

#Con las siguientes variables guardamos el contenidos de las secciones S1, S2 y S3 para preguntar luego si contienen conmutadores de polaridad e invertirla
textoS1 = ""
textoS2 = ""
textoS3 = ""

for l2 in taggedFile:
	
	lineaTagFile = l2.split("\t")
	
	section = ""
	
	#if lineaTagFile[0] in signosDePuntuacion:
	#	 cuentaPalabras = cuentaPalabras
	#else:
	#	cuentaPalabras += 1

	cuentaPalabras += 1

	#Asignamos la sección a la que pertenece la palabra
	#Nota: Esto no es preciso 100% es una aproximación. Además, el archivo original luego es tokenizado y genera algunos tokens extras.
	if cuentaPalabras <= limIntro:
		section = "S1"
		textoS1 += lineaTagFile[0].lower() + ' '
	elif cuentaPalabras > limIntro and cuentaPalabras <= limCuerpo:
		section = "S2"
		textoS2 += lineaTagFile[0].lower() + ' '
	else:
		section = "S3"
		textoS3 += lineaTagFile[0].lower() + ' '
	
	sentiwordnet = open("SentiWordNet_3.0.txt", "r")
	
	if lineaTagFile[2] != "NoSentiTag":
	
		for l3 in sentiwordnet:
		
			lineaSenti = l3.split("\t")
			
			if lineaTagFile[2] == lineaSenti[1]:
				
				mapFile.write(lineaTagFile[0] + "\t" + lineaTagFile[1] + "\t" + lineaTagFile[2] + "\t" + lineaSenti[2] + "\t" + lineaSenti[3] + "\t" + section + "\t" + lineaTagFile[3][:-1] + "\n")
				#mapFile.write(l2[:-3] + "\t" + lineaSenti[2] + "\t" + lineaSenti[3] + "\t" + section + "\t" + lineaTagFile[3][:-1] + "\n")
				break #Hay pocos casos en los que el ID en sentiwordnet no es único, entonces nos quedamos con el primer sentido encontrado
					  #en el archivo de arriba hacia abajo
	else:
		
		mapFile.write(lineaTagFile[0] + "\t" + lineaTagFile[1] + "\t" + lineaTagFile[2] + "\t" + "0" + "\t" + "0" + "\t" + section + "\t" + lineaTagFile[3][:-1] + "\n")
		#mapFile.write(l2[:-3] + "\t" + "0" + "\t" + "0" + "\t" + section + "\t" + lineaTagFile[3][:-1] + "\n")

taggedFile.close()
sentiwordnet.close()
mapFile.close()

'''
for ts1, ts2, ts3 in zip(textoS1, textoS2, textoS3):
	print ts1
	print ts2
	print ts3
'''	


#Aqui se extraen los patrones: 1) Verbo + Objeto 2) Atributo 
#Esto se hace leyendo el archivo analizado sintácticamente

print "Extracting patterns . . .\n\n"

parsedFile = open("outputFreelingParsed.txt","r")

#Los siguientes dos archivos no concatenan los patrones, los sobrescriben para cada articulo
#VerboObjetoFile = open("patronesVerboObjeto.txt", "w")
#AtributoFile = open("patronesAtributo.txt", "w")

#Los siguientes dos archivos concatenan los patrones para todos los articulos.
VerboObjetoFile = open("patronesVerboObjeto.txt", "a")
AtributoFile = open("patronesAtributo.txt", "a")
SintagmaAdjFile = open("sintagmasAdjetivales.txt", "a")
VerbosParticipioFile = open("verbosParticipio.txt", "a")


cargasPatronesVerboObjetoPos = open("cargasPatronesVerboObjetoPos.txt", "w")
cargasPatronesVerboObjetoNeg = open("cargasPatronesVerboObjetoNeg.txt", "w")
cargasPatronesAtributoPos = open("cargasPatronesAtributoPos.txt", "w")
cargasPatronesAtributoNeg = open("cargasPatronesAtributoNeg.txt", "w")
cargasSintagmasAdjFilePos = open("cargasSintagmasAdjetivalesPos.txt", "w")
cargasSintagmasAdjFileNeg = open("cargasSintagmasAdjetivalesNeg.txt", "w")
cargasVerbosParticipioFilePos = open("cargasVerbosParticipioPos.txt", "w")
cargasVerbosParticipioFileNeg = open("cargasVerbosParticipioNeg.txt", "w")


gv = 0 #grupo verbal desactivado
cuentaCorchetes = 0		#Esta variable cuenta los corchetes para grupo sn
cuenta = False  #activa la cuenta de corchetes para el grupo sn
cuenta2 = False #activa la cuenta de corchetes para el grupo verbal
cuenta3 = False	#activa la cuenta de corchetes para el grupo sp
cuenta5 = False	#activa la cuenta de corchetes para el grupo s_adj
cuentaCorchetesAdj = 0

cuenta6 = False	#activa la cuenta de corchetes para el grupo v_part
cuentaCorchetesV_Part = 0


isVerb = False
esCopulativo = False
esAux = False
cuentaCorchetesVerb = 0		#Esta variable cuenta los corchetes para grupo verbal
grupVerb = False
cuentaCorchetesSp = 0		#Esta variable cuenta los corchetes para sp
grupSp = False
negacion = False

lineaVObj = 0	#Este valor sirve para controlar la asignación de sección de los patrones. Inician en la sección 1.
lineaAtr = 0	#Este valor sirve para controlar la asignación de sección de los patrones. Inician en la sección 1. 
lineaAdj = 0	#Este valor sirve para controlar la asignación de sección de los patrones Adjetivo. Inician en la sección 1.

cntAtr = 0

verbo = []
verbo_forma = []
tagV = []
objeto = []
tagObj = []
atributo = []
atributo_lemma = []
tagAtr = []
IDsVerbo = []
IDsObj = []
IDsAtr = []

s_adj = []
s_adj_forma = []
tag_s_adj = []
IDs_s_adj = []

v_part = []
tag_v_part = []
IDs_v_part = []

adjuntos = [] #Para preguntar luego por la aparición de la negación en el patrón V + obj

#lista de verbos copulativos o seudocopulativos
copulativos = ['ser', 'parecer', 'haber', 'ponerse', 'sentirse', 'andar', 'estar', 'tener']

#Listado de verbos con su polaridad y su tipo. 
#Polaridad:
#(0->neutro, 1->positivo, -1->negativo)
#Tipo:
#(0->neutro; 1->verbo de refuero; 2->verbo de decadencia)
#Ej: mejorar -> 10; verbo de carga positiva y tipo neutro
#Nota: por ahora solo lo tengo con la polaridad, el tipo todavía no lo he implementado.

#lista_verbos = {"pensionar": "1", "poner": "0", "mejorar": "1", "dejar": "0", "saber": "0", "generar": "1", "ampliar": "1", "venir": "0", "disminuir": "0", "crear": "0", "alcanzar": "1", "revertir": "1", "llegar": "0", "dar": "0", "brindar": "1", "recibir": "0", "permitir": "1", "cotizar": "0", "completar": "1", "lograr": "1", "obtener": "1", "extender": "1", "aumentar": "0", "expresar": "0", "examinar": "0", "iniciar": "0", "atravesar": "0", "levantar": "0", "compartir": "1", "asegurar": "0", "enfrentar": "0", "hablar": "0", "hacer": "0", "profundizar": "0", "ver": "0", "tramitar": "0", "visar": "0", "plantear": "0", "facilitar": "1", "apoyar": "1", "resultar": "0", "solicitar": "0", "superar": "1", "aprovechar": "0", "obligar": "-1", "ganar": "1", "necesitar": "-1", "buscar": "0", "implementar": "0", "garantizar": "1", "finalizar": "0", "afectar": "-1", "desencadenar": "0", "deber": "-1", "producir": "0", "evidenciar": "0", "regular": "0", "evitar": "0", "pasar": "0", "anunciar": "0", "dotar": "1", "contar": "0", "invertir": "0", "subsidiar": "1", "alejar": "0", "decir": "0", "firmar": "0", "beneficiar": "1", "llevar": "0", "destacar": "1", "depender": "0", "querer": "0", "adquirir": "1", "comprar": "0", "informar": "0", "entregar": "0", "recordar": "0", "constituir": "1", "invitar": "0", "aunar": "1", "crecer": "0", "implicar": "0", "cerrar": "0", "acabar": "0", "comprender": "1", "considerar": "0", "realizar": "0", "seguir": "0", "exigir": "-1", "perder": "-1", "partir": "0", "mostrar": "0", "bajar": "0", "proclamar": "0", "reducir": "0", "reconocer": "0", "suceder": "0", "salir": "0", "impedir": "-1", "desacelerar": "-1", "resolver": "0", "afirmar": "0", "mirar": "0", "llenar": "0", "aprobar": "1", "fortalecer": "1", "explicar": "0", "atender": "0", "esperar": "0", "llevar_a_cabo": "0", "incluir": "0", "revelar": "0", "prender": "0", "advertir": "0", "presentar": "0", "señalar": "0", "desenvolver": "0", "trabajar": "1", "contraer": "0", "desarrollar": "1", "promover": "0", "existir": "0", "desempeñar": "0", "encontrar": "0", "prevalecer": "0", "diferenciar": "0", "identificar": "0", "predominar": "0", "inferir": "0", "representar": "0", "percibir": "0", "pertenecer": "0", "concluir": "0", "impulsar": "0", "defender": "0", "lanzar": "0", "democratizar": "0", "sellar": "0", "rechazar": "0", "devolver": "0", "preferir": "0", "abandonar": "-1", "coincidir": "0", "adelantar": "0", "resaltar": "0", "recalcar": "0", "insistir": "0", "ir": "0", "hacer_ver": "0", "sufrir": "-1", "reiterar": "0", "divulgar": "0", "tratar": "0", "conformar": "0", "ejercer": "0", "pedir": "0", "desconcentrar": "-1", "expedir": "0", "blindar": "1", "proteger": "1", "suscribir": "0", "apuntar": "0", "articular": "0", "sostener": "0", "equivaler": "0", "estimar": "0", "ralentizar": "-1", "caer": "0", "mantener": "0", "suponer": "0", "indicar": "0", "registrar": "0", "cuestionar": "0", "versar": "0", "indagar": "0", "responder": "0", "quedar": "0", "respetar": "1", "sobrevivir": "1", "opinar": "0", "escribir": "0", "incrementar": "0", "prestar": "0", "proponer": "0", "creer": "0", "salvar": "1", "elegir": "0", "poder": "0", "prevenir": "1", "padecer": "-1", "combatir": "1", "requerir": "0", "asumir": "0", "consistir": "0", "votar": "0", "fundar": "0", "asesinar": "-1", "utilizar": "0", "morir": "-1", "causar": "0",  "construir": "1", "cumplir": "1", "llover": "0", "caminar": "0", "romper": "-1", "sumar": "0", "declarar": "0", "aterrizar": "0", "convertir": "0", "incautar": "-1", "desarticular": "0", "ejecutar": "0", "cometer": "-1", "conquistar": "0", "faltar": "0", "conciliar": "1", "pensar": "0", "demostrar": "0", "cambiar": "0", "reunir": "0", "vender": "0", "emitir": "0", "exonerar": "1", "engañar": "-1", "discutir": "0", "entender": "0", "desaparecer": "0", "parir": "0", "acordar": "1", "concretar": "0", "pelear": "-1", "imaginar": "0", "preocupar": "-1", "rondar": "0", "avanzar": "0", "poner_de_relieve": "0", "escoger": "0", "explorar": "0", "fijar": "0", "complejizar": "-1", "tomar": "0", "desconocer": "0", "concentrar": "0", "disponer": "0", "hallar": "0", "abrir": "0", "cargar": "0", "silenciar": "0", "restituir": "1", "conocer": "0", "sacar": "0", "confesar": "0", "erradicar": "1", "dedicar": "0", "conseguir": "0", "sacrificar": "0", "reiniciar": "0", "evacuar": "0", "precisar": "0", "pronosticar": "0", "cifrar": "0", "estimular": "0", "afianzar": "0", "distribuir": "0", "racionalizar": "1", "valorar": "0", "sobrellevar": "0", "regresar": "0", "arrancar": "0", "agregar": "0", "ofrecer": "1", "aclarar": "0", "liderar": "1", "ubicar": "0", "sentir": "0", "evaluar": "0", "simplificar": "1", "fomentar": "1", "ocupar": "0", "surgir": "0", "dinamizar": "1", "insinuar": "0", "citar": "0", "avecinar": "0", "manejar": "0", "eliminar": "0", "generalizar": "0", "colaborar": "0", "diferir": "0", "definir": "0", "negar": "0", "centrar": "0", "dejar_de_lado": "0", "basar": "0", "comparar": "0", "transformar": "0", "exponer": "0", "fique": "0", "regalar": "1", "usurpar": "-1",  "pretender": "0", "criticar": "-1", "legitimar": "0", "trinar": "0", "legislar": "0", "justificar": "0", "desmotivar": "-1", "frenar": "0", "paralizar": "-1", "revivir": "0", "imponer": "-1", "vivir": "0", "incentivar": "1", "medir": "0", "reportar": "0", "escuchar": "0", "enseñar": "0", "formalizar": "0", "empezar": "0", "contratar": "0", "olvidar": "0", "acceder": "0", "ratificar": "0", "aportar": "0", "puntualizar": "0", "hacendar": "0", "calificar": "0", "participar": "0", "elogiar": "1", "restar": "0", "comprobar": "0", "agradecer": "1", "retirar": "0", "respaldar": "1", "filtrar": "0", "otorgar": "1", "añadir": "0", "acatar": "0", "cobrar": "0", "luchar": "0", "sembrar": "0", "cosechar": "1", "publicar": "0", "mencionar": "0", "acompañar": "0", "protagonizar": "0", "conversar": "0", "significar": "0", "delinear": "0", "descalificar": "-1", "correr": "0", "estrechar": "0", "leer": "0", "manifestar": "0", "transcurrir": "0", "inquietar": "0", "llamar": "0", "explotar": "0", "disparar": "-1", "experimentar": "0", "reflejar": "0", "amenazar": "-1", "confirmar": "0", "destruir": "-1", "rodrigar": "0", "determinar": "0", "terminar": "0", "destinar": "0", "reparar": "1", "enfatizar": "0", "desplazar": "0", "denunciar": "-1", "bastar": "0", "arremeter": "0", "pronunciar": "0", "moler": "0", "precipitar": "0", "reelegir": "0", "formar_parte": "0", "referir": "0", "visitar": "0", "entrar": "0", "apostar": "0", "descartar": "0", "tapar": "0", "admitir": "0", "encarecer": "0", "meter": "0", "pagar": "0", "enrarecer": "0", "penalizar": "0", "aspirar": "0", "ajustar": "0", "inventar": "0", "aparecer": "0", "ayudar": "0", "costar": "0", "acumular": "0", "desmontar": "0", "rebajar": "0",  "callar": "0", "restablecer": "1", "lamentar": "-1", "gustar": "0", "repetir": "0", "echar": "0", "averiguar": "0", "gestionar": "1", "solucionar": "1", "transportar": "0", "gastar": "0", "reservar": "0", "cubrir": "0", "concebir": "0", "propiciar": "0", "apalancar": "0", "planificar": "0", "potenciar": "0", "establecer": "0", "radicar": "0", "merecer": "0", "consolidar": "0", "optar": "0", "tardar": "0", "traer": "0", "diversificar": "0", "descargar": "0", "sobresalir": "1", "expandir": "0", "comentar": "0",  "proveer": "1", "integrar": "0", "gobernar": "0", "poseer": "0", "acaparar": "0", "acrecentar": "0", "detallar": "0", "explicitar": "1", "poner_de_manifiesto": "0", "controlar": "0", "direccionar": "0", "privilegiar": "0", "confluir": "0", "reclamar": "0", "cansar": "-1", "calmar": "1", "hartar": "-1", "arrastrar": "0", "desgastar": "-1", "arrasar": "0", "reavivar": "1", "ordenar": "1", "contener": "0", "dividir": "0", "durar": "0", "bloquear": "0", "marcar": "0", "intercambiar": "0", "regir": "0", "redoblar": "0", "descender": "0", "subrayar": "0", "enfocar": "0", "aliviar": "1", "reivindicar": "1", "ingresar": "0", "devengar": "0", "sancionar": "0", "contemplar": "0", "oscilar": "0", "gozar": "1", "sorprender": "0", "predecir": "0", "graduar": "0", "encandilar": "-1", "duchar": "0", "provocar": "0", "suspender": "0", "equivocar": "-1", "recoger": "0", "recaer": "-1", "enumerar": "0", "recuperar": "0", "empujar": "0", "adjudicar": "0":, "conmemorar": "0", "secuestrar": "-1", "ofender": "-1", "continuar": "0", "legalizar": "0", "sustituir": "0", "someter": "0", "desvanecer": "0", "retroceder": "0", "estigmatizar": "-1", "arriesgar": "0", "recortar": "0", "adicionar": "0", "atrasar": "0", "estancar": "0", "corregir": "1", "congelar": "0", "despojar": "0", "centralizar": "0", "mandar": "0", "asignar": "0", "derrochar": "-1", "quejar": "-1", "negociar": "0", "igualar": "0", "desanimar": "-1", "naufragar": "-1", "renegociar": "0", "maltratar": "-1", "modificar": "0", "atacar": "-1", "intervenir": "0", "destapar": "0", "resguardar": "0", "aplicar": "0", "remplazar": "0", "tributar": "0", "financiar": "0", "interesar": "0", "recomendar": "0", "acoger": "1", "condonar": "0", "nutrir": "0", "traicionar": "-1", "elevar": "0", "dar_cuenta": "0", "subir": "0", "dictaminar": "0", "corresponder": "0", "ascender": "0", "incorporar": "0", "tener_en_cuenta": "0", "reorientar": "0", "reafirmar": "0", "argumentar": "0", "servir": "1", "ahorrar": "0", "traducir": "0", "complementar": "0", "lucir": "0", "focalizar": "0", "dilapidar": "-1", "priorizar": "0", "permanecer": "0", "violar": "-1", "documentar": "0", "presionar": "0", "vigilar": "0", "criminalizar": "-1", "finar": "0", "destituir": "-1", "aceptar": "0", "anticipar": "0", "heredar": "0", "mover": "0", "agarrar": "0", "preguntar": "0", "disgustar": "-1", "inyectar": "0", "montar": "0", "repartir": "0", "mezclar": "0", "juntar": "0", "arrepentir": "0", "actuar": "0", "anteponer": "0", "preservar": "0", "valer": "0", "decidir": "0", "pactar": "0", "soltar": "0", "abolir": "0", "jalar": "0", "rezar": "0", "reversar": "0", "importar": "0", "usar": "0", "promediar": "0", "atribuir": "0", "colmar": "0", "sudar": "0", "equilibrar": "0", "certificar": "0", "operar": "0", "inculcar": "0", "comprometer": "0", "perdurar": "0", "administrar": "0", "observar": "0", "quitar": "0", "repensar": "0", "subsistir": "0", "circular": "0", "dar_paso": "0", "celebrar": "0", "comparecer": "0", "ceder": "1", "verificar": "0", "enlodar": "-1", "invocar": "0", "rendir": "0", "acentuar": "0", "transferir": "0", "capturar": "0", "alegar": "0", "recorrer": "0", "perseguir": "0", "saltar": "0", "cuadruplicar": "0", "exacerbar": "-1", "dar_a_conocer": "0", "mantra": "0", "prometer": "0", "dominar": "0", "designar": "0", "ilustrar": "0", "satisfacer": "1", "rezagar": "0", "dificultar": "-1", "analizar": "0", "enriquecer": "1", "desangrar": "-1", "emprender": "0", "contribuir": "0", "desprender": "0", "impactar": "0", "sugerir": "0", "carecer": "-1", "funcionar": "0", "retomar": "0", "estudiar": "0", "detectar": "0", "proseguir": "0", "voltear": "0", "averiar": "-1", "revisar": "0", "distorsionar": "-1", "rehuir": "0", "ignorar": "0", "asimilar": "0", "incidir": "0", "distar": "0", "suplir": "1", "notar": "0", "ocasionar": "0", "desfavorecer": "-1", "caracterizar": "0", "perpetuar": "0", "derivar": "0", "reflexionar": "0", "anotar": "0", "ostentar": "0", "escriturar": "0", "soportar": "0", "adoptar": "0", "sustentar": "0", "incursionar": "0", "introducir": "0", "escalar": "0", "refrendar": "0", "diseñar": "0", "viajar": "0", "conectar": "0", "contrarrestar": "0", "abarcar": "0", "renunciar": "0", "perfeccionar": "1", "alinear": "0", "asistir": "0", "remarcar": "0", "inaugurar": "0", "conjurar": "0", "describir": "0", "erar": "0", "calcular": "0", "preparar": "0", "nivelar": "0", "chocar": "0", "agudizar": "0", "concordar": "0", "dignificar": "0", "accionar": "0", "demandar": "0", "normalizar": "0", "asomar": "0", "botar": "0", "apretar": "0", "distraer": "0", "reemplazar": "0", "comenzar": "0", "estrenar": "0", "gratiscon": "0", "seleccionar": "0", "prever": "0", "confiar": "1", "materializar": "0", "debatir": "0", "fracasar": "-1", "trasladar": "0", "aplaudir": "0", "cruzar": "0", "barajar": "0", "aguardar": "0", "revolver": "0", "zigzagear": "0", "borrar": "0", "pesar": "0", "zarpar": "0", "mercar": "0", "acotar": "0", "agitar": "0", "beber": "0", "conducir": "0", "acercar": "0", "tocar": "0", "soñar": "0", "movilizar": "0", "exportar": "0", "emplear": "0", "provenir": "0", "replicar": "0", "oficializar": "0", "coordinar": "0", "pilar": "0", "exhibir": "0", "especificar": "0", "denominar": "0", "protestar": "0", "abundar": "0", "endeudar": "-1", "estructurar": "0", "convenir": "0", "pescar": "0", "proporcionar": "1", "duplicar": "0", "invadir": "0", "planear": "0", "formular": "0", "descontar": "0", "atrancar": "0", "narrar": "0", "aducir": "0", "lucrar": "0", "involucrar": "0", "militarizar": "0", "monitorear": "0", "elaborar": "0", "orientar": "0", "interpretar": "0", "componer": "0", "limitar": "0", "masificar": "0", "instalar": "0", "contestar": "0", "rajar": "0", "efectuar": "0":, "encauzar": "0", "persistir": "0", "repercutir": "0", "cesar": "0", "acoplar": "0", "plantar": "0", "conllevar": "0", "mitigar": "0", "disimular": "0", "dirigir": "0", "encarnar": "0", "circundar": "0", "encarar": "0", "enlutar": "-1", "atesorar": "0", "fluir": "0", "tirar": "0":, "displacer": "-1", "soplar": "0", "escasear": "0", "apoderar": "0", "rescatar": "0", "mutar": "0", "matar": "-1", "sumir": "0", "atenazar": "0", "practicar": "0", "pilotear": "0", "encuellando": "0", "reptar": "0", "rodar": "0", "surtir": "0", "parar": "0", "complacer": "1", "localizar": "0", "sobrar": "0", "proferir": "0", "sintetizar": "0", "acudir": "0", "alterar": "0", "convivir": "0", "posibilitar": "0", "derrotar": "0", "emigrar": "0", "convencer": "0", "disipar": "0", "formar": "0", "cursar": "0", "multiplicar": "0", "egresar": "0", "cercenar": "-1", "cimentar": "0", "implantar": "0", "estabilizar": "0", "cuantificar": "0", "dialogar": "1", "cofinanciar": "0", "interferir": "0", "marchar": "0", "obedecer": "0", "desaprovechar": "0", "subutilizar": "-1", "volver": "0", "robar": "-1", "contagiar": "0":, "tasar": "0", "inflar": "0", "catalogar": "0", "horadar": "0", "quebrar": "0", "permutar": "0", "enviar": "0", "oír": "0", "pulular": "0", "adecuar": "0", "escindir": "0", "nacer": "0", "suscitar": "0", "apreciar": "0", "demorar": "0", "acometer": "0", "detener": "0", "ambientar": "0", "doblar": "0", "condenar": "-1", "entrevistar": "0", "encender": "0", "pegar": "0", "refutar": "0", "trascender": "0", "agravar": "-1", "vengar": "-1", "agredir": "-1", "sonar": "0", "menguar": "0", "dañar": "-1", "resistir": "0", "mendigar": "-1", "retornar": "0", "saquear": "-1", "relatar": "0":, "afrontar": "0", "extraer": "0", "deshacer": "0", "cultivar": "0", "paular": "0", "disfrutar": "1", "aseverar": "0", "restringir": "0", "apuntalar": "0", "favorecer": "0", "colocar": "": "0", "prosperar": "0", "separar": "0", "disputar": "0", "dudar": "0", "clasificar": "0", "fallar": "0", "empantanar": "0", "organizar": "0", "vendar": "0", "habitar": "0", "coger": "0", "avisar": "0", "despedir": "0", "arrebatar": "-1", "lavar": "0", "autorizar": "0", "alistar": "0", "laborar": "0", "remunerar": "1", "jugar": "0", "cuidar": "0", "descubrir": "0", "arreglar": "0", "ocultar": "0", "gritar": "0", "enterar": "0", "contactar": "0", "regar": "0", "girar": "0", "hervir": "0", "lazar": "0", "convocar": "0", "abordar": "0", "dormir": "0", "retratar": "0", "rabiar": "-1", "sonreír": "1", "vislumbrar": "0", "compensar": "0", "arrojar": "0", "comer": "0", "capacitar": "0", "concurrir": "0", "sentenciar": "0", "añorar": "0", "interrumpir": "0", "contaminar": "-1", "librar": "0", "escapar": "0", "conservar": "0", "datar": "0", "reforzar": "0", "aguantar": "0", "rebuscar": "0", "portar": "0", "motivar": "0", "figurar": "0", "enchapar": "0", "manipular": "0", "malograr": "-1", "fabricar": "0", "implorar": "0", "drogar": "-1", "desbordar": "0", "forzar": "0", "aclimatar": "0", "presentir": "0", "comercializar": "0", "huir": "0", "consumir": "0", "derogar": "0", "valorizar": "0", "vinculadose": "0", "unificar": "0", "vincular": "0", "alertar": "0", "encargar": "0", "velar": "0", "golpear": "0", "enfilar": "0", "finiquitar": "0", "exaltar": "1", "ocurrir": "0", "proyectar": "0", "engordar": "0", "caber": "0"}
lista_verbos = {"pensionar": "1", "poner": "0", "mejorar": "1", "dejar": "-1", "saber": "0", "generar": "0", "ampliar": "1", "venir": "0", "disminuir": "-1", "crear": "0", "alcanzar": "1", "revertir": "1", "llegar": "0", "dar": "0", "brindar": "1", "recibir": "0", "permitir": "1", "cotizar": "0", "completar": "1", "lograr": "1", "obtener": "1", "extender": "1", "aumentar": "0", "expresar": "0", "examinar": "0", "iniciar": "0", "atravesar": "0", "levantar": "0", "compartir": "1", "asegurar": "0", "enfrentar": "0", "hablar": "0", "hacer": "0", "profundizar": "0", "ver": "0", "tramitar": "0", "visar": "0", "plantear": "0", "facilitar": "1", "apoyar": "1", "resultar": "0", "solicitar": "0", "superar": "1", "aprovechar": "0", "obligar": "-1", "ganar": "1", "necesitar": "-1", "buscar": "0", "implementar": "0", "garantizar": "1", "finalizar": "0", "afectar": "-1", "desencadenar": "0", "deber": "-1", "producir": "0", "evidenciar": "0", "regular": "0", "evitar": "0", "pasar": "0", "anunciar": "0", "dotar": "1", "contar": "0", "invertir": "0", "subsidiar": "1", "alejar": "0", "decir": "0", "firmar": "0", "beneficiar": "1", "llevar": "0", "destacar": "0", "depender": "0", "querer": "0", "adquirir": "1", "comprar": "0", "informar": "0", "entregar": "0", "recordar": "0", "constituir": "1", "invitar": "0", "aunar": "1", "crecer": "0", "implicar": "0", "cerrar": "0", "acabar": "0", "comprender": "1", "considerar": "0", "realizar": "0", "seguir": "0", "exigir": "-1", "perder": "-1", "partir": "0", "mostrar": "0", "bajar": "0", "proclamar": "0", "reducir": "-1", "reconocer": "0", "suceder": "0", "salir": "-1", "impedir": "-1", "desacelerar": "-1", "resolver": "0", "afirmar": "0", "mirar": "0", "llenar": "0", "aprobar": "1", "fortalecer": "1", "explicar": "0", "atender": "0", "esperar": "0", "llevar_a_cabo": "0", "incluir": "0", "revelar": "0", "prender": "0", "advertir": "0", "presentar": "0", "señalar": "0", "desenvolver": "0", "trabajar": "1", "contraer": "0", "desarrollar": "1", "promover": "0", "existir": "0", "desempeñar": "0", "encontrar": "0", "prevalecer": "0", "diferenciar": "0", "identificar": "0", "predominar": "0", "inferir": "0", "representar": "0", "percibir": "0", "pertenecer": "0", "concluir": "0", "impulsar": "0", "defender": "0", "lanzar": "0", "democratizar": "0", "sellar": "0", "rechazar": "0", "devolver": "0", "preferir": "0", "abandonar": "-1", "coincidir": "0", "adelantar": "0", "resaltar": "0", "recalcar": "0", "insistir": "0", "ir": "0", "hacer_ver": "0", "sufrir": "-1", "reiterar": "0", "divulgar": "0", "tratar": "0", "conformar": "0", "ejercer": "0", "pedir": "0", "desconcentrar": "-1", "expedir": "0", "blindar": "1", "proteger": "1", "suscribir": "0", "apuntar": "0", "articular": "0", "sostener": "0", "equivaler": "0", "estimar": "0", "ralentizar": "-1", "caer": "0", "mantener": "0", "suponer": "0", "indicar": "0", "registrar": "0", "cuestionar": "0", "versar": "0", "indagar": "0", "responder": "0", "quedar": "0", "respetar": "1", "sobrevivir": "1", "opinar": "0", "escribir": "0", "incrementar": "0", "prestar": "0", "proponer": "0", "creer": "0", "salvar": "1", "elegir": "0", "poder": "0", "prevenir": "1", "padecer": "-1", "combatir": "0", "requerir": "0", "asumir": "0", "consistir": "0", "votar": "0", "fundar": "0", "asesinar": "-1", "utilizar": "0", "morir": "-1", "causar": "0",  "construir": "1", "cumplir": "1", "llover": "0", "caminar": "0", "romper": "-1", "sumar": "0", "declarar": "0", "aterrizar": "0", "convertir": "0", "incautar": "-1", "desarticular": "0", "ejecutar": "0", "cometer": "0", "conquistar": "0", "faltar": "0", "conciliar": "1", "pensar": "0", "demostrar": "0", "cambiar": "0", "reunir": "0", "vender": "0", "emitir": "0", "exonerar": "1", "engañar": "-1", "discutir": "0", "entender": "0", "desaparecer": "0", "parir": "0", "acordar": "1", "concretar": "0", "pelear": "-1", "imaginar": "0", "preocupar": "-1", "rondar": "0", "avanzar": "0", "poner_de_relieve": "0", "escoger": "0", "explorar": "0", "fijar": "0", "complejizar": "-1", "tomar": "0", "desconocer": "0", "concentrar": "0", "disponer": "0", "hallar": "0", "abrir": "0", "cargar": "0", "silenciar": "0", "restituir": "1", "conocer": "0", "sacar": "-1", "confesar": "0", "erradicar": "-1", "dedicar": "0", "conseguir": "0", "sacrificar": "0", "reiniciar": "0", "evacuar": "0", "precisar": "0", "pronosticar": "0", "cifrar": "0", "estimular": "0", "afianzar": "0", "distribuir": "0", "racionalizar": "1", "valorar": "0", "sobrellevar": "0", "regresar": "0", "arrancar": "0", "agregar": "0", "ofrecer": "1", "aclarar": "0", "liderar": "1", "ubicar": "0", "sentir": "0", "evaluar": "0", "simplificar": "1", "fomentar": "1", "ocupar": "0", "surgir": "0", "dinamizar": "1", "insinuar": "0", "citar": "0", "avecinar": "0", "manejar": "0", "eliminar": "-1", "generalizar": "0", "colaborar": "0", "diferir": "0", "definir": "0", "negar": "0", "centrar": "0", "dejar_de_lado": "0", "basar": "0", "comparar": "0", "transformar": "0", "exponer": "0", "fique": "0", "regalar": "1", "usurpar": "-1",  "pretender": "0", "criticar": "-1", "legitimar": "0", "trinar": "0", "legislar": "0", "justificar": "0", "desmotivar": "-1", "frenar": "-1", "paralizar": "-1", "revivir": "0", "imponer": "-1", "vivir": "0", "incentivar": "1", "medir": "0", "reportar": "0", "escuchar": "0", "enseñar": "0", "formalizar": "0", "empezar": "0", "contratar": "0", "olvidar": "0", "acceder": "0", "ratificar": "0", "aportar": "0", "puntualizar": "0", "hacendar": "0", "calificar": "0", "participar": "0", "elogiar": "1", "restar": "0", "comprobar": "0", "agradecer": "1", "retirar": "0", "respaldar": "1", "filtrar": "0", "otorgar": "1", "añadir": "0", "acatar": "0", "cobrar": "0", "luchar": "0", "sembrar": "0", "cosechar": "1", "publicar": "0", "mencionar": "0", "acompañar": "0", "protagonizar": "0", "conversar": "0", "significar": "0", "delinear": "0", "descalificar": "-1", "correr": "0", "estrechar": "0", "leer": "0", "manifestar": "0", "transcurrir": "0", "inquietar": "0", "llamar": "0", "explotar": "0", "disparar": "-1", "experimentar": "0", "reflejar": "0", "amenazar": "-1", "confirmar": "0", "destruir": "-1", "rodrigar": "0", "determinar": "0", "terminar": "0", "destinar": "0", "reparar": "1", "enfatizar": "0", "desplazar": "0", "denunciar": "-1", "bastar": "0", "arremeter": "0", "pronunciar": "0", "moler": "0", "precipitar": "0", "reelegir": "0", "formar_parte": "0", "referir": "0", "visitar": "0", "entrar": "0", "apostar": "0", "descartar": "0", "tapar": "0", "admitir": "0", "encarecer": "0", "meter": "0", "pagar": "0", "enrarecer": "0", "penalizar": "0", "aspirar": "0", "ajustar": "0", "inventar": "0", "aparecer": "0", "ayudar": "0", "costar": "0", "acumular": "0", "desmontar": "0", "rebajar": "0",  "callar": "0", "restablecer": "1", "lamentar": "-1", "gustar": "0", "repetir": "0", "echar": "0", "averiguar": "0", "gestionar": "1", "solucionar": "1", "transportar": "0", "gastar": "0", "reservar": "0", "cubrir": "0", "concebir": "0", "propiciar": "0", "apalancar": "0", "planificar": "0", "potenciar": "0", "establecer": "0", "radicar": "0", "merecer": "0", "consolidar": "0", "optar": "0", "tardar": "0", "traer": "0", "diversificar": "0", "descargar": "0", "sobresalir": "1", "expandir": "0", "comentar": "0",  "proveer": "1", "integrar": "0", "gobernar": "0", "poseer": "0", "acaparar": "0", "acrecentar": "0", "detallar": "0", "explicitar": "1", "poner_de_manifiesto": "0", "controlar": "0", "direccionar": "0", "privilegiar": "0", "confluir": "0", "reclamar": "0", "cansar": "-1", "calmar": "1", "hartar": "-1", "arrastrar": "0", "desgastar": "-1", "arrasar": "0", "reavivar": "1", "ordenar": "1", "contener": "0", "dividir": "0", "durar": "0", "bloquear": "0", "marcar": "0", "intercambiar": "0", "regir": "0", "redoblar": "0",  "descender": "0", "subrayar": "0", "enfocar": "0", "aliviar": "1", "reivindicar": "1", "ingresar": "0", "devengar": "0", "sancionar": "0", "contemplar": "0", "oscilar": "0", "gozar": "1", "sorprender": "0", "predecir": "0", "graduar": "0", "encandilar": "-1", "duchar": "0", "provocar": "0", "suspender": "0", "equivocar": "-1", "recoger": "0", "recaer": "-1", "enumerar": "0", "recuperar": "0", "empujar": "0", "adjudicar": "0", "conmemorar": "0", "secuestrar": "-1", "ofender": "-1", "continuar": "0", "legalizar": "0", "sustituir": "0", "someter": "0", "desvanecer": "0", "retroceder": "0", "estigmatizar": "-1", "arriesgar": "0", "recortar": "0", "adicionar": "0", "atrasar": "0", "estancar": "0", "corregir": "1", "congelar": "0", "despojar": "0", "centralizar": "0", "mandar": "0", "asignar": "0", "derrochar": "-1", "quejar": "-1", "negociar": "0", "igualar": "0", "desanimar": "-1", "naufragar": "-1", "renegociar": "0", "maltratar": "-1", "modificar": "0", "atacar": "-1", "intervenir": "0", "destapar": "0", "resguardar": "0", "aplicar": "0", "remplazar": "0", "tributar": "0", "financiar": "0", "interesar": "0", "recomendar": "0", "acoger": "1", "condonar": "0", "nutrir": "0", "traicionar": "-1", "elevar": "0", "dar_cuenta": "0", "subir": "0", "dictaminar": "0", "corresponder": "0", "ascender": "0", "incorporar": "0", "tener_en_cuenta": "0", "reorientar": "0", "reafirmar": "0", "argumentar": "0", "servir": "1", "ahorrar": "0", "traducir": "0", "complementar": "0", "lucir": "0", "focalizar": "-1", "dilapidar": "-1", "priorizar": "0", "permanecer": "0", "violar": "-1", "documentar": "0", "presionar": "0", "vigilar": "0", "criminalizar": "-1", "finar": "0", "destituir": "-1", "aceptar": "0", "anticipar": "0", "heredar": "0", "mover": "0",  "agarrar": "0", "preguntar": "0", "disgustar": "-1", "inyectar": "0", "montar": "0", "repartir": "0", "mezclar": "0", "juntar": "0", "arrepentir": "0", "actuar": "0", "anteponer": "0", "preservar": "0", "valer": "0", "decidir": "0", "pactar": "0", "soltar": "0", "abolir": "0", "jalar": "0", "rezar": "0", "reversar": "0", "importar": "0", "usar": "0", "promediar": "0", "atribuir": "0", "colmar": "0", "sudar": "0", "equilibrar": "0", "certificar": "0", "operar": "0", "inculcar": "0", "comprometer": "0", "perdurar": "0", "administrar": "0", "observar": "0", "quitar": "0", "repensar": "0", "subsistir": "0", "circular": "0", "dar_paso": "0", "celebrar": "0", "comparecer": "0", "ceder": "1", "verificar": "0", "enlodar": "-1", "invocar": "0", "rendir": "0", "acentuar": "0", "transferir": "0", "capturar": "0", "alegar": "0", "recorrer": "0", "perseguir": "0", "saltar": "0", "cuadruplicar": "0", "exacerbar": "-1", "dar_a_conocer": "0", "mantra": "0", "prometer": "0", "dominar": "0", "designar": "0", "ilustrar": "0", "satisfacer": "1", "rezagar": "0", "dificultar": "-1", "analizar": "0", "enriquecer": "1", "desangrar": "-1", "emprender": "0", "contribuir": "0", "desprender": "0", "impactar": "0", "sugerir": "0", "carecer": "-1", "funcionar": "0", "retomar": "0", "estudiar": "0", "detectar": "0", "proseguir": "0", "voltear": "0", "averiar": "-1", "revisar": "0", "distorsionar": "-1", "rehuir": "0", "ignorar": "0", "asimilar": "0", "incidir": "0", "distar": "0", "suplir": "1", "notar": "0", "ocasionar": "0", "desfavorecer": "-1", "caracterizar": "0", "perpetuar": "0", "derivar": "0", "reflexionar": "0", "anotar": "0", "ostentar": "0", "escriturar": "0", "soportar": "0", "adoptar": "0",  "sustentar": "0", "incursionar": "0", "introducir": "0", "escalar": "0", "refrendar": "0", "diseñar": "0", "viajar": "0", "conectar": "0", "contrarrestar": "0", "abarcar": "0", "renunciar": "0", "perfeccionar": "1", "alinear": "0", "asistir": "0", "remarcar": "0", "inaugurar": "0", "conjurar": "0", "describir": "0", "erar": "0", "calcular": "0", "preparar": "0", "nivelar": "0", "chocar": "0", "agudizar": "-1", "concordar": "0", "dignificar": "0", "accionar": "0", "demandar": "0", "normalizar": "0", "asomar": "0", "botar": "0", "apretar": "0", "distraer": "0", "reemplazar": "0", "comenzar": "0", "estrenar": "0", "gratiscon": "0", "seleccionar": "0", "prever": "0", "confiar": "1", "materializar": "0", "debatir": "0", "fracasar": "-1", "trasladar": "0", "aplaudir": "0", "cruzar": "0", "barajar": "0", "aguardar": "0", "revolver": "0", "zigzagear": "0", "borrar": "0", "pesar": "0", "zarpar": "0", "mercar": "0", "acotar": "0", "agitar": "0", "beber": "0", "conducir": "0", "acercar": "0", "tocar": "0", "soñar": "0", "movilizar": "0", "exportar": "0", "emplear": "0", "provenir": "0", "replicar": "0", "oficializar": "0", "coordinar": "0", "pilar": "0", "exhibir": "0", "especificar": "0", "denominar": "0", "protestar": "0", "abundar": "0", "endeudar": "-1", "estructurar": "0", "convenir": "0", "pescar": "0", "proporcionar": "1", "duplicar": "0", "invadir": "0", "planear": "0", "formular": "0", "descontar": "0", "atrancar": "0", "narrar": "0", "aducir": "0", "lucrar": "0", "involucrar": "0", "militarizar": "0", "monitorear": "0", "elaborar": "0", "orientar": "0", "interpretar": "0", "componer": "0", "limitar": "0", "masificar": "0", "instalar": "0", "contestar": "0", "rajar": "0",  "efectuar": "0", "encauzar": "0", "persistir": "0", "repercutir": "0", "cesar": "0", "acoplar": "0", "plantar": "0", "conllevar": "0", "mitigar": "0", "disimular": "0", "dirigir": "0", "encarnar": "0", "circundar": "0", "encarar": "0", "enlutar": "-1", "atesorar": "0", "fluir": "0", "tirar": "0", "displacer": "-1", "soplar": "0", "escasear": "0", "apoderar": "0", "rescatar": "0", "mutar": "0", "matar": "-1", "sumir": "0", "atenazar": "0", "practicar": "0", "pilotear": "0", "encuellando": "0", "reptar": "0", "rodar": "0", "surtir": "0", "parar": "0", "complacer": "1", "localizar": "0", "sobrar": "0", "proferir": "0", "sintetizar": "0", "acudir": "0", "alterar": "0", "convivir": "0", "posibilitar": "0", "derrotar": "0", "emigrar": "0", "convencer": "0", "disipar": "0", "formar": "0", "cursar": "0", "multiplicar": "0", "egresar": "0", "cercenar": "-1", "cimentar": "0", "implantar": "0", "estabilizar": "0", "cuantificar": "0", "dialogar": "1", "cofinanciar": "0", "interferir": "0", "marchar": "0", "obedecer": "0", "desaprovechar": "0", "subutilizar": "-1", "volver": "0", "robar": "-1", "contagiar": "0", "tasar": "0", "inflar": "0", "catalogar": "0", "horadar": "0", "quebrar": "0", "permutar": "0", "enviar": "0", "oír": "0", "pulular": "0", "adecuar": "0", "escindir": "0", "nacer": "0", "suscitar": "0", "apreciar": "0", "demorar": "0", "acometer": "0", "detener": "0", "ambientar": "0", "doblar": "0", "condenar": "-1", "entrevistar": "0", "encender": "0", "pegar": "0", "refutar": "0", "trascender": "0", "agravar": "-1", "vengar": "-1", "agredir": "-1", "sonar": "0", "menguar": "0", "dañar": "-1", "resistir": "0", "mendigar": "-1", "retornar": "0",  "saquear": "-1", "relatar": "0", "afrontar": "0", "extraer": "0", "deshacer": "0", "cultivar": "0", "paular": "0", "disfrutar": "1", "aseverar": "0", "restringir": "0", "apuntalar": "0", "favorecer": "0", "colocar": "0", "prosperar": "0", "separar": "0", "disputar": "0", "dudar": "0", "clasificar": "0", "fallar": "0", "empantanar": "0", "organizar": "0", "vendar": "0", "habitar": "0", "coger": "0", "avisar": "0", "despedir": "0", "arrebatar": "-1", "lavar": "0", "autorizar": "0", "alistar": "0", "laborar": "0", "remunerar": "1", "jugar": "0", "cuidar": "0", "descubrir": "0", "arreglar": "0", "ocultar": "0", "gritar": "0", "enterar": "0", "contactar": "0", "regar": "0", "girar": "0", "hervir": "0", "lazar": "0", "convocar": "0", "abordar": "0", "dormir": "0", "retratar": "0", "rabiar": "-1", "sonreír": "1",  "vislumbrar": "0", "compensar": "0", "arrojar": "0", "comer": "0", "capacitar": "0", "concurrir": "0", "sentenciar": "0", "añorar": "0", "interrumpir": "0", "contaminar": "-1", "librar": "0", "escapar": "0", "conservar": "0", "datar": "0", "reforzar": "0", "aguantar": "0", "rebuscar": "0", "portar": "0", "motivar": "0", "figurar": "0", "enchapar": "0", "manipular": "0", "malograr": "-1", "fabricar": "0", "implorar": "0", "drogar": "-1", "desbordar": "0", "forzar": "-1", "aclimatar": "0", "presentir": "0", "comercializar": "0", "huir": "0", "consumir": "0", "derogar": "0", "valorizar": "0", "vinculadose": "0", "unificar": "0", "vincular": "0", "alertar": "0", "encargar": "0", "velar": "0", "golpear": "0", "enfilar": "0", "finiquitar": "0", "exaltar": "1", "ocurrir": "0", "proyectar": "0", "engordar": "0", "caber": "0", "debilitar": "-1"}
#lista_verbos = dict()
#lista_verbos = {"pensionar": "10", "poner": "0", "mejorar": "10", "dejar": "-1", "saber": "0", "generar": "0", "ampliar": "1", "venir": "0", "disminuir": "-1", "crear": "0", "alcanzar": "1", "revertir": "1", "llegar": "0", "dar": "0", "brindar": "1", "recibir": "0", "permitir": "1", "cotizar": "0", "completar": "1", "lograr": "1", "obtener": "1", "extender": "1", "aumentar": "0", "expresar": "0", "examinar": "0", "iniciar": "0", "atravesar": "0", "levantar": "0", "compartir": "1", "asegurar": "0", "enfrentar": "0", "hablar": "0", "hacer": "0", "profundizar": "0", "ver": "0", "tramitar": "0", "visar": "0", "plantear": "0", "facilitar": "1", "apoyar": "1", "resultar": "0", "solicitar": "0", "superar": "1", "aprovechar": "0", "obligar": "-1", "ganar": "1", "necesitar": "-1", "buscar": "0", "implementar": "0", "garantizar": "1", "finalizar": "0", "afectar": "-1", "desencadenar": "0", "deber": "-1", "producir": "0", "evidenciar": "0", "regular": "0", "evitar": "0", "pasar": "0", "anunciar": "0", "dotar": "1", "contar": "0", "invertir": "0", "subsidiar": "1", "alejar": "0", "decir": "0", "firmar": "0", "beneficiar": "1", "llevar": "0", "destacar": "0", "depender": "0", "querer": "0", "adquirir": "1", "comprar": "0", "informar": "0", "entregar": "0", "recordar": "0", "constituir": "1", "invitar": "0", "aunar": "1", "crecer": "0", "implicar": "0", "cerrar": "0", "acabar": "0", "comprender": "1", "considerar": "0", "realizar": "0", "seguir": "0", "exigir": "-1", "perder": "-1", "partir": "0", "mostrar": "0", "bajar": "0", "proclamar": "0", "reducir": "0", "reconocer": "0", "suceder": "0", "salir": "-1", "impedir": "-1", "desacelerar": "-1", "resolver": "0", "afirmar": "0", "mirar": "0", "llenar": "0", "aprobar": "1", "fortalecer": "1", "explicar": "0", "atender": "0", "esperar": "0", "llevar_a_cabo": "0", "incluir": "0", "revelar": "0", "prender": "0", "advertir": "0", "presentar": "0", "señalar": "0", "desenvolver": "0", "trabajar": "1", "contraer": "0", "desarrollar": "1", "promover": "0", "existir": "0", "desempeñar": "0", "encontrar": "0", "prevalecer": "0", "diferenciar": "0", "identificar": "0", "predominar": "0", "inferir": "0", "representar": "0", "percibir": "0", "pertenecer": "0", "concluir": "0", "impulsar": "0", "defender": "0", "lanzar": "0", "democratizar": "0", "sellar": "0", "rechazar": "0", "devolver": "0", "preferir": "0", "abandonar": "-1", "coincidir": "0", "adelantar": "0", "resaltar": "0", "recalcar": "0", "insistir": "0", "ir": "0", "hacer_ver": "0", "sufrir": "-1", "reiterar": "0", "divulgar": "0", "tratar": "0", "conformar": "0", "ejercer": "0", "pedir": "0", "desconcentrar": "-1", "expedir": "0", "blindar": "1", "proteger": "1", "suscribir": "0", "apuntar": "0", "articular": "0", "sostener": "0", "equivaler": "0", "estimar": "0", "ralentizar": "-1", "caer": "0", "mantener": "0", "suponer": "0", "indicar": "0", "registrar": "0", "cuestionar": "0", "versar": "0", "indagar": "0", "responder": "0", "quedar": "0", "respetar": "1", "sobrevivir": "1", "opinar": "0", "escribir": "0", "incrementar": "0", "prestar": "0", "proponer": "0", "creer": "0", "salvar": "1", "elegir": "0", "poder": "0", "prevenir": "1", "padecer": "-1", "combatir": "0", "requerir": "0", "asumir": "0", "consistir": "0", "votar": "0", "fundar": "0", "asesinar": "-1", "utilizar": "0", "morir": "-1", "causar": "0",  "construir": "1", "cumplir": "1", "llover": "0", "caminar": "0", "romper": "-1", "sumar": "0", "declarar": "0", "aterrizar": "0", "convertir": "0", "incautar": "-1", "desarticular": "0", "ejecutar": "0", "cometer": "0", "conquistar": "0", "faltar": "0", "conciliar": "1", "pensar": "0", "demostrar": "0", "cambiar": "0", "reunir": "0", "vender": "0", "emitir": "0", "exonerar": "1", "engañar": "-1", "discutir": "0", "entender": "0", "desaparecer": "0", "parir": "0", "acordar": "1", "concretar": "0", "pelear": "-1", "imaginar": "0", "preocupar": "-1", "rondar": "0", "avanzar": "0", "poner_de_relieve": "0", "escoger": "0", "explorar": "0", "fijar": "0", "complejizar": "-1", "tomar": "0", "desconocer": "0", "concentrar": "0", "disponer": "0", "hallar": "0", "abrir": "0", "cargar": "0", "silenciar": "0", "restituir": "1", "conocer": "0", "sacar": "-1", "confesar": "0", "erradicar": "1", "dedicar": "0", "conseguir": "0", "sacrificar": "0", "reiniciar": "0", "evacuar": "0", "precisar": "0", "pronosticar": "0", "cifrar": "0", "estimular": "0", "afianzar": "0", "distribuir": "0", "racionalizar": "1", "valorar": "0", "sobrellevar": "0", "regresar": "0", "arrancar": "0", "agregar": "0", "ofrecer": "1", "aclarar": "0", "liderar": "1", "ubicar": "0", "sentir": "0", "evaluar": "0", "simplificar": "1", "fomentar": "1", "ocupar": "0", "surgir": "0", "dinamizar": "1", "insinuar": "0", "citar": "0", "avecinar": "0", "manejar": "0", "eliminar": "-1", "generalizar": "0", "colaborar": "0", "diferir": "0", "definir": "0", "negar": "0", "centrar": "0", "dejar_de_lado": "0", "basar": "0", "comparar": "0", "transformar": "0", "exponer": "0", "fique": "0", "regalar": "1", "usurpar": "-1",  "pretender": "0", "criticar": "-1", "legitimar": "0", "trinar": "0", "legislar": "0", "justificar": "0", "desmotivar": "-1", "frenar": "-1", "paralizar": "-1", "revivir": "0", "imponer": "-1", "vivir": "0", "incentivar": "1", "medir": "0", "reportar": "0", "escuchar": "0", "enseñar": "0", "formalizar": "0", "empezar": "0", "contratar": "0", "olvidar": "0", "acceder": "0", "ratificar": "0", "aportar": "0", "puntualizar": "0", "hacendar": "0", "calificar": "0", "participar": "0", "elogiar": "1", "restar": "0", "comprobar": "0", "agradecer": "1", "retirar": "0", "respaldar": "1", "filtrar": "0", "otorgar": "1", "añadir": "0", "acatar": "0", "cobrar": "0", "luchar": "0", "sembrar": "0", "cosechar": "1", "publicar": "0", "mencionar": "0", "acompañar": "0", "protagonizar": "0", "conversar": "0", "significar": "0", "delinear": "0", "descalificar": "-1", "correr": "0", "estrechar": "0", "leer": "0", "manifestar": "0", "transcurrir": "0", "inquietar": "0", "llamar": "0", "explotar": "0", "disparar": "-1", "experimentar": "0", "reflejar": "0", "amenazar": "-1", "confirmar": "0", "destruir": "-1", "rodrigar": "0", "determinar": "0", "terminar": "0", "destinar": "0", "reparar": "1", "enfatizar": "0", "desplazar": "0", "denunciar": "-1", "bastar": "0", "arremeter": "0", "pronunciar": "0", "moler": "0", "precipitar": "0", "reelegir": "0", "formar_parte": "0", "referir": "0", "visitar": "0", "entrar": "0", "apostar": "0", "descartar": "0", "tapar": "0", "admitir": "0", "encarecer": "0", "meter": "0", "pagar": "0", "enrarecer": "0", "penalizar": "0", "aspirar": "0", "ajustar": "0", "inventar": "0", "aparecer": "0", "ayudar": "0", "costar": "0", "acumular": "0", "desmontar": "0", "rebajar": "0",  "callar": "0", "restablecer": "1", "lamentar": "-1", "gustar": "0", "repetir": "0", "echar": "0", "averiguar": "0", "gestionar": "1", "solucionar": "1", "transportar": "0", "gastar": "0", "reservar": "0", "cubrir": "0", "concebir": "0", "propiciar": "0", "apalancar": "0", "planificar": "0", "potenciar": "0", "establecer": "0", "radicar": "0", "merecer": "0", "consolidar": "0", "optar": "0", "tardar": "0", "traer": "0", "diversificar": "0", "descargar": "0", "sobresalir": "1", "expandir": "0", "comentar": "0",  "proveer": "1", "integrar": "0", "gobernar": "0", "poseer": "0", "acaparar": "0", "acrecentar": "0", "detallar": "0", "explicitar": "1", "poner_de_manifiesto": "0", "controlar": "0", "direccionar": "0", "privilegiar": "0", "confluir": "0", "reclamar": "0", "cansar": "-1", "calmar": "1", "hartar": "-1", "arrastrar": "0", "desgastar": "-1", "arrasar": "0", "reavivar": "1", "ordenar": "1", "contener": "0", "dividir": "0", "durar": "0", "bloquear": "0", "marcar": "0", "intercambiar": "0", "regir": "0", "redoblar": "0",  "descender": "0", "subrayar": "0", "enfocar": "0", "aliviar": "1", "reivindicar": "1", "ingresar": "0", "devengar": "0", "sancionar": "0", "contemplar": "0", "oscilar": "0", "gozar": "1", "sorprender": "0", "predecir": "0", "graduar": "0", "encandilar": "-1", "duchar": "0", "provocar": "0", "suspender": "0", "equivocar": "-1", "recoger": "0", "recaer": "-1", "enumerar": "0", "recuperar": "0", "empujar": "0", "adjudicar": "0", "conmemorar": "0", "secuestrar": "-1", "ofender": "-1", "continuar": "0", "legalizar": "0", "sustituir": "0", "someter": "0", "desvanecer": "0", "retroceder": "0", "estigmatizar": "-1", "arriesgar": "0", "recortar": "0", "adicionar": "0", "atrasar": "0", "estancar": "0", "corregir": "1", "congelar": "0", "despojar": "0", "centralizar": "0", "mandar": "0", "asignar": "0", "derrochar": "-1", "quejar": "-1", "negociar": "0", "igualar": "0", "desanimar": "-1", "naufragar": "-1", "renegociar": "0", "maltratar": "-1", "modificar": "0", "atacar": "-1", "intervenir": "0", "destapar": "0", "resguardar": "0", "aplicar": "0", "remplazar": "0", "tributar": "0", "financiar": "0", "interesar": "0", "recomendar": "0", "acoger": "1", "condonar": "0", "nutrir": "0", "traicionar": "-1", "elevar": "0", "dar_cuenta": "0", "subir": "0", "dictaminar": "0", "corresponder": "0", "ascender": "0", "incorporar": "0", "tener_en_cuenta": "0", "reorientar": "0", "reafirmar": "0", "argumentar": "0", "servir": "1", "ahorrar": "0", "traducir": "0", "complementar": "0", "lucir": "0", "focalizar": "-1", "dilapidar": "-1", "priorizar": "0", "permanecer": "0", "violar": "-1", "documentar": "0", "presionar": "0", "vigilar": "0", "criminalizar": "-1", "finar": "0", "destituir": "-1", "aceptar": "0", "anticipar": "0", "heredar": "0", "mover": "0",  "agarrar": "0", "preguntar": "0", "disgustar": "-1", "inyectar": "0", "montar": "0", "repartir": "0", "mezclar": "0", "juntar": "0", "arrepentir": "0", "actuar": "0", "anteponer": "0", "preservar": "0", "valer": "0", "decidir": "0", "pactar": "0", "soltar": "0", "abolir": "0", "jalar": "0", "rezar": "0", "reversar": "0", "importar": "0", "usar": "0", "promediar": "0", "atribuir": "0", "colmar": "0", "sudar": "0", "equilibrar": "0", "certificar": "0", "operar": "0", "inculcar": "0", "comprometer": "0", "perdurar": "0", "administrar": "0", "observar": "0", "quitar": "0", "repensar": "0", "subsistir": "0", "circular": "0", "dar_paso": "0", "celebrar": "0", "comparecer": "0", "ceder": "1", "verificar": "0", "enlodar": "-1", "invocar": "0", "rendir": "0", "acentuar": "0", "transferir": "0", "capturar": "0", "alegar": "0", "recorrer": "0", "perseguir": "0", "saltar": "0", "cuadruplicar": "0", "exacerbar": "-1", "dar_a_conocer": "0", "mantra": "0", "prometer": "0", "dominar": "0", "designar": "0", "ilustrar": "0", "satisfacer": "1", "rezagar": "0", "dificultar": "-1", "analizar": "0", "enriquecer": "1", "desangrar": "-1", "emprender": "0", "contribuir": "0", "desprender": "0", "impactar": "0", "sugerir": "0", "carecer": "-1", "funcionar": "0", "retomar": "0", "estudiar": "0", "detectar": "0", "proseguir": "0", "voltear": "0", "averiar": "-1", "revisar": "0", "distorsionar": "-1", "rehuir": "0", "ignorar": "0", "asimilar": "0", "incidir": "0", "distar": "0", "suplir": "1", "notar": "0", "ocasionar": "0", "desfavorecer": "-1", "caracterizar": "0", "perpetuar": "0", "derivar": "0", "reflexionar": "0", "anotar": "0", "ostentar": "0", "escriturar": "0", "soportar": "0", "adoptar": "0",  "sustentar": "0", "incursionar": "0", "introducir": "0", "escalar": "0", "refrendar": "0", "diseñar": "0", "viajar": "0", "conectar": "0", "contrarrestar": "0", "abarcar": "0", "renunciar": "0", "perfeccionar": "1", "alinear": "0", "asistir": "0", "remarcar": "0", "inaugurar": "0", "conjurar": "0", "describir": "0", "erar": "0", "calcular": "0", "preparar": "0", "nivelar": "0", "chocar": "0", "agudizar": "-1", "concordar": "0", "dignificar": "0", "accionar": "0", "demandar": "0", "normalizar": "0", "asomar": "0", "botar": "0", "apretar": "0", "distraer": "0", "reemplazar": "0", "comenzar": "0", "estrenar": "0", "gratiscon": "0", "seleccionar": "0", "prever": "0", "confiar": "1", "materializar": "0", "debatir": "0", "fracasar": "-1", "trasladar": "0", "aplaudir": "0", "cruzar": "0", "barajar": "0", "aguardar": "0", "revolver": "0", "zigzagear": "0", "borrar": "0", "pesar": "0", "zarpar": "0", "mercar": "0", "acotar": "0", "agitar": "0", "beber": "0", "conducir": "0", "acercar": "0", "tocar": "0", "soñar": "0", "movilizar": "0", "exportar": "0", "emplear": "0", "provenir": "0", "replicar": "0", "oficializar": "0", "coordinar": "0", "pilar": "0", "exhibir": "0", "especificar": "0", "denominar": "0", "protestar": "0", "abundar": "0", "endeudar": "-1", "estructurar": "0", "convenir": "0", "pescar": "0", "proporcionar": "1", "duplicar": "0", "invadir": "0", "planear": "0", "formular": "0", "descontar": "0", "atrancar": "0", "narrar": "0", "aducir": "0", "lucrar": "0", "involucrar": "0", "militarizar": "0", "monitorear": "0", "elaborar": "0", "orientar": "0", "interpretar": "0", "componer": "0", "limitar": "0", "masificar": "0", "instalar": "0", "contestar": "0", "rajar": "0",  "efectuar": "0", "encauzar": "0", "persistir": "0", "repercutir": "0", "cesar": "0", "acoplar": "0", "plantar": "0", "conllevar": "0", "mitigar": "0", "disimular": "0", "dirigir": "0", "encarnar": "0", "circundar": "0", "encarar": "0", "enlutar": "-1", "atesorar": "0", "fluir": "0", "tirar": "0", "displacer": "-1", "soplar": "0", "escasear": "0", "apoderar": "0", "rescatar": "0", "mutar": "0", "matar": "-1", "sumir": "0", "atenazar": "0", "practicar": "0", "pilotear": "0", "encuellando": "0", "reptar": "0", "rodar": "0", "surtir": "0", "parar": "0", "complacer": "1", "localizar": "0", "sobrar": "0", "proferir": "0", "sintetizar": "0", "acudir": "0", "alterar": "0", "convivir": "0", "posibilitar": "0", "derrotar": "0", "emigrar": "0", "convencer": "0", "disipar": "0", "formar": "0", "cursar": "0", "multiplicar": "0", "egresar": "0", "cercenar": "-1", "cimentar": "0", "implantar": "0", "estabilizar": "0", "cuantificar": "0", "dialogar": "1", "cofinanciar": "0", "interferir": "0", "marchar": "0", "obedecer": "0", "desaprovechar": "0", "subutilizar": "-1", "volver": "0", "robar": "-1", "contagiar": "0", "tasar": "0", "inflar": "0", "catalogar": "0", "horadar": "0", "quebrar": "0", "permutar": "0", "enviar": "0", "oír": "0", "pulular": "0", "adecuar": "0", "escindir": "0", "nacer": "0", "suscitar": "0", "apreciar": "0", "demorar": "0", "acometer": "0", "detener": "0", "ambientar": "0", "doblar": "0", "condenar": "-1", "entrevistar": "0", "encender": "0", "pegar": "0", "refutar": "0", "trascender": "0", "agravar": "-1", "vengar": "-1", "agredir": "-1", "sonar": "0", "menguar": "0", "dañar": "-1", "resistir": "0", "mendigar": "-1", "retornar": "0",  "saquear": "-1", "relatar": "0", "afrontar": "0", "extraer": "0", "deshacer": "0", "cultivar": "0", "paular": "0", "disfrutar": "1", "aseverar": "0", "restringir": "0", "apuntalar": "0", "favorecer": "0", "colocar": "0", "prosperar": "0", "separar": "0", "disputar": "0", "dudar": "0", "clasificar": "0", "fallar": "0", "empantanar": "0", "organizar": "0", "vendar": "0", "habitar": "0", "coger": "0", "avisar": "0", "despedir": "0", "arrebatar": "-1", "lavar": "0", "autorizar": "0", "alistar": "0", "laborar": "0", "remunerar": "1", "jugar": "0", "cuidar": "0", "descubrir": "0", "arreglar": "0", "ocultar": "0", "gritar": "0", "enterar": "0", "contactar": "0", "regar": "0", "girar": "0", "hervir": "0", "lazar": "0", "convocar": "0", "abordar": "0", "dormir": "0", "retratar": "0", "rabiar": "-1", "sonreír": "1",  "vislumbrar": "0", "compensar": "0", "arrojar": "0", "comer": "0", "capacitar": "0", "concurrir": "0", "sentenciar": "0", "añorar": "0", "interrumpir": "0", "contaminar": "-1", "librar": "0", "escapar": "0", "conservar": "0", "datar": "0", "reforzar": "0", "aguantar": "0", "rebuscar": "0", "portar": "0", "motivar": "0", "figurar": "0", "enchapar": "0", "manipular": "0", "malograr": "-1", "fabricar": "0", "implorar": "0", "drogar": "-1", "desbordar": "0", "forzar": "-1", "aclimatar": "0", "presentir": "0", "comercializar": "0", "huir": "0", "consumir": "0", "derogar": "0", "valorizar": "0", "vinculadose": "0", "unificar": "0", "vincular": "0", "alertar": "0", "encargar": "0", "velar": "0", "golpear": "0", "enfilar": "0", "finiquitar": "0", "exaltar": "1", "ocurrir": "0", "proyectar": "0", "engordar": "0", "caber": "0", "debilitar": "-1"}

#Conmutadores de polaridad de la frase previa y de la frase actual
# Incluir "pero" da mucho ruido y errores, es muy dificil porque no siempre es conmutador.
shifters_frase_previa = ['no_obstante', 'sin embargo', 'aunque'] 
#shifters_frase_actual = ['pese_a', 'poco', 'poca', 'ninguno', 'ninguna', 'nunca', 'pero']
shifters_frase_actual = ['pese_a', ' poco ', ' poca ', ' ninguno ', ' ninguna ', ' nunca ', ' pero ', ' poco.', ' poca.', ' ninguno.', ' ninguna.', ' nunca.']

for l4 in parsedFile:

	#Para el grupo adj_
	if "adj_" in l4:
		cuenta5 = True
	
	if cuenta5 == True and "[" in l4:
		cuentaCorchetesAdj = cuentaCorchetesAdj + 1
	
	if cuenta5 == True and "]" in l4:
		cuentaCorchetesAdj = cuentaCorchetesAdj - 1	

	if ("(" in l4) and (cuenta5 == True):
		
		lineaParsed = re.sub('.*\(', "", l4).split(" ")
		
		s_adj_forma.append(lineaParsed[0])		#Forma
		s_adj.append(lineaParsed[1])		#Lemma
		tag_s_adj.append(lineaParsed[2])	#POS
		
		if len(lineaParsed) > 3:

			id_ = re.sub('-.*\n', '', lineaParsed[3])
		
		else:
			
			id_ = ''

		if id_ == '':
			id_ = "NoSentiTag"
		
		IDs_s_adj.append(id_)
	
	if cuentaCorchetesAdj == 0 and cuenta5 == True:

		patternAdj = ' '.join(s_adj) 

		#SintagmaAdjFile.write(adjunto+'\t'+patternAdj+'\n')
		SintagmaAdjFile.write(patternAdj+'\n')


		#tagAdj
		cargaAdjPos = []
		cargaAdjNeg = []
		sectionAdj = []
		id_frase = []
		
		mapFile = open("sentiTaggedFile.txt", "r")

		#Para los adjetivos

		cntAdj = 0

		for ad in s_adj_forma:
			
			for st in mapFile:
						
				cntAdj += 1	#Con esto controlamos en que linea del archivo etiquetado vamos para no volver a tenerla en cuenta
						
				line = st.split("\t")
		
				if ad[:-1] in line[0] and cntAdj > lineaAdj:

					#ESTA PARTE ES MUY IMPORTANTE
					#AQUI SE TIENE EN CUENTA LA NEGACION DEL PATRON Y SE INVIERTE LA POLARIDAD DE CADA TOKEN DEL ATRIBUTO SI EL
					#PATRÓN ESTÁ NEGADO
							
					if negacion == False:
						cargaAdjPos.append(line[3])
						cargaAdjNeg.append(line[4])
					else:
						cargaAdjPos.append(line[4])
						cargaAdjNeg.append(line[3])

					sectionAdj.append(line[5])
					#print sectionAdj
					#tagAtr.append(line[1])

					id_frase.append(line[6][:-1])
					#print id_frase

					lineaAdj = cntAdj
								
					break

		#Para imprimir el Part-of-Speech y las cargas correspondientes a cada token
		cargasSintagmasAdjFilePos.write('\t'.join(tag_s_adj)+"\t"+'\t'.join(cargaAdjPos)+'\t'+sectionAdj[0]+'\t'+id_frase[-1]+'\n')
		cargasSintagmasAdjFileNeg.write('\t'.join(tag_s_adj)+"\t"+'\t'.join(cargaAdjNeg)+'\t'+sectionAdj[0]+'\t'+id_frase[-1]+'\n')

		#cargasSintagmasAdjFilePos.write('\t'.join(tag_s_adj)+"\t"+'\t'.join(cargaAdjPos)+'\t'+sectionAdj[0]+'\n')
		#cargasSintagmasAdjFileNeg.write('\t'.join(tag_s_adj)+"\t"+'\t'.join(cargaAdjNeg)+'\t'+sectionAdj[0]+'\n')


		s_adj = []
		s_adj_forma = []
		tag_s_adj = []
		IDs_s_adj = []
		cuenta5 = False
	
	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	'''
	#Para el grupo v_part
	if "+parti" in l4 or "+forma-ger" in l4:
		cuenta6 = True
	
	if cuenta6 == True and "[" in l4:
		cuentaCorchetesV_Part = cuentaCorchetesV_Part + 1
	
	if cuenta6 == True and "]" in l4:
		cuentaCorchetesV_Part = cuentaCorchetesV_Part - 1	

	if ("(" in l4) and (cuenta6 == True):
		
		lineaParsed = re.sub('.*\(', "", l4).split(" ")
		
		v_part.append(lineaParsed[0])		#Forma
		#v_part.append(lineaParsed[1])		#Lemma
		tag_v_part.append(lineaParsed[2])	#POS
		
		if len(lineaParsed) > 3:

			id_ = re.sub('-.*\n', '', lineaParsed[3])
		
		else:
			
			id_ = ''

		if id_ == '':
			id_ = "NoSentiTag"
		
		IDs_v_part.append(id_)
	
	if cuentaCorchetesV_Part == 0 and cuenta6 == True:

		patternV_Part = ' '.join(v_part) 

		#VerbosParticipioFile.write(adjunto+'\t'+patternV_Part+'\n')
		VerbosParticipioFile.write(patternV_Part+'\n')


		#tagV_Part
		cargaV_PartPos = []
		cargaV_PartNeg = []
		sectionV_Part = []

		cntV_Part = 0
		
		mapFile = open("sentiTaggedFile.txt", "r")

		#Para los verbos en participio
		for v_p in v_part:
								
			for st in mapFile:
						
				cntV_Part += 1	#Con esto controlamos en que linea del archivo etiquetado vamos para no volver a tenerla en cuenta
						
				line = st.split("\t")
		
				#print o + "\t" + line[2]
				if v_p[:-1] in line[0] and cntV_Part > lineaAdj:
							
					#ESTA PARTE ES MUY IMPORTANTE
					#AQUI SE TIENE EN CUENTA LA NEGACION DEL PATRON Y SE INVIERTE LA POLARIDAD DEL VERBO SI ESTÁ NEGADO
							
					if negacion == False:
						cargaV_PartPos.append(line[3])
						cargaV_PartNeg.append(line[4])
					else:
						cargaV_PartPos.append(line[4])
						cargaV_PartNeg.append(line[3])

					sectionV_Part.append(line[5])
					#tagV_Part.append(line[1])

					lineaV_Part = cntV_Part
								
					break

		#Para imprimir el Part-of-Speech y las cargas correspondientes a cada token
		cargasVerbosParticipioFilePos.write('\t'.join(tag_v_part)+"\t"+'\t'.join(cargaV_PartPos)+'\t'+sectionV_Part[0]+"\n")
		cargasVerbosParticipioFileNeg.write('\t'.join(tag_v_part)+"\t"+'\t'.join(cargaV_PartNeg)+'\t'+sectionV_Part[0]+"\n")

		v_part = []
		tag_v_part = []
		IDs_v_part = []
		cuenta6 = False
	'''
	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	#Para el grupo verbal
	if "grup-verb" in l4:
		cuenta2 = True
		grupVerb = True

	if cuenta2 == True and "[" in l4:
		cuentaCorchetesVerb = cuentaCorchetesVerb + 1
		#print "sume cuenta corchetes grupo verbal"
	
	if cuenta2 == True and "]" in l4:
		cuentaCorchetesVerb = cuentaCorchetesVerb - 1
		#print "reste cuenta corchetes grupo verbal"	
	
	if cuentaCorchetesVerb == 0 and grupVerb == True:
			verbo = []
			verbo_forma = []
			tagV = []
			cuenta2 = False
			gv = 0
			grupVerb = False
			IDsVerbo = []
			
			#print "cerre el grupo verbal"

	if "(" in l4:
		lineaParsed = re.sub('.*\(', "", l4).split(" ")
		if len(lineaParsed) > 1:
			adjuntos.append(lineaParsed[1])
			

	if ("forma-inf") in l4 or ("+verb_") in l4 or ("+parti_") in l4 or ("+forma-ger_") in l4:
	#if "grup-verb" in l4:
		gv = 1 #grupo verbal activado
		isVerb = True
		esAux = False
		esCopulativo = False	#Con esta línea se deja de tomar el copulativo cuando se encuentra otro verbo no copulativo dentro del grupo verbal
		#print "entre grup verb"

		cuenta4 = False		#Con esto dejo de agregar elementos a la lista de adjuntos porque ya llegué al verbo 
		negacion = False

		#Hacemos que grupSp esté en False para poder incluir los patrones V + Obj y los atributos de los copulativos que estén
		#dentro de un sintagma preposicional. Como patrón completo, pero aún excluyendo los sn dentro de los sp como objetos directos
		#puesto que hace falta garantizar que sean frases adverbiales y no objetos oblicuos. Eso hay que desambiguarlo y es objeto
		#de una investigación futura.
		grupSp = False

	if "vaux_" in l4:
		esAux = True
			
	if (gv == 1) and ("(" in l4) and (cuenta == False) and (isVerb == True):
		
		lineaParsed = re.sub('.*\(', "", l4).split(" ")
		
		#Controlamos los verbos copulativos
		if lineaParsed[1] in copulativos and esAux == False:
			esCopulativo = True
			isVerb = False
		elif esAux == False:
			verbo_forma.append(lineaParsed[0])		#Forma del verbo
			verbo.append(lineaParsed[1])		#Lemma del verbo
			tagV.append(lineaParsed[2])			#POS del verbo
			isVerb = False
			
			id_ = re.sub('-.*\n', '', lineaParsed[3])
			if id_ == '':
				id_ = "NoSentiTag"
			IDsVerbo.append(id_)
			#print "id Verbo "+id_
		
		#print verbo
		
		#verbo.append(lineaParsed[1])		#Lemma
		#print "guarde verb"
	
	
	#Controlamos los sp que pueden estar después del verbo y que pueden contener un sn, para que este sn no se tome como objeto, sino
	#el sn que hay después de cerrar el sp
	
	# se impone la condición de que excluya los sn dentro de los sp si y solo si se esta capturando el patron v+obj, no para los atributos.
	
	if "grup-sp_" in l4 and esCopulativo == False:
		cuenta3 = True
		grupSp = True
		
	if cuenta3 == True and "[" in l4:
		cuentaCorchetesSp = cuentaCorchetesSp + 1
		#print "sume cuenta corchetes grupo verbal"
	
	if cuenta3 == True and "]" in l4:
		cuentaCorchetesSp = cuentaCorchetesSp - 1
		#print "reste cuenta corchetes grupo verbal"
	
	if cuentaCorchetesSp == 0 and grupSp == True:
			
		cuenta3 = False
		grupSp = False
			
	#if (gv == 1) and ("sn_" in l4):			#Esto es para tomar casos como no cumple con los requisitos. El sn está dentro de un sp. Tratando de omitir lo dicho en l:276	
												#Funciona mejor teniendo en cuenta lo dicho unas lineas arriba
	if (gv == 1) and ("sn_" in l4) and grupSp==False:

		cuenta = True
		#print "active cuenta"
		
	if cuenta == True and "[" in l4:
		cuentaCorchetes = cuentaCorchetes + 1
		#print "sume cuenta corchetes"
	
	if cuenta == True and "]" in l4:
		cuentaCorchetes = cuentaCorchetes - 1
		#print "reste cuenta corchetes"
		
			
	if (gv == 1) and (cuenta == True) and ("(" in l4):
			lineaParsed = re.sub(' *\+', "", l4).split(" ")
			
			#guardamos o bien el objeto del patron V + Obj o bien el atributo si el verbo es copulativo
			if esCopulativo == True:
				atributo.append(lineaParsed[0][1:])		#Forma del atributo
				atributo_lemma.append(lineaParsed[1])		#lemma del atributo
				tagAtr.append(lineaParsed[2])			#POS del atributo
				
				id_ = re.sub('-.*\n', '', lineaParsed[3])
				if id_ == '':
					id_ = "NoSentiTag"
				IDsAtr.append(id_)
				#print "\nid atributo "+id_
				
			else:	
				objeto.append(lineaParsed[0][1:])		#Forma del objeto
				tagObj.append(lineaParsed[2])			#POS del objeto
				#objeto.append(lineaParsed[1])			#Lemma del objeto
				#print "guarde sintagma"
			
				id_ = re.sub('-.*\n', '', lineaParsed[3])
				if id_ == '':
					id_ = "NoSentiTag"
				IDsObj.append(id_)
				#print "\nid objeto "+id_
	

	if cuentaCorchetes == 0 and cuenta == True:

		adjuntos_str = ' '.join(adjuntos)

		opcAdj1 = ' no '
		opcAdj1_1 = ' ni '
				
		
		if esCopulativo == True:
		
			#Se escribe el atributo
			patternAtr = ' '.join(atributo)
			patternAtr_lemma = ' '.join(atributo_lemma)
			#AtributoFile.write(patternAtr+"\n")

			if opcAdj1 in adjuntos_str:
				
				#verificamos que no haya un fin de oración con punto después de encontrar el no. En ese caso, no se activa la negación.
				indice_neg = adjuntos_str.index(" no ")	#indice de la negación no
				indice_FS = 0
				if "." in adjuntos_str:
					indice_FS = adjuntos_str.index(".")		#indice de fin de oración

				if indice_FS  > indice_neg:
					AtributoFile.write(''+'\t'+patternAtr+'\n')
					negacion = False
				else:
					adjunto = re.sub('.* no','no',adjuntos_str)
					adjunto = re.sub(patternAtr_lemma+'','',adjunto)
					AtributoFile.write(adjunto+'\t'+patternAtr+'\n')
					negacion = True
			
			elif opcAdj1_1 in adjuntos_str:
				
				#verificamos que no haya un fin de oración con punto después de encontrar el ni. En ese caso, no se activa la negación.
				indice_neg = adjuntos_str.index(" ni ")	#indice de la negación ni
				indice_FS = 0
				if "." in adjuntos_str:
					indice_FS = adjuntos_str.index(".")		#indice de fin de oración

				if indice_FS  > indice_neg:
					AtributoFile.write(''+'\t'+patternAtr+'\n')
					negacion = False
				else:
					adjunto = re.sub('.* ni','ni',adjuntos_str)
					adjunto = re.sub(patternAtr_lemma+'','',adjunto)
					AtributoFile.write(adjunto+'\t'+patternAtr+'\n')
					negacion = True
				
			else:	
				AtributoFile.write(''+'\t'+patternAtr+"\n")
				negacion = False


			#Se debe detectar y arreglar la inconsistencia que ocasiona que a veces se generen más patrones en el archivo con las cargas
			#que en el archivo que muestra el patrón en texto. Esto para los patrones atributo. Lo importante es que en los patrones con carga
			#que son los que al final interesan, no hay errores y lo hace bien.

			adjuntos = []
		
		else:
			
			if len(verbo) > 0:
			
				#se escribe el patron Verbo + Objeto	
				patternV = ' '.join(verbo)
				patternObj = ' '.join(objeto)

				'''
				opcAdj2 = 'no se'
				opcAdj3 = 'no ha'
				opcAdj4 = 'no se ha'
				
				
				if (' '+opcAdj1+' '+verbo[-1]) in adjuntos_str:
					VerboObjetoFile.write(opcAdj1+'\t'+verbo[-1]+"\t"+patternObj+'\n')
					negacion = True
				elif (' '+opcAdj2+' '+verbo[-1]) in adjuntos_str:
					VerboObjetoFile.write(opcAdj2+'\t'+verbo[-1]+"\t"+patternObj+'\n')
					negacion = True
				elif (' '+opcAdj3+' '+verbo[-1]) in adjuntos_str:
					VerboObjetoFile.write(opcAdj3+"\t"+verbo[-1]+'\t'+patternObj+'\n')
					negacion = True
				elif (' '+opcAdj4+' '+verbo[-1]) in adjuntos_str:
					VerboObjetoFile.write(opcAdj4+"\t"+verbo[-1]+'\t'+patternObj+'\n')
					negacion = True
				else:	
					#VerboObjetoFile.write(patternV+" "+patternObj+"\n")	#Aquí se toman todos los verbos concatenados en la lista
					VerboObjetoFile.write(''+'\t'+verbo[-1]+"\t"+patternObj+"\n")	#Aquí solo el último verbo que ingresó a la lista que es el que interesa
					negacion = False

				'''

				if opcAdj1 in adjuntos_str:
					
					#verificamos que no haya un fin de oración con punto después de encontrar el no. En ese caso, no se activa la negación.
					indice_neg = adjuntos_str.index(" no ")	#indice de la negación no
					indice_FS = 0
					if "." in adjuntos_str:
						indice_FS = adjuntos_str.index(".")		#indice de fin de oración

					if indice_FS  > indice_neg:
						VerboObjetoFile.write(''+'\t'+verbo[-1]+"\t"+patternObj+'\n')
						negacion = False	 
					else:
						adjunto = re.sub('.* no','no',adjuntos_str)
						adjunto = re.sub(verbo[-1]+'.*','',adjunto)
						VerboObjetoFile.write(adjunto+'\t'+verbo[-1]+"\t"+patternObj+'\n')
						negacion = True

				elif opcAdj1_1 in adjuntos_str:

					#verificamos que no haya un fin de oración con punto después de encontrar el ni. En ese caso, no se activa la negación.
					indice_neg = adjuntos_str.index(" ni ")	#indice de la negación ni
					indice_FS = 0
					if "." in adjuntos_str:
						indice_FS = adjuntos_str.index(".")		#indice de fin de oración

					if indice_FS  > indice_neg:
						VerboObjetoFile.write(''+'\t'+verbo[-1]+"\t"+patternObj+'\n')
						negacion = False
					else:
						adjunto = re.sub('.* ni','ni',adjuntos_str)
						adjunto = re.sub(verbo[-1]+'.*','',adjunto)
						VerboObjetoFile.write(adjunto+'\t'+verbo[-1]+"\t"+patternObj+'\n')
						negacion = True

				else:	
					#VerboObjetoFile.write(patternV+" "+patternObj+"\n")	#Aquí se toman todos los verbos concatenados en la lista
					VerboObjetoFile.write(''+'\t'+verbo[-1]+"\t"+patternObj+"\n")	#Aquí solo el último verbo que ingresó a la lista que es el que interesa
					negacion = False


				adjuntos = []

			#print verbo[-1]
		
		#Aqui se crean las características para Machine Learning
		
		#Una vez extraida el patrón V+Obj o el atributo se buscan las correspondientes cargas de sentimiento ya mapeadas de sentiwordnet
		#después de haber desambiguado el sentido de cada palabra con ukb de freeling.
		#Se tiene en cuenta el diccionario de verbos etiquetados y las reglas para asignar peso a los patrones


		mapFile = open("sentiTaggedFile.txt", "r")
		
		#tagV = []
		cargaVPos = []
		cargaVNeg = []
		sectionV = []
		id_fraseV = []

		#tagObj = []
		cargaObjPos = []
		cargaObjNeg = []
		sectionObj = []
		id_fraseObj = []

		#tagAtr = []
		cargaAtrPos = []
		cargaAtrNeg = []
		sectionAtr = []
		id_fraseAtr = []
		
		cntVObj = 0

		verboEnLista = False
		
		#Para los verbos
		
		#print str(len(IDsVerbo)) + "\n" 
		
		if len(verbo) != 0 and esCopulativo == False:
			
			#Ahora se tiene en cuenta el diccionario de verbos para asignar la carga en primera instancia, sino esta alli se toma de sentiwordnet
			if lista_verbos.get(verbo[-1]) != None:
				
				verboEnLista = True
				
				#Muy importante: Se hace la asignacion de carga teniendo en cuenta si el patron está negado (no, ni). Si hay negacion se invierte la polaridad en la carga de sentimiento del verbo.
				
				if lista_verbos.get(verbo[-1]) == "1":

					if negacion == False:
						cargaVPos.append("0.125")	#Asignamos 0.125 y no 1 para evitar sesgos por carga tan alta respecto a
						cargaVNeg.append("0")		#los otros tokens
					else:
						cargaVPos.append("0")		#Asignamos 0.125 y no 1 para evitar sesgos por carga tan alta respecto a
						cargaVNeg.append("0.125")	#los otros tokens

				elif lista_verbos.get(verbo[-1]) == "-1":

					if negacion == False:
						cargaVPos.append("0")
						cargaVNeg.append("0.125") #Se le da valor de 0.125 (positivo) y no -0.125 (negativo) a la carga negativa del verbo para evitar errores al sumar mas adelante
					else:
						cargaVPos.append("0.125")
						cargaVNeg.append("0")

					#print "Si tome la carga."

				else:
					cargaVPos.append("0")
					cargaVNeg.append("0")

				#print "Estoy usando el diccionario de verbos . . ."
				#print lista_verbos.get(verbo[-1])+verbo[-1]

			for st in mapFile:
				
				cntVObj += 1 #Con esto controlamos en que linea del archivo etiquetado vamos para no volver a tenerla en cuenta
				
				line = st.split("\t")

				#El POS esta en la posicion 1
				#El ID después de desambiguar está en la posición 2 de la lista
				#La carga pos está en la posición 3 de la lista
				#La carga neg está en la posición 4 de la lista
				#La sección está en la posición 5 de la lista

				if verbo_forma[-1].lower() in line[0].lower() and cntVObj > lineaVObj:

					#print "Cod verbo: " + IDsVerbo[-1]
					#print "Cod en sentitag: " + line[2]
					#print "Verbo: " + verbo[-1]

					#ESTA PARTE ES MUY IMPORTANTE
					#AQUI SE TIENE EN CUENTA LA NEGACION DEL PATRON Y SE INVIERTE LA POLARIDAD DEL VERBO EN CASO DE QUE EL PATRÓN ESTÉ NEGADO
				
					#Solo toma la carga de sentiwordnet cuando el verbo no este en el diccionario de verbos
					if verboEnLista == False:

						if negacion == False:
							cargaVPos.append(line[3])
							cargaVNeg.append(line[4])
						else:
							cargaVPos.append(line[4])
							cargaVNeg.append(line[3])

					sectionV.append(line[5])
					#tagV.append(line[1])

					id_fraseV.append(line[6][:-1])
					#print id_fraseV

					lineaVObj = cntVObj
						
					#print v[:-1] + "\t" + line[2]
					
					#print verbo[-1] + " " + IDsVerbo[-1][:-1] + " " + line[5]
					
					break

			#Para los objetos
			for o in IDsObj:			
				for st in mapFile:	
					line = st.split("\t")
		
					#print o + "\t" + line[2]
					if o[:-1] in line[2]:
						
						#print "Cod obj: " + o[:-1]
						#print "Cod en sentitag: " + line[2]
					
						#ESTA PARTE ES MUY IMPORTANTE
						#AQUI SE TIENE EN CUENTA LA NEGACION DEL PATRON Y SE INVIERTE LA POLARIDAD DE CADA TOKEN DEL OBJETO DIRECTO DEL MISMO EN CASO DE QUE
						#PATRÓN ESTÉ NEGADO
						
						if negacion == False:
							cargaObjPos.append(line[3])
							cargaObjNeg.append(line[4])
						else:
							cargaObjPos.append(line[4])
							cargaObjNeg.append(line[3])

						#tagObj.append(line[1])	

						#En caso de necesitarse esta parte hay que hacerle la misma corrección que a sectionV y sectionAtr con cntVObj y cntAtr
						#sectionObj.append(line[5])
					
						break
						
			
			#print cargaVPos
			#print "$$$"
			#print cargaObjPos
			#print "\n"	
			
			if len(sectionV) > 0:		#Este condicional se pone por si ocurren casos no tratados en el texo que ocasionen ruptura del scritp cuando sectionV queda vacia.
				
				#Para imprimir el patron en texto y las cargas correspondientes a cada token
				#cargasPatronesVerboObjetoPos.write(verbo[-1]+" "+patternObj+"\t"+'\t'.join(cargaVPos)+"\t"+'\t'.join(cargaObjPos)+'\t'+sectionV[0])
				#cargasPatronesVerboObjetoNeg.write(verbo[-1]+" "+patternObj+"\t"+'\t'.join(cargaVNeg)+"\t"+'\t'.join(cargaObjNeg)+'\t'+sectionV[0])
				
				#Para imprimir el Part-of-Speech y las cargas correspondientes a cada token
				cargasPatronesVerboObjetoPos.write(tagV[-1]+"\t"+'\t'.join(tagObj)+"\t"+'\t'.join(cargaVPos)+"\t"+'\t'.join(cargaObjPos)+'\t'+sectionV[0]+"\t"+id_fraseV[-1]+"\n")
				cargasPatronesVerboObjetoNeg.write(tagV[-1]+"\t"+'\t'.join(tagObj)+"\t"+'\t'.join(cargaVNeg)+"\t"+'\t'.join(cargaObjNeg)+'\t'+sectionV[0]+"\t"+id_fraseV[-1]+"\n")
			
				


		#elif len(verbo) == 0 and esCopulativo == True:	
		else:
		
			cntAtr = 0

			#Para los atributos
			for a in atributo:

				for st in mapFile:
					
					cntAtr += 1	#Con esto controlamos en que linea del archivo etiquetado vamos para no volver a tenerla en cuenta
					
					line = st.split("\t")

					
					#print o + "\t" + line[2]
					
					#validamos también que a no quede vacío (con un salto de línea) para que no hayan errores al tomar una carga que no corresponde al token actual

					if a[:-1] in line[0] and cntAtr > lineaAtr:

						#ESTA PARTE ES MUY IMPORTANTE
						#AQUI SE TIENE EN CUENTA LA NEGACION DEL PATRON Y SE INVIERTE LA POLARIDAD DE CADA TOKEN DEL ATRIBUTO SI EL
						#PATRÓN ESTÁ NEGADO
						
						if negacion == False:
							cargaAtrPos.append(line[3])
							cargaAtrNeg.append(line[4])
						else:
							cargaAtrPos.append(line[4])
							cargaAtrNeg.append(line[3])

						
						sectionAtr.append(line[5])
						#tagAtr.append(line[1])

						id_fraseAtr.append(line[6][:-1])
						

						lineaAtr = cntAtr

						break
		
			#print ' '.join(cargaVPos) + "\n"
			
			#print len(IDsAtr)

			if len(sectionAtr) > 0:		#Este condicional se pone porque ocurren casos no tratados en el texo que ocasionan ruptura del scritp cuando sectionAtr queda vacia.
				#Para imprimir el patron en texto y las cargas correspondientes a cada token
				#cargasPatronesAtributoPos.write(patternAtr+"\t"+'\t'.join(cargaAtrPos)+'\t'+sectionAtr[0])
				#cargasPatronesAtributoNeg.write(patternAtr+"\t"+'\t'.join(cargaAtrNeg)+'\t'+sectionAtr[0])

				#Para imprimir el Part-of-Speech y las cargas correspondientes a cada token
				cargasPatronesAtributoPos.write('\t'.join(tagAtr)+"\t"+'\t'.join(cargaAtrPos)+'\t'+sectionAtr[0]+"\t"+id_fraseAtr[-1]+'\n')
				cargasPatronesAtributoNeg.write('\t'.join(tagAtr)+"\t"+'\t'.join(cargaAtrNeg)+'\t'+sectionAtr[0]+"\t"+id_fraseAtr[-1]+'\n')

		
		IDsObj = []
		IDsAtr = []
							
		cuenta = False
		verbo = []
		verbo_forma = []
		tagV = []
		objeto = []
		tagObj = []
		atributo = []
		atributo_lemma = []
		tagAtr = []
		gv = 0
		esCopulativo = False

		#print "termine patron"


#Escribimos un separador para los patrones de cada artículo
AtributoFile.write("----------------------------------Fin de artículo -------------------------------\n")
VerboObjetoFile.write("----------------------------------Fin de artículo -------------------------------\n")
SintagmaAdjFile.write("----------------------------------Fin de artículo -------------------------------\n")

parsedFile.close()
VerboObjetoFile.close()
AtributoFile.close()
SintagmaAdjFile.close()
VerbosParticipioFile.close()	
mapFile.close()
cargasPatronesVerboObjetoPos.close()
cargasPatronesVerboObjetoNeg.close()
cargasPatronesAtributoPos.close()
cargasPatronesAtributoNeg.close()
cargasSintagmasAdjFilePos.close()
cargasSintagmasAdjFileNeg.close()

#Aquí se recopila la base de datos para machine learning

print "Building training Data. . .\n\n"

FileVObjPos = open("cargasPatronesVerboObjetoPos.txt", "r")
FileVObjNeg = open("cargasPatronesVerboObjetoNeg.txt", "r")
FileAtrPos = open("cargasPatronesAtributoPos.txt", "r")
FileAtrNeg = open("cargasPatronesAtributoNeg.txt", "r")
FileSAdjPos = open("cargasSintagmasAdjetivalesPos.txt", "r")
FileSAdjNeg = open("cargasSintagmasAdjetivalesNeg.txt", "r")


features = open("features.txt", "a")

###############################################################

#Extraccion de caracteristicas VObjPos de S1, S2 y S3

###############################################################

#Acumuladores de carga para la seccion S1
SumVObjPosS1 = 0

#Acumuladores de carga para la seccion S2
SumVObjPosS2 = 0

#Acumuladores de carga para la seccion S3
SumVObjPosS3 = 0


#Lista de listas con cargas por patrón y con la frase en la que se encuentra
ListSumVObjPosS1 = []
ListSumVObjPosS2 = []
ListSumVObjPosS3 = []

cuentaS1 = 0
cuentaS2 = 0
cuentaS3 = 0

seccionesVerboObj = []
numFraseVerboObj = []
cargasPosVerbos = []
cargasPosObj = []

for vop in FileVObjPos:
	
	#Eliminamos las dobles tabulaciones si las hay para evitar errores en al tomar las etiquetas y sus cargas
	vop = re.sub("\t\t", "\t", vop)
	
	lista_vop = vop.split("\t")
	#seccion = lista_vop[-1][:-1]
	seccion = lista_vop[-2]
	num_frase = lista_vop[-1][:-1]
	#print seccion
	lista_vop.pop(-1)
	lista_vop.pop(-1)	#Se elimina dos veces la última posición de la lista. Esto es, primero se elimina el id de la frase y luego la sección del patrón.	
	dimLvop = len(lista_vop)
	
	#Este condicional se usa poco pero corrige las inconsistencias que se presentan cuando hay mas cargas que tags debido a entradas como pensionarse que freeling lo parte en dos y genera la
	#inconsistencia
	if dimLvop % 2 != 0:
		lista_vop.pop(-2)
		dimLvop = len(lista_vop)
	
	tags = []
	cargas = []
	contador = 0
	for item in lista_vop:
		
		if contador < len(lista_vop)/2:
			tags.append(item)
		else:
			cargas.append(item)
		
		contador += 1

	
	#print "Tags -> "+' '.join(tags)
	#print "\n"
	#print "Cargas -> "+' '.join(cargas)

	
	#Ahora se asigna la carga al patron
	#En primera instancia se usaba un enfoque simple, de izquieda a derecha hasta encontrar un valor diferente de cero y esa va a ser la carga del patron.
	#Este enfoque dio muy malos resultados porque no tenia en cuenta aspectos linguisticos relevantes como: el diccionario de verbos, y la suma de las cargas
	#de todo el objeto directo del verbo o unicamente de los adjetivos sin tener en cuenta los nombres.
	patternCharge = 0
	directObjCharge = 0
	#Omitimos la carga del verbo para computar la carga del objeto directo
	charges = cargas[1:]
	#print "Charges -> "+' '.join(charges)
	#print "Cargas -> "+' '.join(cargas)
	for c in charges:
		if c != '0' and is_number(c):
			#Aqui se computa el acumulado de carga del objeto directo. Sin embargo, otra alternativa seria solo tomar la carga de los adjetivos que aprezcan en el obj directo
			directObjCharge += float(c)
			#break
	
	seccionesVerboObj.append(seccion)	#solo se hace para los positivos puesto que coincide con la de los patrones v+obj neg
	numFraseVerboObj.append(num_frase)
	cargasPosVerbos.append(cargas[0])
	cargasPosObj.append(directObjCharge)

'''
	if seccion == "S1":
		SumVObjPosS1 += patternCharge
		cuentaS1 += 1
	elif seccion == "S2":
		SumVObjPosS2 += patternCharge
		cuentaS2 += 1
	elif seccion == "S3":
		SumVObjPosS3 += patternCharge
		cuentaS3 += 1

if cuentaS1 > 0:
	VObjPosS1 = (SumVObjPosS1/cuentaS1)
else:
	VObjPosS1 = 0

if cuentaS2 > 0:
	VObjPosS2 = (SumVObjPosS2/cuentaS2)
else:
	VObjPosS2 = 0

if cuentaS3 > 0:
	VObjPosS3 = (SumVObjPosS3/cuentaS3)
else:
	VObjPosS3 = 0

'''

#print "Carga Positiva en S1 -> "+str(SumVObjPosS1/cuentaS1)
#print "Carga Positiva en S2 -> "+str(SumVObjPosS2/cuentaS2)
#print "Carga Positiva en S3 -> "+str(SumVObjPosS3/cuentaS3)



###############################################################

#Extraccion de caracteristicas VObjNeg de S1, S2 y S3

###############################################################

#Acumuladores de carga para la seccion S1
SumVObjNegS1 = 0

#Acumuladores de carga para la seccion S2
SumVObjNegS2 = 0

#Acumuladores de carga para la seccion S3
SumVObjNegS3 = 0

#Lista de listas con cargas por patrón y con la frase en la que se encuentra
ListSumVObjNegS1 = []
ListSumVObjNegS2 = []
ListSumVObjNegS3 = []

cuentaS1 = 0
cuentaS2 = 0
cuentaS3 = 0

cargasNegVerbos = []
cargasNegObj = []

for von in FileVObjNeg:
	
	#Eliminamos las dobles tabulaciones si las hay para evitar errores en al tomar las etiquetas y sus cargas
	von = re.sub("\t\t", "\t", von)
	
	lista_von = von.split("\t")
	seccion = lista_von[-1][:-1]
	lista_von.pop(-1)
	lista_von.pop(-1)	#Se elimina dos veces la última posición de la lista. Esto es, primero se elimina el id de la frase y luego la sección del patrón.
	dimLvon = len(lista_von)
	
	#Este condicional se usa poco pero corrige las inconsistencias que se presentan cuando hay mas cargas que tags debido a entradas como pensionarse que freeling lo parte en dos y genera la
	#inconsistencia
	if dimLvon % 2 != 0:
		lista_von.pop(-2)
		dimLvon = len(lista_von)
	
	tags = []
	cargas = []
	contador = 0
	for item in lista_von:
		
		if contador < len(lista_von)/2:
			tags.append(item)
		else:
			cargas.append(item)
		
		contador += 1

	
	#print "Tags -> "+' '.join(tags)
	#print "\n"
	#print "Cargas -> "+' '.join(cargas)

	#Ahora se asigna la carga al patron
	#En primera instancia se usaba un enfoque simple, de izquieda a derecha hasta encontrar un valor diferente de cero y esa va a ser la carga del patron.
	#Este enfoque dio muy malos resultados porque no tenia en cuenta aspectos linguisticos relevantes como: el diccionario de verbos, y la suma de las cargas
	#de todo el objeto directo del verbo o unicamente de los adjetivos sin tener en cuenta los nombres.
	patternCharge = 0
	directObjCharge = 0
	#Omitimos la carga del verbo para computar la carga del objeto directo
	charges = cargas[1:]
	#print "Charges -> "+' '.join(charges)
	#print "Cargas -> "+' '.join(cargas)
	
	##Aqui se computa el acumulado de carga del objeto directo.
	for c, t in zip(charges,tags):
		if c != '0' and is_number(c):
			directObjCharge += float(c)
		
		#Aqui se computa la carga del objeto directo. Solo se toma la carga de los Adj no se tienen en cuenta los nombres u otros verbos en el obj dir.
		#if c != '0' and is_number(c) and t.startswith('A'):
			#directObjCharge += float(c)
			
	
	cargasNegVerbos.append(cargas[0])
	cargasNegObj.append(directObjCharge)


'''	
	if seccion == "S1":
		SumVObjNegS1 += patternCharge
		cuentaS1 += 1
	elif seccion == "S2":
		SumVObjNegS2 += patternCharge
		cuentaS2 += 1
	elif seccion == "S3":
		SumVObjNegS3 += patternCharge
		cuentaS3 += 1

if cuentaS1 > 0:
	VObjNegS1 = (SumVObjNegS1/cuentaS1)
else:
	VObjNegS1 = 0

if cuentaS2 > 0:	
	VObjNegS2 = (SumVObjNegS2/cuentaS2)
else:
	VObjNegS2 = 0

if cuentaS3 > 0:
	VObjNegS3 = (SumVObjNegS3/cuentaS3)
else:
	VObjNegS3 = 0

'''

#print "Carga Negativa en S1 -> "+str(SumVObjNegS1/cuentaS1)
#print "Carga Negativa en S2 -> "+str(SumVObjNegS2/cuentaS2)
#print "Carga Negativa en S3 -> "+str(SumVObjNegS3/cuentaS3)
			


#Aqui se asignan las cargas de los patrones V+Obj y se crean las caracteristicas finalmente

for vpos, vneg, cobjp, cobjn, s, f in zip(cargasPosVerbos, cargasNegVerbos, cargasPosObj, cargasNegObj, seccionesVerboObj, numFraseVerboObj):

	if is_number(vpos) == False:
		vpos = 0
	if is_number(vneg) == False:
		vneg = 0

	#print "vpos = "+str(vpos)+"; vneg = "+str(vneg)+"; cobjp = "+str(cobjp)+"; cobjn = "+str(cobjn)+"; seccion = "+str(s)

	#Las reglas para asignar los pesos a los patrones V+Obj es asi:
	# VP * ObjP = P
	# VP * ObjN = P
	# VN * ObjP = N
	# VN * ObjN = P

	#Hay excepciones para las reglas anteriores, pero este es el enfoque que se está trabajando porque no hay reglas que funcionen
	#para todos los casos.

	if float(vpos) > float(vneg):

		#En igualdad de carga se le da prioridad a lo negativo con el mayor estricto. Esto debido a qué es más dificil detectar lo negativo.
		if float(cobjp) > float(cobjn):

			patternChargePos = float(vpos) + float(cobjp)
			patternChargeNeg = 0

		#Este else es inncesario porque se hace la misma asignación que en el if, pero se deja por si más tarde llegan a cambiar las reglas de pesado
		else:

			patternChargePos = float(vpos) + float(cobjn)
			patternChargeNeg = 0

	elif float(vneg) > float(vpos):

		#En igualdad de carga se le da prioridad a lo negativo con el mayor estricto. Esto debido a qué es más dificil detectar lo negativo.
		if float(cobjp) >= float(cobjn):

			patternChargeNeg = float(vneg) + float(cobjp)
			patternChargePos = 0

		else:

			patternChargePos = float(vneg) + float(cobjn)
			patternChargeNeg = 0

	else:

		#En igualdad de carga se le da prioridad a lo negativo con el mayor estricto. Esto debido a qué es más dificil detectar lo negativo.
		if float(cobjp) > float(cobjn):

			patternChargePos = float(cobjp)
			patternChargeNeg = 0			

		else:

			patternChargeNeg = float(cobjn)
			patternChargePos = 0

	'''
	#Sin reglas de pesado

	patternChargePos = float(vpos) + float(cobjp)
	patternChargeNeg = float(vneg) + float(cobjp)

	'''


	if s == "S1":
		SumVObjPosS1 += patternChargePos
		ListSumVObjPosS1.append([f, patternChargePos])
		SumVObjNegS1 += patternChargeNeg
		ListSumVObjNegS1.append([f,patternChargeNeg])
		cuentaS1 += 1
		#print "pase por S1"
	elif s == "S2":
		SumVObjPosS2 += patternChargePos
		ListSumVObjPosS2.append([f, patternChargePos])
		SumVObjNegS2 += patternChargeNeg
		ListSumVObjNegS2.append([f,patternChargeNeg])
		cuentaS2 += 1
		#print "pase por S2"
	elif s == "S3":
		SumVObjPosS3 += patternChargePos
		ListSumVObjPosS3.append([f, patternChargePos])
		SumVObjNegS3 += patternChargeNeg
		ListSumVObjNegS3.append([f,patternChargeNeg])
		cuentaS3 += 1
		#print "pase por S3"


	#print "Cargas Positivas Obj "+str(cobjp)
	#print "Cargas Negativas Obj "+str(cobjn)

###############################################################

#Extraccion de caracteristicas AtrPos de S1, S2 y S3

###############################################################

#Acumuladores de carga para la seccion S1
SumAtrPosS1 = 0

#Acumuladores de carga para la seccion S2
SumAtrPosS2 = 0

#Acumuladores de carga para la seccion S3
SumAtrPosS3 = 0

#Lista de listas con cargas por patrón y con la frase en la que se encuentra
ListSumAtrPosS1 = []
ListSumAtrPosS2 = []
ListSumAtrPosS3 = []

cuentaS1 = 0
cuentaS2 = 0
cuentaS3 = 0

seccionesAtr = []
numFraseAtr = []

for atrp in FileAtrPos:
	
	#Eliminamos las dobles tabulaciones si las hay para evitar errores en al tomar las etiquetas y sus cargas
	atrp = re.sub("\t\t", "\t", atrp)
	
	lista_atrp = atrp.split("\t")
	#seccion = lista_atrp[-1][:-1]
	seccion = lista_atrp[-2]
	num_frase = lista_atrp[-1][:-1]
	lista_atrp.pop(-1)
	lista_atrp.pop(-1)	#Se elimina dos veces la última posición de la lista. Esto es, primero se elimina el id de la frase y luego la sección del patrón.
	dimLatrp = len(lista_atrp)
	
	#Este condicional se usa poco pero corrige las inconsistencias que se presentan cuando hay mas cargas que tags debido a entradas como pensionarse que freeling lo parte en dos y genera la
	#inconsistencia
	if dimLatrp % 2 != 0 and len(lista_atrp) >= 2: 
		lista_atrp.pop(-2)
		dimLatrp = len(lista_atrp)
	
	tags = []
	cargas = []
	contador = 0
	for item in lista_atrp:
		
		if contador < len(lista_atrp)/2:
			tags.append(item)
		else:
			cargas.append(item)
		
		contador += 1

	
	#print "Tags -> "+' '.join(tags)
	#print "\n"
	#print "Cargas -> "+' '.join(cargas)

	
	#Ahora se asigna la carga al patron
	#En primera instancia se usaba un enfoque simple, de izquieda a derecha hasta encontrar un valor diferente de cero y esa va a ser la carga del patron.
	#Ahora se computa la carga de cada token en el patrón

	#Se valida que coincidan el numero de tags (tokens) con la cantidad de cargas de sentimiento asignadas 
	#Esto se hace porque existen algunas incosistencias en este mapeo

	patternCharge = 0
	for c in cargas:
		if c != '0' and is_number(c):
			patternCharge += float(c)
			#break
	
	seccionesAtr.append(seccion)	#solo se hace para los positivos puesto que coincide con la de los patrones atr neg
	numFraseAtr.append(num_frase)

	if seccion == "S1":
		SumAtrPosS1 += patternCharge
		ListSumAtrPosS1.append([num_frase, patternCharge])
		cuentaS1 += 1
	elif seccion == "S2":
		SumAtrPosS2 += patternCharge
		ListSumAtrPosS2.append([num_frase, patternCharge])
		cuentaS2 += 1
	elif seccion == "S3":
		SumAtrPosS3 += patternCharge
		ListSumAtrPosS3.append([num_frase, patternCharge])
		cuentaS3 += 1


if cuentaS1 > 0:
	AtrPosS1 = (SumAtrPosS1/cuentaS1)
else:
	AtrPosS1 = 0

if cuentaS2> 0:	
	AtrPosS2 = (SumAtrPosS2/cuentaS2)
else:
	AtrPosS2 = 0

if cuentaS3> 0:
	AtrPosS3 = (SumAtrPosS3/cuentaS3)
else:
	AtrPosS3 = 0

#print "Carga Positiva de Atributos en S1 -> "+str(SumAtrPosS1/cuentaS1)
#print "Carga Positiva de Atributos en S2 -> "+str(SumAtrPosS2/cuentaS2)
#print "Carga Positiva de Atributos en S3 -> "+str(SumAtrPosS3/cuentaS3)



###############################################################

#Extraccion de caracteristicas AtrNeg de S1, S2 y S3

###############################################################

#Acumuladores de carga para la seccion S1
SumAtrNegS1 = 0

#Acumuladores de carga para la seccion S2
SumAtrNegS2 = 0

#Acumuladores de carga para la seccion S3
SumAtrNegS3 = 0

#Lista de listas con id de frase y carga de cada patrón
ListSumAtrNegS1 = []
ListSumAtrNegS2 = []
ListSumAtrNegS3 = []

cuentaS1 = 0
cuentaS2 = 0
cuentaS3 = 0

for atrn in FileAtrNeg:
	
	#Eliminamos las dobles tabulaciones si las hay para evitar errores en al tomar las etiquetas y sus cargas
	atrn = re.sub("\t\t", "\t", atrn)
	
	lista_atrn = atrn.split("\t")
	#seccion = lista_atrn[-1][:-1]
	seccion = lista_atrn[-2]
	num_frase = lista_atrn[-1][:-1]
	lista_atrn.pop(-1)
	lista_atrn.pop(-1)	#Se elimina dos veces la última posición de la lista. Esto es, primero se elimina el id de la frase y luego la sección del patrón.
	dimLatrn = len(lista_atrn)
	
	#Este condicional se usa poco pero corrige las inconsistencias que se presentan cuando hay mas cargas que tags debido a entradas como pensionarse que freeling lo parte en dos y genera la
	#inconsistencia
	if dimLatrn % 2 != 0 and len(lista_atrn) >= 2:
		lista_atrn.pop(-2)
		dimLatrn = len(lista_atrn)
	
	tags = []
	cargas = []
	contador = 0
	for item in lista_atrn:
		
		if contador < len(lista_atrn)/2:
			tags.append(item)
		else:
			cargas.append(item)
		
		contador += 1

	
	#print "Tags -> "+' '.join(tags)
	#print "\n"
	#print "Cargas -> "+' '.join(cargas)

	
	#Ahora se asigna la carga al patron
	#En primera instancia se usaba un enfoque simple, de izquieda a derecha hasta encontrar un valor diferente de cero y esa va a ser la carga del patron.
	#Ahora se computa la carga de cada token en el patrón
	
	patternCharge = 0
	for c in cargas:
		if c != '0' and is_number(c):
			patternCharge += float(c)
			#break
	
	if seccion == "S1":
		SumAtrNegS1 += patternCharge
		ListSumAtrNegS1.append([num_frase, patternCharge])
		cuentaS1 += 1
	elif seccion == "S2":
		SumAtrNegS2 += patternCharge
		ListSumAtrNegS2.append([num_frase, patternCharge])
		cuentaS2 += 1
	elif seccion == "S3":
		SumAtrNegS3 += patternCharge
		ListSumAtrNegS3.append([num_frase, patternCharge])
		cuentaS3 += 1

if cuentaS1 > 0: 
	AtrNegS1 = (SumAtrNegS1/cuentaS1)
else:
	AtrNegS1 = 0

if cuentaS2 > 0:
	AtrNegS2 = (SumAtrNegS2/cuentaS2)
else:
	AtrNegS2 = 0

if cuentaS3 > 0:
	AtrNegS3 = (SumAtrNegS3/cuentaS3)
else:
	AtrNegS3 = 0

#print "Carga Positiva de Atributos en S1 -> "+str(SumAtrPosS1/cuentaS1)
#print "Carga Positiva de Atributos en S2 -> "+str(SumAtrPosS2/cuentaS2)
#print "Carga Positiva de Atributos en S3 -> "+str(SumAtrPosS3/cuentaS3)


###############################################################

#Extraccion de caracteristicas SAdjPos de S1, S2 y S3

###############################################################

#Acumuladores de carga para la seccion S1
SumSAdjPosS1 = 0

#Acumuladores de carga para la seccion S2
SumSAdjPosS2 = 0

#Acumuladores de carga para la seccion S3
SumSAdjPosS3 = 0


ListSumSAdjPosS1 = []
ListSumSAdjPosS2 = []
ListSumSAdjPosS3 = []

cuentaS1 = 0
cuentaS2 = 0
cuentaS3 = 0

seccionesSAdj = []
numFraseSAdj = []

for sadjp in FileSAdjPos:
	
	#Eliminamos las dobles tabulaciones si las hay para evitar errores en al tomar las etiquetas y sus cargas
	sadjp = re.sub("\t\t", "\t", sadjp)
	
	lista_sadjp = sadjp.split("\t")
	#seccion = lista_sadjp[-1][:-1]
	seccion = lista_sadjp[-2]
	num_frase = lista_sadjp[-1][:-1]
	lista_sadjp.pop(-1)
	lista_sadjp.pop(-1)	#Se elimina dos veces la última posición de la lista. Esto es, primero se elimina el id de la frase y luego la sección del patrón.
	dimLsadjp = len(lista_sadjp)
	
	#Este condicional se usa poco pero corrige las inconsistencias que se presentan cuando hay mas cargas que tags debido a entradas como pensionarse que freeling lo parte en dos y genera la
	#inconsistencia
	if dimLsadjp % 2 != 0 and len(lista_sadjp) >= 2:
		lista_sadjp.pop(-2)
		dimLsadjp = len(lista_sadjp)
	
	tags = []
	cargas = []
	contador = 0
	for item in lista_sadjp:
		
		if contador < len(lista_sadjp)/2:
			tags.append(item)
		else:
			cargas.append(item)
		
		contador += 1

	
	#print "Tags -> "+' '.join(tags)
	#print "\n"
	#print "Cargas -> "+' '.join(cargas)

	
	#Ahora se asigna la carga al patron
	#En primera instancia se usaba un enfoque simple, de izquieda a derecha hasta encontrar un valor diferente de cero y esa va a ser la carga del patron.
	#Ahora se computa la carga de cada token en el patrón

	#Se valida que coincidan el numero de tags (tokens) con la cantidad de cargas de sentimiento asignadas 
	#Esto se hace porque existen algunas incosistencias en este mapeo

	patternCharge = 0
	for c in cargas:
		if c != '0' and is_number(c):
			patternCharge += float(c)
			#break
	
	seccionesSAdj.append(seccion)	#solo se hace para los positivos puesto que coincide con la de los patrones v+obj neg
	numFraseSAdj.append(num_frase)

	if seccion == "S1":
		SumSAdjPosS1 += patternCharge
		ListSumSAdjPosS1.append([num_frase, patternCharge])
		cuentaS1 += 1
	elif seccion == "S2":
		SumSAdjPosS2 += patternCharge
		ListSumSAdjPosS2.append([num_frase, patternCharge])
		cuentaS2 += 1
	elif seccion == "S3":
		SumSAdjPosS3 += patternCharge
		ListSumSAdjPosS3.append([num_frase, patternCharge])
		cuentaS3 += 1


if cuentaS1 > 0:
	SAdjPosS1 = (SumSAdjPosS1/cuentaS1)
else:
	SAdjPosS1 = 0

if cuentaS2> 0:	
	SAdjPosS2 = (SumSAdjPosS2/cuentaS2)
else:
	SAdjPosS2 = 0

if cuentaS3> 0:
	SAdjPosS3 = (SumSAdjPosS3/cuentaS3)
else:
	SAdjPosS3 = 0

#print "Carga Positiva de Sintagmas Adjetivales en S1 -> "+str(SumSAdjPosS1/cuentaS1)
#print "Carga Positiva de Sintagmas Adjetivales en S2 -> "+str(SumSAdjPosS2/cuentaS2)
#print "Carga Positiva de Sintagmas Adjetivales en S3 -> "+str(SumSAdjPosS3/cuentaS3)



###############################################################

#Extraccion de caracteristicas SAdjNeg de S1, S2 y S3

###############################################################

#Acumuladores de carga para la seccion S1
SumSAdjNegS1 = 0

#Acumuladores de carga para la seccion S2
SumSAdjNegS2 = 0

#Acumuladores de carga para la seccion S3
SumSAdjNegS3 = 0


ListSumSAdjNegS1 = []
ListSumSAdjNegS2 = []
ListSumSAdjNegS3 = []

cuentaS1 = 0
cuentaS2 = 0
cuentaS3 = 0

for sadjn in FileSAdjNeg:
	
	#Eliminamos las dobles tabulaciones si las hay para evitar errores en al tomar las etiquetas y sus cargas
	sadjn = re.sub("\t\t", "\t", sadjn)
	
	lista_sadjn = sadjn.split("\t")
	#seccion = lista_sadjn[-1][:-1]
	seccion = lista_sadjn[-2]
	num_frase = lista_sadjn[-1][:-1]
	lista_sadjn.pop(-1)
	lista_sadjn.pop(-1)	#Se elimina dos veces la última posición de la lista. Esto es, primero se elimina el id de la frase y luego la sección del patrón.
	dimLsadjn = len(lista_sadjn)
	
	#Este condicional se usa poco pero corrige las inconsistencias que se presentan cuando hay mas cargas que tags debido a entradas como pensionarse que freeling lo parte en dos y genera la
	#inconsistencia
	if dimLsadjn % 2 != 0 and len(lista_sadjn) >= 2:
		lista_sadjn.pop(-2)
		dimLsadjn = len(lista_sadjn)
	
	tags = []
	cargas = []
	contador = 0
	for item in lista_sadjn:
		
		if contador < len(lista_sadjn)/2:
			tags.append(item)
		else:
			cargas.append(item)
		
		contador += 1

	'''
	print "Tags -> "+' '.join(tags)
	print "\n"
	print "Cargas -> "+' '.join(cargas)
	'''
	
	#Ahora se asigna la carga al patron
	#En primera instancia se usaba un enfoque simple, de izquieda a derecha hasta encontrar un valor diferente de cero y esa va a ser la carga del patron.
	#Ahora se computa la carga de cada token en el patrón

	patternCharge = 0
	for c in cargas:
		if c != '0' and is_number(c):
			patternCharge += float(c)
			#break
	
	if seccion == "S1":
		SumSAdjNegS1 += patternCharge
		ListSumSAdjNegS1.append([num_frase, patternCharge])
		cuentaS1 += 1
	elif seccion == "S2":
		SumSAdjNegS2 += patternCharge
		ListSumSAdjNegS2.append([num_frase, patternCharge])
		cuentaS2 += 1
	elif seccion == "S3":
		SumSAdjNegS3 += patternCharge
		ListSumSAdjNegS3.append([num_frase, patternCharge])
		cuentaS3 += 1

if cuentaS1 > 0: 
	SAdjNegS1 = (SumSAdjNegS1/cuentaS1)
else:
	SAdjNegS1 = 0

if cuentaS2 > 0:
	SAdjNegS2 = (SumSAdjNegS2/cuentaS2)
else:
	SAdjNegS2 = 0

if cuentaS3 > 0:
	SAdjNegS3 = (SumSAdjNegS3/cuentaS3)
else:
	SAdjNegS3 = 0

#print "Carga Negativa de Sintagmas Adjetivales en S1 -> "+str(SumSAdjPosS1/cuentaS1)
#print "Carga Negativa de Sintagmas Adjetivales en S2 -> "+str(SumSAdjPosS2/cuentaS2)
#print "Carga Negativa de Sintagmas Adjetivales en S3 -> "+str(SumSAdjPosS3/cuentaS3)


#Se escriben los vectores de caracteristicas que representan al texto
#Encabezado
#features.write("V+O_posS1\tV+O_negS1\tAtr_posS1\tAtr_negS1\tV+O_posS2\tV+O_negS2\tAtr_posS2\tAtr_negS2\tV+O_posS3\tV+O_negS3\tAtr_posS3\tAtr_negS3\n\n")

#Escribimos el vector de caracteristicas promediando el peso sobre el total de patrones por seccion
#features.write(str(VObjPosS1)+"\t"+str(VObjNegS1)+"\t"+str(AtrPosS1)+"\t"+str(AtrNegS1)+"\t"+str(VObjPosS2)+"\t"+str(VObjNegS2)+"\t"+str(AtrPosS2)+"\t"+str(AtrNegS2)+"\t"+str(VObjPosS3)+"\t"+str(VObjNegS3)+"\t"+str(AtrPosS3)+"\t"+str(AtrNegS3)+"\n")

#Sin promediar


#Aplicamos los shifters (conmutadores de polaridad)

'''
shifter_presentS1 = False
shifter_presentS2 = False
shifter_presentS3 = False

for sh in shifters:
	if sh in textoS1:
		shifter_presentS1 = True
	
	if sh in textoS2:
		shifter_presentS2 = True

	if sh in textoS3:
		shifter_presentS3 = True
		

print shifter_presentS1
print shifter_presentS2
print shifter_presentS3

#En caso de presencia de un shifter hay que invertir el valor de las cargas en cada característica, lo pos a neg y lo neg a pos.
#Para S1
if shifter_presentS1 == True:
	temp = SumVObjPosS1
	SumVObjPosS1 = SumVObjNegS1
	SumVObjNegS1 = temp

	temp = SumAtrPosS1
	SumAtrPosS1 = SumAtrNegS1
	SumAtrNegS1 = temp

	temp = SumSAdjPosS1
	SumSAdjPosS1 = SumSAdjNegS1
	SumSAdjNegS1 = temp


#Para S2
if shifter_presentS2 == True:
	temp = SumVObjPosS2
	SumVObjPosS2 = SumVObjNegS2
	SumVObjNegS2 = temp

	temp = SumAtrPosS2
	SumAtrPosS2 = SumAtrNegS2
	SumAtrNegS2 = temp

	temp = SumSAdjPosS2
	SumSAdjPosS2 = SumSAdjNegS2
	SumSAdjNegS2 = temp

#Para S3
if shifter_presentS3 == True:
	temp = SumVObjPosS3
	SumVObjPosS3 = SumVObjNegS3
	SumVObjNegS3 = temp

	temp = SumAtrPosS3
	SumAtrPosS3 = SumAtrNegS3
	SumAtrNegS3 = temp

	temp = SumSAdjPosS3
	SumSAdjPosS3 = SumSAdjNegS3
	SumSAdjNegS3 = temp

'''


#Aplicamos los conmutadores de polaridad
#Shifters a la frase actual y shifters para frase previa

#VObjS1

AcumVObjPosXfraseS1 = []
AcumVObjNegXfraseS1 = []
posAcum = 0

f_evaluada = ""

for f, s in zip(numFraseVerboObj, seccionesVerboObj):
	
	AcumVObjPosS1 = 0
	AcumVObjNegS1 = 0

	if f != f_evaluada and s == 'S1':

		tieneNegacion = False
		
		#Conmutadores de frase actual
		contVObjS1 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contVObjS1 == 0:
					for lp, ln in zip(ListSumVObjPosS1, ListSumVObjNegS1):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumVObjPosS1 += cargaPatronPos
							AcumVObjNegS1 += cargaPatronNeg

							
						#i += 1
					
					AcumVObjPosXfraseS1.append(AcumVObjPosS1)
					AcumVObjNegXfraseS1.append(AcumVObjNegS1)
					posAcum += 1

					contVObjS1 += 1
					break
					#print "\n"


		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumVObjPosS1, ListSumVObjNegS1):
				if lp[0] == f:
					AcumVObjPosS1 += lp[1]
					AcumVObjNegS1 += ln[1]

			AcumVObjPosXfraseS1.append(AcumVObjPosS1)
			AcumVObjNegXfraseS1.append(AcumVObjNegS1)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumVObjPosXfraseS1) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumVObjPosXfraseS1[posAcum-2]
					AcumVObjPosXfraseS1[posAcum-2] = AcumVObjNegXfraseS1[posAcum-2]
					AcumVObjNegXfraseS1[posAcum-2] = tm

					break


#VObjS2

AcumVObjPosXfraseS2 = []
AcumVObjNegXfraseS2 = []
posAcum = 0

f_evaluada = ""

for f, s in zip(numFraseVerboObj, seccionesVerboObj):
	
	AcumVObjPosS2 = 0
	AcumVObjNegS2 = 0

	
	if f != f_evaluada and s == 'S2':
		
		tieneNegacion = False

		contVObjS2 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contVObjS2 == 0:
					for lp, ln in zip(ListSumVObjPosS2, ListSumVObjNegS2):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumVObjPosS2 += cargaPatronPos
							AcumVObjNegS2 += cargaPatronNeg					

						#i += 1

					AcumVObjPosXfraseS2.append(AcumVObjPosS2)
					AcumVObjNegXfraseS2.append(AcumVObjNegS2)
					posAcum += 1
	
					contVObjS2 += 1
					break
					#print "\n"

		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumVObjPosS2, ListSumVObjNegS2):
				if lp[0] == f:
					AcumVObjPosS2 += lp[1]
					AcumVObjNegS2 += ln[1]

			AcumVObjPosXfraseS2.append(AcumVObjPosS2)
			AcumVObjNegXfraseS2.append(AcumVObjNegS2)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumVObjPosXfraseS2) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior

					tm = AcumVObjPosXfraseS2[posAcum-2]
					AcumVObjPosXfraseS2[posAcum-2] = AcumVObjNegXfraseS2[posAcum-2]
					AcumVObjNegXfraseS2[posAcum-2] = tm

					break


#VObjS3
AcumVObjPosXfraseS3 = []
AcumVObjNegXfraseS3 = []
posAcum = 0

f_evaluada = ""

for f, s in zip(numFraseVerboObj, seccionesVerboObj):
	
	AcumVObjPosS3 = 0
	AcumVObjNegS3 = 0

	if f != f_evaluada and s == 'S3':
		
		tieneNegacion = False

		contVObjS3 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contVObjS3 == 0:
					for lp, ln in zip(ListSumVObjPosS3, ListSumVObjNegS3):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumVObjPosS3 += cargaPatronPos
							AcumVObjNegS3 += cargaPatronNeg					

						#i += 1
					
					AcumVObjPosXfraseS3.append(AcumVObjPosS3)
					AcumVObjNegXfraseS3.append(AcumVObjNegS3)
					posAcum += 1
	
					contVObjS3 += 1
					break
					#print "\n"


		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumVObjPosS3, ListSumVObjNegS3):
				if lp[0] == f:
					AcumVObjPosS3 += lp[1]
					AcumVObjNegS3 += ln[1]
			
			AcumVObjPosXfraseS3.append(AcumVObjPosS3)
			AcumVObjNegXfraseS3.append(AcumVObjNegS3)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumVObjPosXfraseS3) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumVObjPosXfraseS3[posAcum-2]
					AcumVObjPosXfraseS3[posAcum-2] = AcumVObjNegXfraseS3[posAcum-2]
					AcumVObjNegXfraseS3[posAcum-2] = tm

					break



#AtrS1
AcumAtrPosXfraseS1 = []
AcumAtrNegXfraseS1 = []
posAcum = 0

f_evaluada = ""


for f, s in zip(numFraseAtr, seccionesAtr):
	
	AcumAtrPosS1 = 0
	AcumAtrNegS1 = 0

	
	if f != f_evaluada and s == 'S1':
	
		tieneNegacion = False

		contAtrS1 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contAtrS1 == 0:
					for lp, ln in zip(ListSumAtrPosS1, ListSumAtrNegS1):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumAtrPosS1 += cargaPatronPos
							AcumAtrNegS1 += cargaPatronNeg					

						#i += 1
	
					AcumAtrPosXfraseS1.append(AcumAtrPosS1)
					AcumAtrNegXfraseS1.append(AcumAtrNegS1)
					posAcum += 1
		
					contAtrS1 += 1
					break
					#print "\n"


		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumAtrPosS1, ListSumAtrNegS1):
				if lp[0] == f:
					AcumAtrPosS1 += lp[1]
					AcumAtrNegS1 += ln[1]

			AcumAtrPosXfraseS1.append(AcumAtrPosS1)
			AcumAtrNegXfraseS1.append(AcumAtrNegS1)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumAtrPosXfraseS1) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumAtrPosXfraseS1[posAcum-2]
					AcumAtrPosXfraseS1[posAcum-2] = AcumAtrNegXfraseS1[posAcum-2]
					AcumAtrNegXfraseS1[posAcum-2] = tm

					break



#AtrS2
AcumAtrPosXfraseS2 = []
AcumAtrNegXfraseS2 = []
posAcum = 0

f_evaluada = ""

for f, s in zip(numFraseAtr, seccionesAtr):
	
	AcumAtrPosS2 = 0
	AcumAtrNegS2 = 0


	
	if f != f_evaluada and s == 'S2':
		
		tieneNegacion = False

		contAtrS2 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contAtrS2 == 0:
					for lp, ln in zip(ListSumAtrPosS2, ListSumAtrNegS2):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumAtrPosS2 += cargaPatronPos
							AcumAtrNegS2 += cargaPatronNeg					

						#i += 1
					
					AcumAtrPosXfraseS2.append(AcumAtrPosS2)
					AcumAtrNegXfraseS2.append(AcumAtrNegS2)

					contAtrS2 += 1
					break
					#print "\n"

		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumAtrPosS2, ListSumAtrNegS2):
				if lp[0] == f:
					AcumAtrPosS2 += lp[1]
					AcumAtrNegS2 += ln[1]

			AcumAtrPosXfraseS2.append(AcumAtrPosS2)
			AcumAtrNegXfraseS2.append(AcumAtrNegS2)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumAtrPosXfraseS2) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumAtrPosXfraseS2[posAcum-2]
					AcumAtrPosXfraseS2[posAcum-2] = AcumAtrNegXfraseS2[posAcum-2]
					AcumAtrNegXfraseS2[posAcum-2] = tm

					break



#AtrS3
AcumAtrPosXfraseS3 = []
AcumAtrNegXfraseS3 = []
posAcum = 0

f_evaluada = ""


for f, s in zip(numFraseAtr, seccionesAtr):
	
	AcumAtrPosS3 = 0
	AcumAtrNegS3 = 0
	
	if f != f_evaluada and s == 'S3':
		
		tieneNegacion = False

		contAtrS3 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contAtrS3 == 0:
					for lp, ln in zip(ListSumAtrPosS3, ListSumAtrNegS3):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumAtrPosS3 += cargaPatronPos
							AcumAtrNegS3 += cargaPatronNeg					

						#i += 1
						
					AcumAtrPosXfraseS3.append(AcumAtrPosS3)
					AcumAtrNegXfraseS3.append(AcumAtrNegS3)
						
					contAtrS3 += 1
					break
					#print "\n"


		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumAtrPosS3, ListSumAtrNegS3):
				if lp[0] == f:
					AcumAtrPosS3 += lp[1]
					AcumAtrNegS3 += ln[1]

			AcumAtrPosXfraseS3.append(AcumAtrPosS3)
			AcumAtrNegXfraseS3.append(AcumAtrNegS3)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumAtrPosXfraseS3) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumAtrPosXfraseS3[posAcum-2]
					AcumAtrPosXfraseS3[posAcum-2] = AcumAtrNegXfraseS3[posAcum-2]
					AcumAtrNegXfraseS3[posAcum-2] = tm

					break


#SAdjS1
AcumSAdjPosXfraseS1 = []
AcumSAdjNegXfraseS1 = []
posAcum = 0

f_evaluada = ""

for f, s in zip(numFraseSAdj, seccionesSAdj):
	
	AcumSAdjPosS1 = 0
	AcumSAdjNegS1 = 0

	if f != f_evaluada and s == 'S1':
		
		tieneNegacion = False

		contSAdjS1 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contSAdjS1 == 0:
					for lp, ln in zip(ListSumSAdjPosS1, ListSumSAdjNegS1):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumSAdjPosS1 += cargaPatronPos
							AcumSAdjNegS1 += cargaPatronNeg					

						#i += 1
					
					AcumSAdjPosXfraseS1.append(AcumSAdjPosS1)
					AcumSAdjNegXfraseS1.append(AcumSAdjNegS1)	
					
					contSAdjS1 += 1
					break
					#print "\n"

		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumSAdjPosS1, ListSumSAdjNegS1):
				if lp[0] == f:
					AcumSAdjPosS1 += lp[1]
					AcumSAdjNegS1 += ln[1]

			AcumSAdjPosXfraseS1.append(AcumSAdjPosS1)
			AcumSAdjNegXfraseS1.append(AcumSAdjNegS1)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumSAdjPosXfraseS1) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumSAdjPosXfraseS1[posAcum-2]
					AcumSAdjPosXfraseS1[posAcum-2] = AcumSAdjNegXfraseS1[posAcum-2]
					AcumSAdjNegXfraseS1[posAcum-2] = tm

					break




#SAdjS2
AcumSAdjPosXfraseS2 = []
AcumSAdjNegXfraseS2 = []
posAcum = 0

f_evaluada = ""


for f, s in zip(numFraseSAdj, seccionesSAdj):
	
	AcumSAdjPosS2 = 0
	AcumSAdjNegS2 = 0

	if f != f_evaluada and s == 'S2':
		
		tieneNegacion = False

		contSAdjS2 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contSAdjS2 == 0:
					for lp, ln in zip(ListSumSAdjPosS2, ListSumSAdjNegS2):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumSAdjPosS2 += cargaPatronPos
							AcumSAdjNegS2 += cargaPatronNeg					

						#i += 1
					
					AcumSAdjPosXfraseS2.append(AcumSAdjPosS2)
					AcumSAdjNegXfraseS2.append(AcumSAdjNegS2)

					contSAdjS2 += 1
					break
					#print "\n"

		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumSAdjPosS2, ListSumSAdjNegS2):
				if lp[0] == f:
					AcumSAdjPosS2 += lp[1]
					AcumSAdjNegS2 += ln[1]

			AcumSAdjPosXfraseS2.append(AcumSAdjPosS2)
			AcumSAdjNegXfraseS2.append(AcumSAdjNegS2)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumSAdjPosXfraseS2) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumSAdjPosXfraseS2[posAcum-2]
					AcumSAdjPosXfraseS2[posAcum-2] = AcumSAdjNegXfraseS2[posAcum-2]
					AcumSAdjNegXfraseS2[posAcum-2] = tm

					break


#SAdjS3
AcumSAdjPosXfraseS3 = []
AcumSAdjNegXfraseS3 = []
posAcum = 0

f_evaluada = ""

for f, s in zip(numFraseSAdj, seccionesSAdj):
	
	AcumSAdjPosS3 = 0
	AcumSAdjNegS3 = 0

	if f != f_evaluada and s == 'S3':
		
		tieneNegacion = False

		contSAdjS3 = 0
		for sh in shifters_frase_actual:
			if len(frases) > int(f) and sh in frases[int(f)].lower():
				tieneNegacion = True
				#print "I was here!"
				#Recorrer las listas e invertir las polaridades en la frase actual
				#i = 0 # para la posición en las listas Sum
				if contSAdjS3 == 0:
					for lp, ln in zip(ListSumSAdjPosS3, ListSumSAdjNegS3):

						id_fPos = lp[0]
						cargaPatronPos = lp[1]

						id_fNeg = ln[0]
						cargaPatronNeg = ln[1]

						#print id_fPos
						#print f

						#Aquí se invierten las cargas
						if id_fPos == f:

							f_evaluada = f
							
							#print "frase: " + f + " por presencia del conmutador " + sh + "\n"
							#print "se debe invertir la polaridad  de las cargas: pos = " + str(cargaPatronPos) + " y neg = " + str(cargaPatronNeg)

							#print "Pos: " + id_fPos + "\t" + str(cargaPatronPos)
							#print "Neg: " + id_fNeg + "\t" + str(cargaPatronNeg)

							#ListSumVObjPosS1[i] = [f, cargaPatronNeg]    #Por si se quiere trabajar como lista
							#ListSumVObjNegS1[i] = [f, cargaPatronPos]

							tm = cargaPatronPos
							cargaPatronPos = cargaPatronNeg
							cargaPatronNeg = tm

							AcumSAdjPosS3 += cargaPatronPos
							AcumSAdjNegS3 += cargaPatronNeg					

						#i += 1
					
					AcumSAdjPosXfraseS3.append(AcumSAdjPosS3)
					AcumSAdjNegXfraseS3.append(AcumSAdjNegS3)

					contSAdjS3 += 1
					break
					#print "\n"

		if tieneNegacion == False:
			f_evaluada = f		
			for lp, ln in zip(ListSumSAdjPosS3, ListSumSAdjNegS3):
				if lp[0] == f:
					AcumSAdjPosS3 += lp[1]
					AcumSAdjNegS3 += ln[1]

			AcumSAdjPosXfraseS3.append(AcumSAdjPosS3)
			AcumSAdjNegXfraseS3.append(AcumSAdjNegS3)
			posAcum += 1

		#Aplicamos los conmutadores de frase previa
		if len(AcumSAdjPosXfraseS3) > 1:	#Para garantizar que hay frase previa y evitar error de indice
			
			#Conmutadores de frase previa
			for sh in shifters_frase_previa:
				if len(frases) > int(f) and sh in frases[int(f)].lower():

					#Se aplica el conmutador de frase previa haciendo que la carga de la frase anterior se invierta.
					#Se podría pensar como trabajo futuro una forma de ampliar la cobertura de estos conmutadores más allá de la frase
					#inmediatamente anterior
					tm = AcumSAdjPosXfraseS3[posAcum-2]
					AcumSAdjPosXfraseS3[posAcum-2] = AcumSAdjNegXfraseS3[posAcum-2]
					AcumSAdjNegXfraseS3[posAcum-2] = tm

					break


#Computamos de nuevo los acumulados de carga para cada característica
#VObjPosS1
f1 = 0
for s in AcumVObjPosXfraseS1:
	f1 += s

#VObjNegS1
f2 = 0
for s in AcumVObjNegXfraseS1:
	f2 += s

#AtrPosS1
f3 = 0
for s in AcumAtrPosXfraseS1:
	f3 += s

#AtrNegS1
f4 = 0
for s in AcumAtrNegXfraseS1:
	f4 += s

#SAdjPosS1
f5 = 0
for s in AcumSAdjPosXfraseS1:
	f5 += s

#SAdjNegS1
f6 = 0
for s in AcumSAdjNegXfraseS1:
	f6 += s

#####################

#VObjPosS2
f7 = 0
for s in AcumVObjPosXfraseS2:
	f7 += s

#VObjNegS2
f8 = 0
for s in AcumVObjNegXfraseS2:
	f8 += s

#AtrPosS2
f9 = 0
for s in AcumAtrPosXfraseS2:
	f9 += s

#AtrNegS2
f10 = 0
for s in AcumAtrNegXfraseS2:
	f10 += s

#SAdjPosS2
f11 = 0
for s in AcumSAdjPosXfraseS2:
	f11 += s

#SAdjNegS2
f12 = 0
for s in AcumSAdjNegXfraseS2:
	f12 += s

######################

#VObjPosS3
f13 = 0
for s in AcumVObjPosXfraseS3:
	f13 += s

#VObjNegS3
f14 = 0
for s in AcumVObjNegXfraseS3:
	f14 += s

#AtrPosS3
f15 = 0
for s in AcumAtrPosXfraseS3:
	f15 += s

#AtrNegS3
f16 = 0
for s in AcumAtrNegXfraseS3:
	f16 += s

#SAdjPosS3
f17 = 0
for s in AcumSAdjPosXfraseS3:
	f17 += s

#SAdjNegS3
f18 = 0
for s in AcumSAdjNegXfraseS3:
	f18 += s


#features.write(str(AcumVObjPosS1)+"\t"+str(AcumVObjNegS1)+"\t"+str(AcumAtrPosS1)+"\t"+str(AcumAtrNegS1)+"\t"+str(AcumSAdjPosS1)+"\t"+str(AcumSAdjNegS1)+"\t"+str(AcumVObjPosS2)+"\t"+str(AcumVObjNegS2)+"\t"+str(AcumAtrPosS2)+"\t"+str(AcumAtrNegS2)+"\t"+str(AcumSAdjPosS2)+"\t"+str(AcumSAdjNegS2)+"\t"+str(AcumVObjPosS3)+"\t"+str(AcumVObjNegS3)+"\t"+str(AcumAtrPosS3)+"\t"+str(AcumAtrNegS3)+"\t"+str(AcumSAdjPosS3)+"\t"+str(AcumSAdjNegS3)+"\n")

#features.write(str(SumVObjPosS1)+"\t"+str(SumVObjNegS1)+"\t"+str(SumAtrPosS1)+"\t"+str(SumAtrNegS1)+"\t"+str(SumSAdjPosS1)+"\t"+str(SumSAdjNegS1)+"\t"+str(SumVObjPosS2)+"\t"+str(SumVObjNegS2)+"\t"+str(SumAtrPosS2)+"\t"+str(SumAtrNegS2)+"\t"+str(SumSAdjPosS2)+"\t"+str(SumSAdjNegS2)+"\t"+str(SumVObjPosS3)+"\t"+str(SumVObjNegS3)+"\t"+str(SumAtrPosS3)+"\t"+str(SumAtrNegS3)+"\t"+str(SumSAdjPosS3)+"\t"+str(SumSAdjNegS3)+"\n")

features.write(str(f1)+"\t"+str(f2)+"\t"+str(f3)+"\t"+str(f4)+"\t"+str(f5)+"\t"+str(f6)+"\t"+str(f7)+"\t"+str(f8)+"\t"+str(f9)+"\t"+str(f10)+"\t"+str(f11)+"\t"+str(f12)+"\t"+str(f13)+"\t"+str(f14)+"\t"+str(f15)+"\t"+str(f16)+"\t"+str(f17)+"\t"+str(f18)+"\n")

features.close()
FileVObjPos.close()
FileVObjNeg.close()
FileAtrPos.close()
FileAtrNeg.close()


print "Finished without errors!\n"
