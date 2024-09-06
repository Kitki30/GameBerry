import utime
import modules.json as json

data = json.read("/system/user/settings.json")

def get_timezoned():   
    time1=utime.time() 
    if data.get("timezone").get("timezone_on_minus") < 0:
        temp = data.get("timezone").get("timezone") * 3600
        temp2 = temp * 2
        timeminus = temp - temp2
        final = time1 + timeminus
        return final
    else:
        temp = 3600 * data.get("timezone").get("timezone")
        return time1 + temp
