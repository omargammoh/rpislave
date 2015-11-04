#!/usr/bin/tmux source-file

echo ""
echo ""
echo "-------WELCOME-TO-RPISLAVE-------"
echo "this software was developed by omar gammoh (omar.gammoh@gmail.com)"
echo ""
echo "-> making sure the server is running in a tmux session"
session_name=rpislave
if (tmux has-session -t $session_name 2> /dev/null); then
	echo "  -> session already exists"
	echo "  ->" $(tmux ls)
else
	echo  "  -> session does not exist, starting new session"
	if [ "$TMUX" != "" ]; then
		echo "Error: cannot start session from within tmux."
		exit
	fi
    echo "  -> sudo python /home/pi/rpislave/prerun.py"
	sudo python /home/pi/rpislave/prerun.py
	tmux new-session -d -s $session_name
	tmux split-window -d -t $session_name -h
    echo "  -> sudo python /home/pi/rpislave/manage.py runserver 0.0.0.0:9001"
	tmux send-keys -t $session_name 'sudo python /home/pi/rpislave/manage.py runserver 0.0.0.0:9001' enter C-l
    echo "  -> session started sucessfully"
fi

echo ""
echo "some info for you:"
echo "  to attach the session: tmux a -t $session_name"
echo "  to kill the session: tmux kill-session -t $session_name"
echo "  to run the session: . /home/pi/rpislave/start.sh"
echo "  to update the rpislave: . /home/pi/rpislave/update.sh"
echo "  to run setup again: sudo python /home/pi/rpislave/setup.py"
echo "  to detach the session type: ctrl-b then d"
echo "  to switch panes type: ctrl-b then o"
echo "  to find out all the tmux shortcuts type: ctrl-b ? when in a tmux session"
echo "  to list ssh tunnels: ps aux|grep 'sudo ssh' |grep 900"
echo "--------------ENJOY--------------"
