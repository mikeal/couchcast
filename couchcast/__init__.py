import os, sys
from datetime import datetime

import iso8601
from couchquery import Database
from webenv import HtmlResponse
from webenv.rest import RestApplication
from mako.lookup import TemplateLookup

try:
    import json
except:
    import simplejson as json


this_directory = os.path.abspath(os.path.dirname(__file__))
design_doc = os.path.join(this_directory, 'design')
template_dir = os.path.join(this_directory, 'templates')

lookup = TemplateLookup(directories=[template_dir], encoding_errors='ignore', input_encoding='utf-8', output_encoding='utf-8')

class MakoResponse(HtmlResponse):
    def __init__(self, name, **kwargs):
        template = lookup.get_template(name+'.mko')
        kwargs['json'] = json
        self.body = template.render_unicode(**kwargs).encode('utf-8', 'replace')
        self.headers = []

class FeedResponse(MakoResponse):
    content_type = 'application/rss+xml'

class PodcastApplication(RestApplication):
    def __init__(self, db, title, description, default_entry_title, default_entry_description,
                 site_link, author, author_email, explicit, tags):
        super(PodcastApplication, self).__init__()
        self.db = db
        self.db.sync_design_doc('couchcast', design_doc)
        self.title = title
        self.description = description
        self.default_entry_title = default_entry_title
        self.default_entry_description = default_entry_description
        self.site_link = site_link
        self.author = author
        self.author_email = author_email
        self.explicit = explicit
        self.tags = tags
    
    def GET(self, request, collection):
        nulltimes = self.db.views.couchcast.podcastDocs(key=None)
        if len(nulltimes) is not 0:
            nulltimes.couchcast_pubdatetime = datetime.now().isoformat()
            for doc in nulltimes:
                if 'title' not in doc:
                    doc.title = self.default_entry_title
                if 'description' not in doc:
                    doc.description = self.default_entry_description
            self.db.save(nulltimes)
        items = self.db.views.couchcast.podcastDocs(descending=True)
        for item in items:
            item.attachment, item.attachment['filename'] = [
                                (item._attachments[i], i,) for i in item._attachments.keys() if
                                item._attachments[i].get('content_type') == 'audio/mpeg'][0]                                
            item.attachment['uri'] = self.db.uri+item['_id']+'/'+item.attachment['filename']
            item.pubdt = iso8601.parse_date(item.couchcast_pubdatetime)
        
        podcast = {'title':self.title, 'description':self.description, 'site_link':self.site_link,
                   'author':self.author, 'author_email':self.author_email, 'explicit':self.explicit,
                   'tags':self.tags, 'items':items,
                   }
        
        return FeedResponse(collection, podcast=podcast)

class Podcasts(RestApplication):
    def add_podcast(self, name, dburi, title, description, default_entry_title, default_entry_description, site_link, author, author_email, explicit=True, tags=['Technology']):
        db = Database(dburi)
        application = PodcastApplication(db, title, description, default_entry_title, default_entry_description, site_link, author, author_email, explicit, tags)
        self.add_resource(name, application)


def cli():
    from wsgiref.simple_server import make_server
    import imp
    appmodule = imp.load_source('appmodule', os.path.abspath(sys.argv[-1]))
    httpd = make_server('', 8888, appmodule.application)
    print "Serving on http://localhost:8888/"
    httpd.serve_forever()
