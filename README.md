# Assistant
... is like a task manager, which allows scheduling of python scripts and enables communication between them via messaging.
Scripts can send notifications to a messenger of choice.

Main use case: implement repetitive task as a script, schedule and receive notifications to messenger.<br/>

## Notable features:
  - Jobs: add, schedule, enable, disable, check next run, view a list, save and load from a file.
  - Messenger: receive messages from jobs. *Slack specific*: Assistant creates channels for each job (if it sends messages).
  - Message broker enables possibility to create a more sophisticated setup with jobs communicating with each other via special events. (TBD)
  - settings.json 

## Requirements:
- RabbitMQ. Enables communication between jobs and Assistant.
- Python specific packages (see requirements.txt).
- Messenger that supports API calls (default is Slack).

## OK, how do I use it?
  - Scheduling mechanism requires computer to be awake to some degree... (Compute Stick, mini PC, cloud, ...).
  - Create a folder for Assistant to keep all things in one place.
  - Clone the project and install it ("pip install -e", "pip install -r requirements.txt").
  - Install RabbitMQ. Installing it as a service might be useful.
  - Launch assistant from the workspace, and exit. It will create settings.json with default configuration.
    - Configure Slack to receive notifications:
      - Create Slack application with scopes: *channels:read, chat:write, files:write, groups:read, groups:write*.<br/>
        See "Create an app" in api.slack.com.
      - Configure *token* and *user_id* in settings.json -> messenger.
      - Your Slack *user_id* is required for Assistant to add you to channels created for scheduled jobs.
    - To configure another messenger, implement it in messenger.py first:)
  - Implement a script, add and schedule a job (see j.add, j.sched).<br/>
    See tests/example_job.py, which sends test message.
  - If needed, save jobs configuration into a file (j.save), or review automatically created jobs.json (if configured).
  - Press *enter* for help.
