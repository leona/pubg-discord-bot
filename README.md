# Features
- PUBG API Monitoring for automatically posting match stats in "chicken-dinners" and "reports" channels
- http://pubg.report is monitored when you are in a voice channel and will get posted in "reports" text channel if you kill or get killed by a twitch streamer 
- https://pubg.sh telemetry timelapse is posted with each report. Very useful for seeing where that sneaky opponent was hiding after a game. 
- You must have a KD of at least 1 to join. This is currently how I want it, as playing in other discord servers without this was like playing on randoms. 
- Channels for people with > 1 KD and > 2 KD
- Currently squad only channels as I have not built support for duos yet 
- Channels are created and deleted on the fly to save space. There will always be one free channel. 

# Commands
- ;register <name> <region> - Currently only EU/NA are supported. This links your PUBG account for report notifications and also assigns your role for accessing voice channels 
- ;stat Shroud - Fetch season stats for a player
- ;help - List of commands 
- ;aim-guide - Displays wackyjackys aim guide 
- ;map - Randomly generated map choice 
- ;face - Randomly generated AI faces. Why not? 
- ;insult - Randomly generated insults. 
- ;kick - COMING SOON. Vote kick people from a channel for 1 hour. 
- Commands have shortcuts too. Use ;s to check your own stats. 

# RUNTIME

./bin/production-manage.sh

./bin/production-report.sh

;config-set listener.channel.name squad
;config-set notification.channel.streamReport reports
;config-set notification.channel.highRank reports

# Create tmux sessions
tmux new -s reporter

tmux new -s manager

# List sessions
tmux ls

# attach to sessions
tmux attach-session -t reporter

tmux attach-session -t manager

# CTRL + B D to exit

# cron
@reboot /bin/bash /home/discord/bin/production-report.sh
@reboot /bin/bash /home/discord/bin/production-manage.sh
