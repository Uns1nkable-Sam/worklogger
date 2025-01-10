# Worklogger

This project helps developers track their working hours easily. It is achieved through periodic analysis of code changes. The system collects commits over a certain period, calculates the difference between them, and also takes into account granular worklogs. This data is then passed on to an AI assistant in a form of prompts, which generates a brief and clear summary of the work done. Output can later be uploaded to time tracking system, such as Enji or Jira, or used in the chat for writing a daily standup for the team. Using this tool, you get transparency by typing just a few command lines.

# Prerequisites

- [Poetry](https://python-poetry.org/)
- [PostgreSQL](https://www.postgresql.org/) (inclundig `libpq`)
- [OpenAI API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).

## Development installation

1. Install required prerequisites.
2. Define `OPENAI_API_KEY` environment variable with your key value.
3. Clone this project and switch to its working directory.
4. Run `poetry install`
