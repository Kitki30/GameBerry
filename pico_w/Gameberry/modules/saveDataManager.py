import modules.json as json
import modules.files as files
import utime as time

saving_path = "/system/user/savedata/"

def load():
    start = time.time()
    print()
    print("Loading save data:")
    if files.exist("/game/game_info.json"):
        print("Reading game info...")
        gameInfo = json.read("/game/game_info.json")
        saveDataInfo = gameInfo['saveDataManager']
        print("Game info:")
        print("Game ID: "+ gameInfo['id'])
        print("Game name: " + gameInfo['name'])
        print("Default save data file: "+saveDataInfo["default"])
        if saveDataInfo["format"] == "json":
            print("Checking if save data exists...")
            if files.exist(saving_path+gameInfo["id"]+".json"):
                print("Save data exists")
            else:
                print("Copying default save data ")
                files.copy("/game/"+saveDataInfo["default"], saving_path+gameInfo["id"]+".json")
            savefile = json.read(saving_path+gameInfo["id"]+".json")
            time_elapsed = start - time.time()
            print("Save data read in "+str(time_elapsed)+"s.")
            print("")
            return savefile
        else:
            print("Unsupported file format!")
            print("")
            return None
    else:
        print("Game info not found! Cannot load game data!")
        print("")
        return None
    
def save(data):
    start = time.time()
    print()
    print("Saving save data:")
    if files.exist("/game/game_info.json"):
        print("Reading game info...")
        gameInfo = json.read("/game/game_info.json")
        saveDataInfo = gameInfo['saveDataManager']
        print("Game info:")
        print("Game ID: "+ gameInfo['id'])
        print("Game name: " + gameInfo['name'])
        print("Default save data file: "+saveDataInfo["default"])
        if saveDataInfo["format"] == "json":
            print("Checking if save data exists...")
            if files.exist(saving_path+gameInfo["id"]+".json"):
                print("Save data exists")
            else:
                print("Copying default save data ")
                files.copy("/game/"+saveDataInfo["default"], saving_path+gameInfo["id"]+".json")
            savefile = json.write(saving_path+gameInfo["id"]+".json", data)
            time_elapsed = start - time.time()
            print("Save data saved in "+str(time_elapsed)+"s.")
            print("")
            return 0
        else:
            print("Unsupported file format!")
            print("")
            return 1
    else:
        print("Game info not found! Cannot load game data!")
        print("")
        return 1