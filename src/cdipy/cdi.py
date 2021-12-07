import json
import requests

from .config import CONFIG_MAP

class LoginException(Exception):
    pass

class RequestException(Exception):
    pass


class CDISpace:

    def __init__(self, address, session, data):
        self.address = address
        self.session = session
        self.data = data

        self.id = data['roomId']
        self.name = data['name']
        self.position = data['position']
        
        if self.id in CONFIG_MAP:
            self.floor = CONFIG_MAP[self.id]['floor']
            self.door = CONFIG_MAP[self.id]['doorId']
            if 'zone' in CONFIG_MAP[self.id]:
                self.lights = CONFIG_MAP[self.id]['zone']['all']
                self.light_configs = {
                    key: CONFIG_MAP[self.id]['zone'][key] for key in CONFIG_MAP[self.id]['zone'] if key != 'all'
                }
            else:
                self.lights = None
                self.light_configs = None
        else:
            self.floor = None
            self.door = None


    def set_lights(self, level, selection='all'):
        if self.lights is None:
            return
        if type(selection) is str:
            if selection == 'all':
                selection = self.lights
            else:
                selection = self.light_configs[selection]
        
        print('Setting lights', selection, 'to level', level)
        levels = [ level if light in selection else 0 for light in self.lights  ]
        url = f'http://{self.address}/api/areaControl/setLightsLevel?'
        for level in levels:
            url += f'levels={level}&'
        for light in self.lights:
            url += f'lights={light}&'
        url += f'sessionKey={self.session}'
        request = requests.put(url)
        response = json.loads(request.text)
        if response['callStatus'] != 'SUCCEED':
            raise RequestException(response)
        return response['data']

    def open_door(self):
        if self.door is None or self.floor is None:
            print('This area does not have a door that can be remote controlled.')
            return
        request = requests.put(f'http://{self.address}/api/areaControl/openDoor?doorId={self.door}&floor={self.floor}&sessionKey={self.session}')
        response = json.loads(request.text)
        if response['callStatus'] != 'SUCCEED':
            raise RequestException(response)
        return response['data']

    def set_temperature(self, temperature):
        request = requests.put(f'http://{self.address}/api/areaControl/setACTargetTemperature?roomId={self.id}&temperature={temperature}&sessionKey={self.session}')
        response = json.loads(request.text)
        if response['callStatus'] != 'SUCCEED':
            raise RequestException(response)
        return response['data']


class CDI:

    def __init__(self, address, user, password):
        self.address = address
        self.session = None
        self.spaces = []
        self.spaces_by_id = {}
        self.spaces_by_name = {}

        self.login(user, password)
        spaces = self.space_information()
        for data in spaces:
            space = CDISpace(self.address, self.session, data)
            self.spaces.append(space)
            self.spaces_by_id[space.id] = space
            self.spaces_by_name[space.name] = space
            print('Created space', space.name)

    def login(self, user, password):
        request = requests.get(f'http://{self.address}/api/user/login?userName={user}&userPWD={password}')
        response = json.loads(request.text)
        if response['callStatus'] != 'SUCCEED':
            raise LoginException(response)
        self.session = response['sessionKey']
        return True

    def space_information(self):
        request = requests.get(f'http://{self.address}/api/space/all')
        response = json.loads(request.text)
        if response['callStatus'] != 'SUCCEED':
            raise RequestException(response)
        return response['data']