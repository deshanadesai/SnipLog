'''
Will contain everything related to Search feature
'''
import re

TAGCHAR = '+'
def queryparser(query):
	'''
	Accepts js processed query, returns dict with 'taglist' and 
	'contentstring'

	Assumes that a search query is text with tags preceeded by TAGCHAR,
	and content is by default
	Multi word tags will be in quotation marks, this will be handled by
	the autocomplete js in the frontend
	
	Example: +'tag 1' +'tag' content

	'''
	patterntag = r"\+'(.*?)'"
	taglist = re.findall(patterntag, query)

	contentstring = re.sub(patterntag,'',query).strip(' ')

	return {'taglist':taglist,
			'contentstring':contentstring
			}


# test = raw_input()

# print queryparser(test)