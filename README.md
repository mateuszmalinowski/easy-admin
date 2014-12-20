easy-admin
==========

### Intro

A bunch of files that simplify my administrative work including quicker navigation through a filesystem with a path memorization or ssh to a remote machine while preserving the same path.

### Dots 

Configuration of my bash.
It uses a script sshcd.bash that ssh to a remote machine and cd to the current path (the remote machine must have an access to the current path visible on local machine). This script is handy if working on a Distributed File System. The usage is the same as ssh: sshcd login@remote.

### Notification Daemon

#### Script
A notification daemon that takes a list of the notification recipients (.daemons/seminar_list_example.csv) and sends a notification to them according to date. Warning: Some changes in the code are required in order to provide a proper path.

#### Data
seminar_list_example.csv contains a 'tab' separated fields - date, name, e-mail - of every recipient.
