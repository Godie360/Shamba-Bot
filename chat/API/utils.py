import os
import typing
from typing import List

from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.memory import (
    ConversationBufferWindowMemory,
    SQLChatMessageHistory,
)
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
from sqlmodel import Session, select

prompt = ChatPromptTemplate(
    input_variables=["agent_scratchpad", "input", "chat_history"],
    input_types={
        "chat_history": typing.List[
            typing.Union[
                AIMessage,
                HumanMessage,
                ChatMessage,
                SystemMessage,
                FunctionMessage,
                ToolMessage,
                None,
            ]
        ],
        "agent_scratchpad": typing.List[
            typing.Union[
                AIMessage,
                HumanMessage,
                ChatMessage,
                SystemMessage,
                FunctionMessage,
                ToolMessage,
            ]
        ],
    },
    output_parser=JsonOutputParser(),
    messages=[
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="""You are Shamba Bot. Reply all questions in swahili language. Your topic is about Agriculture and Pests and Diseases and how to control them. Remember your are the smartest bot in the world. The question which will need example you should provide examples. Any question which will need explanation you should provide explanation. If you are not sure about the answer you can ask the user to provide more information. Remember to be polite and professional. Remmember again you are master of the field of Agriculture and Pests and Diseases so provide the best advice which sastify the user. Please answer all question in markdown format. You need to act calm and have respect to the user user and use calm language. Good luck!.
        """,
            )
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(input_variables=["input"], template="{input}")
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad", optional=True),
    ],
)


class CustomSQLMessageHistory(SQLChatMessageHistory):
    def __init__(
        self,
        session_id: str,
        connection_string: str = "sqlite:///./db.sqlite3",
        number_of_messages: int = 5,
        table_name: str = "message_store",
        session_id_field_name: str = "session_id",
    ):
        super().__init__(
            session_id=session_id,
            connection_string=connection_string,
            table_name=table_name,
            session_id_field_name=session_id_field_name,
        )
        self.number_of_messages = number_of_messages

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from PostgreSQL"""
        with Session(self.engine) as session:
            result = (
                session.exec(
                    select(self.sql_model_class)
                    .where(
                        getattr(self.sql_model_class, self.session_id_field_name)
                        == self.session_id
                    )
                    .order_by(self.sql_model_class.id.asc())
                    .limit(self.number_of_messages)
                )
            ).all()
            messages = []
            for record in result:
                messages.append(self.converter.from_sql_model(record))
            return messages

    def add_message(self, message: BaseMessage):
        """Add a message to the PostgreSQL database"""
        with Session(self.engine) as session:
            print(message)
            session.add(self.converter.to_sql_model(message))
            session.commit()
            session.refresh(message)
            return message


def get_local_history(hash_key: str, number_of_conversations: int = 10):
    memory = ConversationBufferWindowMemory(
        chat_memory=CustomSQLMessageHistory(
            session_id=hash_key,
            number_of_messages=number_of_conversations,
        ),
        return_messages=True,
        input_key="input",
        output_key="output",
        memory_key="chat_history",
        k=number_of_conversations,
    )

    return memory.chat_memory


load_dotenv()


class ShambaChat:
    def __init__(self, chat_id: str) -> None:
        self.chat_id = chat_id

    def init_model(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key is None:
            raise Exception("OpenAI API Key is not set")

        return ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)

    def response(self, message: str):
        """
        This function is used to get the response from the model
        """
        memory = get_local_history(self.chat_id)
        model = self.init_model()
        chain = LLMChain(
            model=model,
            prompt=prompt,
            memory=memory,
        )
        response = chain.invoke(
            {
                "input": message,
                "agent_scratchpad": [],
            }
        )
        return response


"""
my_bot = Chat("123")
my_bot.response(message="hi")

"""
