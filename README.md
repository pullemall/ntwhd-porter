# ntwhd-porter
Simple captcha bot which asks to define and enter symbols from picture. If user enter right symbols bot send message which set in hello_message.txt. Otherwise user will be kicked.

## Deployment process on Ubuntu
#### Preparing virtualenv
Clone repo into ```/home/your-username/``` path
. Create a virtual environment in ```ntwhd-porter``` directory
```
cd ntwhd-porter
virtualenv venv
```
Run virtual environment and install dependeces
```
source venv/bin/activate
pip install -r requirements.txt
```
#### Create bot
Create a telegram bot with [BotFather](https://t.me/BotFather) and copy bot token into ```config.yaml```. Add bot to telegram chat and give him permissions to ban users and delete messages. Get a chat id (you can simply write "test" in chat and then make GET request to https://api.telegram.org/bot[TOKEN]/getUpdates) and set it in ```config.yaml```

#### Config supervisor program
Copy the ```ntwhd-porter.conf``` file to ```/etc/supervisor/conf.d/```.
Edit the config file set in ```command``` path to ```/home/username/ntwhd-porter/venv/bin/python3 script.py```.
Set the ```stderr_logfile``` and ```stdout_logfile``` for stderr and stdout output.
Reread supervisor configs
```
sudo supervisorctl reread
```
Add program to supervisord
```
sudo supervisorctl add ntwhd-porter
```
And now you can check status of running process and make sure that your program is running
```
sudo supervisorctl status
```
To stop or start the program
```
sudo supervisorctl stop ntwhd-porter
sudo supervisorctl start ntwhd-porter
```