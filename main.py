#! /usr/bin/env python3
import time

from aiohttp import web
import json
import asyncio

from crosslab.api_client import APIClient
from crosslab.soa_client.device_handler import DeviceHandler
from crosslab.soa_services.file import FileService__Producer
from crosslab.soa_services.message import MessageService__Consumer, MessageServiceEvent
from latency import Latency

global waiting_for_response

async def main_async():
    latency_calc = Latency()

    async def run_server():
        app = web.Application()
        app.router.add_route('GET', '/', handle_index)
        app.router.add_route('POST', '/upload', measurement)
        app.router.add_route('GET', '/measure', measure)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8000)
        await site.start()

    async def handle_index(request):
        # Read the contents of the index.html file
        with open('index.html', 'r') as f:
            html_content = f.read()

        # Return the HTML content as the response
        return web.Response(text=html_content, content_type='text/html')

    async def upload(request):
        latency_calc.start()
        data = await request.post()
        uploaded_file = data['file']

        file_content = uploaded_file.file.read()
        print(file_content)
        await fileServiceProducer.sendFile("ino", file_content)
        return web.Response(text="LED turned on")

    async def measurement(request):
        data = await request.post()
        uploaded_file = data['file']
        file_content = uploaded_file.file.read()
        for i in range(0, 20):
            print(f"Iteration: {i}")
            global waiting_for_response
            waiting_for_response = True
            latency_calc.start()
            print(file_content)
            await fileServiceProducer.sendFile("ino", file_content)
            print("File sent!")
            while(waiting_for_response):
                print("Waiting...")
                await asyncio.sleep(1)

        await asyncio.sleep(3)
        latency_calc.calculateRTTJitter()
        latency_calc.calculateRTTNoUploadJitter()
        latency_calc.calculateRTTMetrics()
        latency_calc.calculateRTTNoUploadMetrics()
        latency_calc.saveAsJSON()
        latency_calc.saveMetricsAsTxt()


    async def measure(request):
        latency_calc.calculateRTTJitter()
        latency_calc.calculateRTTNoUploadJitter()
        latency_calc.calculateRTTMetrics()
        latency_calc.calculateRTTNoUploadMetrics()
        latency_calc.saveAsJSON()
        latency_calc.saveMetricsAsTxt()

    # read config from file
    with open("config.json", "r") as configfile:
        conf = json.load(configfile)

    # debug; delete for prod
    print(conf)

    deviceHandler = DeviceHandler()

    fileServiceProducer = FileService__Producer("file")
    deviceHandler.add_service(fileServiceProducer)

    # --------------------------------------------------------------#
    #   I/O                                                         #
    # --------------------------------------------------------------#
    # message service:
    messageServiceConsumer = MessageService__Consumer("message")

    async def onMessage(message: MessageServiceEvent):
        global waiting_for_response
        print("Received Message of type", message["message_type"])
        print("Message content:", message["message"])
        latency_calc.calculateLatency(message["message"])
        latency_calc.printLatency()
        waiting_for_response = False

    messageServiceConsumer.on("message", onMessage)
    deviceHandler.add_service(messageServiceConsumer)
    url = conf["auth"]["deviceURL"]

    async with APIClient(url) as client:
        client.set_auth_token(conf["auth"]["deviceAuthToken"])
        # Create the HTTP server as a coroutine task
        server_task = asyncio.create_task(run_server())

        deviceHandlerTask = asyncio.create_task(
            deviceHandler.connect("{url}/devices/{did}".format(
                url=conf["auth"]["deviceURL"],
                did=conf["auth"]["deviceID"]
            ), client)
        )

        await asyncio.gather(server_task, deviceHandlerTask)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

