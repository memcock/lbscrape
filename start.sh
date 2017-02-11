#!/usr/bin/with-contenv sh

mode="${1}" 
case ${mode} in 
   worker) 
      echo "Starting worker"
	    exec celery worker --app lbscrape --loglevel DEBUG
      ;; 
   master) 
      echo "Starting master"
      exec gunicorn -b 0.0.0.0 lbscrape:app.app
      ;; 
   *)  
      echo "`basename ${0}`:usage: [ worker, master ]" 
      exit 1 # Command to come out of the program with status 1
      ;; 
esac 