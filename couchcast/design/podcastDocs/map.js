function (doc) {
  if (doc._attachments) {
    for (i in doc._attachments) {
      var attachment = doc._attachments[i];
      if (attachment.content_type == 'audio/mpeg') {
        if (doc.couchcast_pubdatetime) {
          var pubdatetime = doc.couchcast_pubdatetime.replace(' ','T');
        } else {
          var pubdatetime = null;
        }
        emit(pubdatetime, doc);
      }
    }
  }
}