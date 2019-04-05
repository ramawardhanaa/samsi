import subprocess
import time

time.sleep(30)
restart = subprocess.Popen(["sudo", "/etc/init.d/nginx", "restart"], stdout=subprocess.PIPE)
output = restart.communicate()[0]
print(output)