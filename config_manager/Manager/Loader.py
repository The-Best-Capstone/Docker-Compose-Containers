import subprocess
import os, json
try :
    from Logs import Logger
except ImportError :
    print("No log service")
    Logger = None 

ROOT = os.path.dirname(__file__)

class Configuration : 

    def __init__(self) -> None:
        self.path = None 
        self.containers = [
            {
                "name":"simulator",
                "enabled":False,
                "arguments":"",
                "Description":"Produce simulated 10Hz data for pipeline testing and validation",
            },
            {
                "name":"analog",
                "enabled":False,
                "arguments":"",
                "Description":"4-20mA and 0-10V Analog Channels",
            },
            {
                "name":"thermocouples",
                "enabled":False, 
                "arguments":"",
                "Description":"8 K-Type MAX31855 Thermocouple Channels",
            },
            {
                "name":"dsa",
                "enabled":False,
                "arguments":"191.30.80.150",
                "Description":"DSA 191.30.80.150 16 Pressure Channels",
            },
            {
                "name":"dsa",
                "enabled":False,
                "arguments":"191.30.80.152",
                "Description":"DSA 191.30.80.152 16 Pressure Channels",
            },
            {
                "name":"dsa",
                "enabled":False,
                "arguments":"191.30.80.154",
                "Description":"DSA 191.30.80.154 16 Pressure Channels",
            },
            {
                "name":"dsamps",
                "enabled":False,
                "arguments":"191.30.80.156",
                "Description":"MPS DSA 191.30.80.156 24 Pressure Channels",
            },
            {
                "name":"dsamps",
                "enabled":False,
                "arguments":"191.30.80.158",
                "Description":"MPS DSA 191.30.80.158 24 Pressure Channels",
            }
        ]
    
    def exportConfiguration(self, path) :
        self.path = path 
        if Logger :
            Logger.instance().logMessage("Export configuration: "+str(path))
        ## 
        # Write file
        try :
            json.dump(self.containers, open(path, "w")) 
        except Exception as err :
            ## TODO: prompt user of error
            pass
        else : 
            ## TODO: let user know success
            pass 

    def importConfiguration(self, path) : 
        self.path = path 
        if Logger :
            Logger.instance().logMessage("Import configuration: "+str(path))
        if os.path.exists(path) :
            try :
                config = json.load(open(path, "r")) 
            except Exception as err :
                if Logger :
                    Logger.instance().logMessage("Failed to import configuration.")
                    Logger.instance().logError(err)
            else :
                if Logger :
                    Logger.instance().logMessage("Configuration object successfully loaded.")
                self.containers = config 

    def dockerUP(self) :
        if Logger :
            Logger.instance().logMessage("Launching containers...")
        for container in self.containers : 
            if container["enabled"] == True : 
                try :
                    subprocess.call(["docker-compose", "-H", "ssh://pi@191.30.80.100", "-f", f"{os.path.expanduser('~')}/Docker-Compose-Containers/{container['name']}/docker-compose.yml", "up", "--build", "-d"])
                except Exception as e: 
                    ## TODO: display error better
                    if Logger :
                        Logger.instance().logError(e)
    
    def dockerDOWN(self) : 
        if Logger :
            Logger.instance().logMessage("Shutting down containers...")
        for container in self.containers : 
            if container["enabled"] == True : 
                try :
                    subprocess.call(["docker-compose", "-H", "ssh://pi@191.30.80.100", "-f", f"{os.path.expanduser('~')}/Docker-Compose-Containers/{container['name']}/docker-compose.yml", "down"])
                except Exception as e: 
                    ## TODO: display error better
                    if Logger :
                        Logger.instance().logError(e)

