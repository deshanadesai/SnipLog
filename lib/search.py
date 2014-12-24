'''
Will contain everything related to Search feature

Search Philosophy:

**v1.**
Very Primitive.
If the query is : +tag1 +tag2 content
We take the snips with atleast these tags, and then choose the ones
that atleast have one of them words.

Ranking : Ranks based on the number of times words from the query appear
in the post's body + title combined.

'''
import re
from models import Post
from collections import Counter

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

def search_v1(query):
    '''**v1.**
	Very Primitive.
	If the query is : +tag1 +tag2 content
	We take the snips with atleast these tags, and then choose the ones
	that atleast have one of them words.

	The ones with none of those words are discarded.

	Ranking : Ranks based on the number of times words from the query appear
	in the post's body + title combined.
	'''
    qparsed = {}
    
    qparsed = queryparser(query)
    taglist = qparsed['taglist']
    wordlist = qparsed['contentstring'].split()

    #TODO : REMOVE STOPWORDS FROM THE QUERY.
    wordlist_set = set(wordlist)
    
    #DEBATE : Could be replaced with if either one of the tags present.
    
    #If atleast all the tags specified are present. 
    if len(taglist) !=0:
    	posts = Post.objects(tags__all=taglist)
    #If no tags, then use all the posts.
    else:
    	posts = Post.objects.all()

    #I am assuming the database won't be queried again if I work on its content.
    
    #Relevant posts are in this dictionary in the format : <Post>:score
    posts_relevant = {}

    wordlist_len = len(wordlist_set)
    
    for post in posts:
        #Get the bag of words from title and body of the post. Subtitle
        #not included as of now. Don't know the effect of get_bagofwords
        #on an empty field.
        body_split_list = post.get_bagofwords()
        # body_split_set = set(body_split_list)
        
        #This calculates word frequncy table of the post's text.
        body_freq = Counter(body_split_list)
        
        rel_score = 0
        #Score is the sum of the times word from query appears in the
        #text of the post.
        for word in wordlist_set:
            rel_score = rel_score + body_freq[word]
        if rel_score !=0:
            posts_relevant[post] = rel_score

    #Now we need to sort this dictionary according to rel_score
    import operator
    # sorted_posts_relevant = sorted(posts_relevant.items(), key=operator.itemgetter)
    sorted_posts_relevant = sorted(posts_relevant, key = posts_relevant.get, reverse=True)
    #The above is a list of posts.

    return sorted_posts_relevant


# test = raw_input()

# print queryparser(test)
