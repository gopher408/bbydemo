from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging, os
from datastore.aws_datastore import AWSDataStore
from config.banter_config import BanterConfig
from communication.chat import Chat
from communication.sms import SMS
from communication.echo import Echo
from banter_app import BanterClient
import urlparse
import json


cacheClients = {}


@api_view(['POST'])
def send(request):
    print('send')
    print(request.data)

    conversationID = request.data['id']
    if not conversationID in cacheClients:
        partner = 'nordstrom'
        if 'partner' in request.data:
            partner = request.data['partner']
            if partner.startswith('nordstrom'):
                partner = 'nordstrom'
        name = 'Nordstrom'
        if partner == 'nordstrom':
            name = 'Nordstrom'
        elif partner == 'target':
            name = 'Target'
        elif partner == 'bestbuy':
            name = 'BestBuy'

        grammerConfig = BanterConfig(partner, 'case12.fcfg')
        cacheClients[conversationID] = {
            'grammerConfig': grammerConfig,
            'partner': partner,
                    'agent': BanterClient(name, grammerConfig, Chat(), AWSDataStore(partner, None)),
            'customer': BanterClient(None, grammerConfig, Chat(), None)
        }

    work(conversationID, request.data['text'])

    response = {}

    return Response(
        {
            'status': 'OK',
            'response': {
                'to': cacheClients[conversationID]['customer'].get_name(),
                'from': cacheClients[conversationID]['agent'].get_name(),
                'response': cacheClients[conversationID]['agent'].get_communication().get_response(),
                'agent': True,
                'user': False,
                'products': None
            }
        })

cacheClients = {}

@api_view(['POST','GET'])
def sendSMS(request):
    logging.warning('sendSMS')
    logging.warning(request.content_type)
    logging.warning(request.body)

    data = None
    if request.content_type.startswith('text/plain'):
        data = json.loads(request.body)
    else:
        data = request.data
    logging.warning(data)

    #{u'from': {u'endpoint': u'14086556273', u'type': u'Number'}, u'timestamp': u'2016-08-18T04:56:03.2442796Z', u'to': {u'endpoint': u'14152364963', u'type': u'Number'}, u'version': 1, u'message': u'Hi', u'event': u'incomingSms'}
    #{"type": "incomingSms", "messageId": "abcd1234",
    # "timestamp": "2011-01-02 16:52:30 UTC",
    # "from": "+15125551234", "recipient": "512530",
    # "text": "the message body"}

    if 'type' in data and data['type'] != 'incomingSms':
        logging.warning(data['type'])
        return Response()

    text = ''
    smsfrom = ''
    smsto = ''
    if 'Body' in data:
        text = data['Body']
    elif 'message' in data:
        text = data['message']
    elif 'text' in data:
        text = data['text']

    if 'From' in data:
        smsfrom = data['From']
    elif 'from' in data and 'endpoint' in data['from']:
        smsfrom = data['from']['endpoint']
    elif 'from' in data:
        smsfrom = data['from']
    if 'To' in data:
        smsto = data['To']
    elif 'to' in data and 'endpoint' in data['to']:
        smsto = data['to']['endpoint']
    elif 'to' in data:
        smsto = data['to']
    elif 'recipient' in data:
        smsto = data['recipient']

    conversationID = smsfrom + smsto

    if not cacheClients.has_key(conversationID):
        #+18312268370
        #+18312268372
        #+16506678411

        partner = 'nordstrom'
        name = "Nordstrom"
        if smsto == '+18312268372':
            partner = 'nordstrom'
            name = 'Nordstrom'
        elif smsto == '+15042268374':
            partner = 'nordstrom'
            name = 'Nordstrom'
        elif smsto == '+18312268378':
            partner = 'nordstrom'
            name = 'Nordstrom'
        elif smsto == '+16506678411':
            partner = 'bestbuy'
            name = 'Best Buy'
        else:
            partner = 'nordstrom'
            name = 'Nordstrom'

        grammerConfig = BanterConfig(partner, 'case12.fcfg')
        cacheClients[conversationID] = {
            'grammerConfig': grammerConfig,
            'partner': partner,
            'agent': BanterClient(name, grammerConfig, SMS(smsfrom, smsto), AWSDataStore(partner, None)),
            'customer': BanterClient(None, grammerConfig, Echo(), None)
        }

    work(conversationID, text)

    return Response()


def work(conversationID, text):
    print('work')
    print(text)
    if text.lower() == 'unstop' or text.lower() == 'start':
        cacheClients[conversationID]['agent'].retransmit()
    else:
        cacheClients[conversationID]['customer'].question(text)
        cacheClients[conversationID]['agent'].converse(text)


@api_view(['GET'])
def get(request):
    logging.warning('get')
    logging.warning(request.data)

    return Response()

@api_view(['GET'])
def getProducts(request):
    logging.warning('getProducts')
    logging.warning(request.GET)

    ids = request.GET.getlist('pid')
    color = request.GET.get('color')
    partner = request.GET.get('partner')
    if not ids:
        return Response()

    ds = AWSDataStore(partner, None)
    products = ds.getMulti(ids)

    for product in products:
        if color and 'colors' in product:
            colorChoices = ds.getColors(product['id'])
            if colorChoices and len(colorChoices) and not color.lower() in product['color'].lower() :
                for colorChoice in colorChoices:
                    if color.lower() in colorChoice['color'].lower():
                        product['img'] = colorChoice['img']
                        product['color'] = colorChoice['color']
                        u = urlparse.urlparse(product['link'])
                        u = u._replace(query=None)
                        product['link'] = u.geturl() + '?' + 'fashioncolor=' + colorChoice['color']

    return Response({'products': products, 'status': 'OK'})
