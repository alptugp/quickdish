#!/bin/bash

if [[ -n "$DYNO" ]]; then
  echo "Running in Heroku environment"
  export IN_HEROKU="true"
else
  echo "Running in DoC VM environment"
  export IN_HEROKU="false"
fi

# Run your main command or start the application
exec "$@"