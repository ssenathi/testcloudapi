"""Hello World API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""


import endpoints
import webapp2
import base64
import sys

from protorpc import messages
from protorpc import message_types
from protorpc import remote
import httplib2

from apiclient import discovery
from oauth2client import client as oauth2client

PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']
DEFAULT_TOPIC = "projects/sattestcloudapi/topics/mytopic"

def create_pubsub_client(http=None):
    credentials = oauth2client.GoogleCredentials.get_application_default()
    if credentials.create_scoped_required():
        credentials = credentials.create_scoped(PUBSUB_SCOPES)
    if not http:
        http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('pubsub', 'v1beta2', http=http)

# Create a global default client
# 

client = create_pubsub_client()

def create_default_topic():

  try:
    topic = client.projects().topics().create(name= DEFAULT_TOPIC, body={}).execute()
  except:
     print "Unexpected error:", sys.exc_info()[0]
    
  return

  
def create_topic_if_doesnt_exist():
    #client = create_pubsub_client()
    next_page_token = None
    resp = client.projects().topics().list(
        project='projects/sattestcloudapi',
        pageToken=next_page_token).execute()
    topics = resp['topics']
    
    if DEFAULT_TOPIC in topics:
      return False
    else:
      create_default_topic()
      return True
      
    return False

def publish_myevent(msg) :
  #client = create_pubsub_client()
  message1 = base64.urlsafe_b64encode(msg)
  # Create a POST body for the Pub/Sub request
  body = {
    'messages': [{'data': message1}]
    }
  resp = client.projects().topics().publish(
    topic=DEFAULT_TOPIC, body=body).execute()
  
  message_ids = resp.get('messageIds')
  if message_ids:
    return message_ids[0]
  
  

package = 'Hello'

default_topic = create_topic_if_doesnt_exist()

class Greeting(messages.Message):
  """Greeting that stores a message."""
  message = messages.StringField(1)


class GreetingCollection(messages.Message):
  """Collection of Greetings."""
  items = messages.MessageField(Greeting, 1, repeated=True)


STORED_GREETINGS = GreetingCollection(items=[
    Greeting(message='Hello Sathish!'),
    Greeting(message='Goodbye Sathish!'),
])


@endpoints.api(name='helloworld', version='v1')
class HelloWorldApi(remote.Service):
  """Helloworld API v1."""

  @endpoints.method(message_types.VoidMessage, GreetingCollection,
                    path='hellogreeting', http_method='GET',
                    name='greetings.listGreeting')
  def greetings_list(self, unused_request):
    publish_myevent("greetings_list")
    return STORED_GREETINGS

  ID_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      id=messages.IntegerField(1, variant=messages.Variant.INT32))

  @endpoints.method(ID_RESOURCE, Greeting,
                    path='hellogreeting/{id}', http_method='GET',
                    name='greetings.getGreeting')
  def greeting_get(self, request):
    try:
      publish_myevent("greeting_get")
      return STORED_GREETINGS.items[request.id]
    except (IndexError, TypeError):
      raise endpoints.NotFoundException('Greeting %s not found.' %
                                        (request.id,))

apiapp = endpoints.api_server([HelloWorldApi])


class MainHandler(webapp2.RequestHandler):
    def get(self):
        publish_myevent("homepage")
        self.response.write('Hello Sathish!')

mainapp = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)




