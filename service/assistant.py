from api.openai.assistant import AssistantType, ChatGPTAssistant
from domain.common_db import get_openai_session, create_openai_session
from service.agents.manager import ManagerDialogue


class ChatManager:
    def __init__(self):
        self.client = ChatGPTAssistant()
        self._dialogues = {}
        self._current_dialogue: ManagerDialogue = self.get_assistant_dialogue(2, AssistantType.ATAdvisor, "")

    def get_assistant_dialogue(self, project_id: int, assistant_type: AssistantType, reason):
        session = get_openai_session(project_id, assistant_type.value)
        if session is None:
            session_id = self.client.create_session("", assistant_type, reason)
            session = create_openai_session(project_id, assistant_type.value, session_id, reason)

        if session.session_id not in self._dialogues:
            if assistant_type == AssistantType.ATAdvisor:
                self._dialogues[session.session_id] = ManagerDialogue(session, self.client)
            if assistant_type == AssistantType.ATManager:
                self._dialogues[session.session_id] = ManagerDialogue(session, self.client)
        self._dialogues[session.session_id].is_debug = True

        return self._dialogues[session.session_id]

    async def dialogue_is_over(self):
        new_dialogue = self.get_assistant_dialogue(2, AssistantType.ATAdvisor, "")
        if new_dialogue != self._current_dialogue:
            self._current_dialogue = new_dialogue

    async def trigger(self, reason: str):
        new_dialogue = self.get_assistant_dialogue(2, AssistantType.ATManager, reason)
        if new_dialogue != self._current_dialogue:
            self._current_dialogue = new_dialogue

        return await self._current_dialogue.trigger(reason)

    async def human_message_handler(self, msg: str):
        response = await self._current_dialogue.human_message(msg)
        if self._current_dialogue.is_finished:
            await self.dialogue_is_over()
        return response
