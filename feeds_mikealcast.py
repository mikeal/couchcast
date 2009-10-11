from couchcast import Podcasts

couchdb = {'name':'couchdb', 'title':'CouchDB Podcast', 
           'dburi':'http://localhost:5984/couchcast',
           'description':'CouchDB pushing pure relaxification in your ears',
           'default_entry_title':'CouchDB Podcast',
           'default_entry_description':'CouchDB Podcast with Chris Anderson and Jan Lehnardt',
           'site_link':'http://jchrisa.net', 
           'author':'Chris Anderson and Jan Lehnardt', 
           'author_email':'couchdb-podcast@couch.io'
           }

application = Podcasts()
application.add_podcast(**couchdb)



