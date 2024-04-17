The way I think this is going to work is:

- There is an auto job that runs daily, every morning
- The auto job first asks an email REST API endpoint for a list of account_id that need email reminders
- Job then takes that list, and one by one sends a request to another endpoint that generates emails for that account
- After each "send" API call, wait 5 seconds or so to avoid overloading the server
- Each API call needs to have `X-API-KEY` token in the header that matches `os.environ.get("API_KEY")`

This might be overkill, but based on experience with Rams for Progress, you don't want all emails to try to send
out in a single request; it will time out. Instead, stagger your requests.