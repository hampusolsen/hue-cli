import os
from typing import Optional
from urllib import request
import json

import typer
import rich
from click.exceptions import Abort


app = typer.Typer()


class Api:
    def __init__(self, ip: str, user: str) -> None:
        self.baseUrl = f"http://{ip}/api/{user}"

    def get_lights(self):
        with request.urlopen(f"{self.baseUrl}/lights") as response:
            return response.read().decode('utf-8')

    def get_light_by_id(self, id: int):
        with request.urlopen(f"{self.baseUrl}/lights/{id}") as response:
            return response.read().decode('utf-8')

    def get_scenes(self):
        with request.urlopen(f"{self.baseUrl}/scenes") as response:
            return response.read().decode('utf-8')

    def get_groups(self):
        with request.urlopen(f"{self.baseUrl}/groups") as response:
            return response.read().decode('utf-8')

    def put_group(self, id: int, data: bytes):
        req = request.Request(
            f"{self.baseUrl}/groups/{id}/action",
            method="PUT",
            data=data
        )

        with request.urlopen(req) as response:
            return response.read().decode('utf-8')


def create_api():
# modest attempt at having valid configuration
    USER = os.getenv("HUE_BRIDGE_API_USER")
    BRIDGE_IP = os.getenv("HUE_BRIDGE_IP")

    try:
        if BRIDGE_IP is None:
            BRIDGE_IP = typer.prompt("What's your Philips HUE Bridge IP-address?")
        if USER is None:
            USER = typer.prompt("What's your Philips HUE bridge API username?")
    except Abort:
        raise typer.Exit()

    return Api(BRIDGE_IP, USER)


@app.command()
def lights(id: Optional[int] = typer.Argument(None)):
    api = create_api()
    if id:
        lights = api.get_light_by_id(id)
    else:
        lights = api.get_lights()
    rich.print_json(lights)


@app.command()
def scenes():
    api = create_api()
    scenes = api.get_scenes()
    rich.print_json(scenes)


@app.command()
def groups(id: Optional[int] = typer.Argument(None), off: bool = typer.Option(False)):
    on = off == False
    api = create_api()
    if id:
        json_data = json.dumps({ "on": on })
        response = api.put_group(id, bytes(json_data, "utf-8"))
    else:
        response = api.get_groups()
    rich.print_json(response)


if __name__ == "__main__":
    app()
