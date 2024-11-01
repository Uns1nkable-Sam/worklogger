import asyncio
import enum
import re

from openai import OpenAI

from api.openai.client import OPENAI_API_KEY


class AssistantType(enum.Enum):
    ATWayward = "wayward",
    ATAdvisor = "advisor",
    ATManager = "manager",
    ATPatchInterpreter = "patch_interpreter",
    ATCommitInterpreter = "commit_interpreter",


assistant_ids = {
    AssistantType.ATAdvisor: "asst_i3zH9r9dHqOgTnBwYPumz8xg",
    AssistantType.ATWayward: "asst_7ENsOUS5RLWiUPr6RBWuVagC",
    AssistantType.ATManager: "asst_RNmE0gdAFZaiy4nFNPQUD7LI",
    AssistantType.ATPatchInterpreter: "asst_7ENsOUS5RLWiUPr6RBWuVagC",
    AssistantType.ATCommitInterpreter: "asst_7ENsOUS5RLWiUPr6RBWuVagC",
}


class ChatGPTAssistant:
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            organization='org-5BSIHvHSUBcynZRbeEb8JlA3',
            project='proj_ZtYgjcThjp1ulUrMZUKukn5n',
        )
        self.assistant_id = assistant_ids[AssistantType.ATAdvisor]

    def create_session(self, system_text, assistant_type: AssistantType, reason):
        thread = self.client.beta.threads.create()
        self.assistant_id = assistant_ids[assistant_type]
        return thread.id

    async def message(self, session_id, role: str, content_text: str, is_repeat: bool = False):

        print(f'Role: {role}\nText:{content_text}\n')
        try:
            message = self.client.beta.threads.messages.create(
                thread_id=session_id,
                role=role,
                content=content_text,
            )
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=session_id,
                assistant_id=self.assistant_id,
            )
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=session_id,
                    order="desc",
                    limit=2,
                )
                response_text = messages.data[0].content[0].text.value
                return response_text.removeprefix("```json").removesuffix('```').strip('\n\r\t ')
            else:
                error = run.last_error.message
                print(f'Run status is: {run.status}\n')
                print(f'Error is: {error}')
                if is_repeat:
                    return None
                if error.startswith('Rate limit reached'):
                    # Regular expression to extract the number of seconds
                    match = re.search(r'try again in (\d+\.?\d*)s', error)

                    # Extract the seconds if found
                    if match:
                        seconds = float(match.group(1)) + 1
                        print(f"Seconds to wait: {seconds}")
                        await asyncio.sleep(seconds)
                        return await self.message(session_id, role, content_text, True)
                return None

        except Exception as e:
            print(f"Error calling Assistant API: {e}")
            return "Could not generate response"

    def ask(self, session_id, content_text):
        try:
            # Send the user's message to the assistant within the specified session
            response = self.client.chat.create(
                # assistant_id=self.assistant_id,
                session_id=session_id,
                message={
                    "role": "user",
                    "content": content_text
                },
                max_tokens=250
            )
            return response.content

        except Exception as e:
            print(f"Error calling Assistant API: {e}")
            return "Could not generate response"
