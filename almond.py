import plugins
import asyncio
import websocket
import shelve
import json
import jsonpickle
#import thread
import time


def _initialise(bot):
    plugins.register_admin_command(["mode","off","refresh","list"])

def mode(bot, event, args):
    """
    Sets almond mode

    /bot mode <i>home</i>
    /bot mode <i>away</i>
    """

    if not args:
        yield from bot.coro_send_message(event.conv, _("Usage: /bot mode <i>home</i>"))
        return

    try:
        #ws logic here.

        from websocket import create_connection
        ws = create_connection("ws://10.10.10.254:7681/root/ready")
        if(args == 'home' or args == 'here'):
            ws.send('{"MobileInternalIndex":"544","CommandType":"UpdateAlmondMode","Mode":"2","EmailId":"jamen@airlim.com"}')
        if(args == 'away' or args == 'gone'):
            ws.send('{"MobileInternalIndex":"554","CommandType":"UpdateAlmondMode","Mode":"3","EmailId":"jamen@airlim.com"}')
        #print "Sent"
        #print "Receiving..."
        result =  ws.recv()
        print("Received '%s'" % result)
        ws.close()

        #response.
        yield from bot.coro_send_message(event.conv, _("OK"))
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error"))

def off(bot, event, args=''):
    """
    Turns on the off scene
    If an argument is supplied the sensor is sent an off command

    /bot off
    /bot off office
    """

    if not args:
        try:
            #ws logic here.
            from websocket import create_connection
            ws = create_connection("ws://10.10.10.254:7681/root/ready")
            ws.send('{"CommandType":"ActivateScene","MobileInternalIndex":"324","Scenes":{"ID":"7"}}')
            #print "Sent"
            #print "Receiving..."
            result =  ws.recv()
            print("Received '%s'" % result)
            ws.close()

            #response.
            yield from bot.coro_send_message(event.conv, _("OK"))
        except ValueError:
            yield from bot.coro_send_message(event.conv, _("Error"))
        return
    try:
        s = shelve.open('alias')
        try:
            existing = s[args]
        finally:
            s.close()

        print("found alias for %s" % existing)
        #ws logic here.
        from websocket import create_connection
        ws = create_connection("ws://10.10.10.254:7681/root/ready")

        ws.send('{"MobilInternalIndex":"543","CommandType":"UpdateDeviceIndex","ID":"1","Index":"1","Value":"false"}')
        #print "Sent"
        #print "Receiving..."
        result =  ws.recv()
        print("Received '%s'" % result)
        ws.close()

        #response.
        yield from bot.coro_send_message(event.conv, _("OK"))
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error"))

def refresh(bot, event):
    """
    Parses all devices for the almond

    /bot refresh
    """
    try:
        s = shelve.open('data')

        #ws logic here.
        from websocket import create_connection
        ws = create_connection("ws://10.10.10.254:7681/root/ready")
        result = ws.recv()
        print(result)
        ws.send('{"MobileInternalIndex":"676","CommandType":"DeviceList"}')
        #time.sleep(20)
        result = ws.recv()
        print(result)
        s['data'] = json.dumps(result)
        s.close()
        ws.close()
        #response.
        yield from bot.coro_send_message(event.conv, _("OK"))
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error"))

def list(bot, event):
    """
    Lists all parsed devices for the almond

    /bot list
    """
    try:
        s = shelve.open('data')
        try:
            data = s['data']
        finally:
            s.close()

        devicelist = json.loads(data)
        response = []
        for key , value in devicelist['Devices'].items():
            for subkey , subvalue in value.items():
                id = "";
                name = "";
                for subsubkey, subsubvalue in subvalue.items():
                    if(subsubkey == "ID"):
                        id = subsubvalue
                    if(subsubkey == "Name"):
                        name = subsubvalue
                        response.append(name + " - " + id) 
        yield from bot.coro_send_message(event.conv, _('<br>'.join(response) ))

    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error"))



def recursive_iter(obj):
    if isinstance(obj, dict):
        for item in obj.values():
            yield from recursive_iter(item)
    elif any(isinstance(obj, t) for t in (list, tuple)):
        for item in obj:
            yield from recursive_iter(item)
    else:
        yield obj
