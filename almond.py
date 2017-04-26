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
        ws = create_connection("ws://10.10.10.254:7681/root/toasty")
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
            ws = create_connection("ws://10.10.10.254:7681/root/toasty")
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
        ws = create_connection("ws://10.10.10.254:7681/root/toasty")

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
        ws = create_connection("ws://10.10.10.254:7681/root/toasty")
        result = ws.recv()
        print(result)
        ws.send('{"MobileInternalIndex":"676","CommandType":"DeviceList"}')
        #time.sleep(20)
        result = ws.recv()
        print(result)
        s['data'] = result.replace('"', "'")
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

        #devicelist = json.loads(data)
        devicelist = jsonpickle.encode(data)
        print(devicelist.replace('"', "'"))
        devicelist = json.loads(devicelist)
        print(devicelist)

        for device in devicelist:
           #now values are dictionary
           for attribute, value in device.iteritems():
               print (attribute)

               #deviceparams = json.loads(frozen)
               #print (key, value)
               #yield from bot.coro_send_message(event.conv, _("%s : %s") % (key, value))
               yield from bot.coro_send_message(event.conv, _("%s") % (value))

                #for subsubkey, subsubvalue in subvalue.items():
    except ValueError:
        yield from bot.coro_send_message(event.conv, _("Error"))
