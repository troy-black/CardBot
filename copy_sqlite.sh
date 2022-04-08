#!/bin/bash

rm -f app.db

sshpass -p "pi" scp -r pi@cardbot:~/CardBot/app.db app.db
