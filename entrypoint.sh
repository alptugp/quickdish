#!/bin/bash

if [[ -n "$DYNO" ]]; then
  echo "Running in Heroku environment"
  export CMD_GUNICORN="cd drpproject && gunicorn drpproject.wsgi"
else
  echo "Running in DoC VM environment"
  export CMD_GUNICORN="cd drpproject && gunicorn --bind 0.0.0.0:8000 drpproject.wsgi"
fi

# Run your main command or start the application
exec "$@"