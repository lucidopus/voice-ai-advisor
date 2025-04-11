import json
import pandas as pd

from datetime import datetime
from pinecone import Pinecone
from langchain_openai import AzureOpenAIEmbeddings
from azure.communication.email import EmailClient
from langsmith import Client

from utils.database import dummy_database
from utils.config import (
    AZURE_EMAIL_URI,
    ADVISOR_NAME,
    AZURE_API_KEY,
    AZURE_EMAIL,
    HUMAN_ADVISOR_EMAIL,
    PINECONE_API_KEY,
    COURSES_DATA_PATH,
    PINECONE_INDEX,
    AZURE_EMBEDDINGS_BASE,
    AZURE_EMBEDDING_MODEL,
    LANGSMITH_API_KEY,
    LANGSMITH_ACADEMIC_ADVISOR_PROMPT_IDENTIFIER,
    LANGSMITH_AI_INITIATION_PROMPT_IDENTIFIER,
)

embedding_model = AzureOpenAIEmbeddings(
    api_key=AZURE_API_KEY,
    azure_endpoint=AZURE_EMBEDDINGS_BASE,
    model=AZURE_EMBEDDING_MODEL,
)


client = EmailClient.from_connection_string(AZURE_EMAIL_URI)
langsmith_client = Client(api_key=LANGSMITH_API_KEY)


def get_advisor_prompt():
    prompt = langsmith_client.pull_prompt(LANGSMITH_ACADEMIC_ADVISOR_PROMPT_IDENTIFIER)
    prompt = prompt.messages[0].prompt.format(ADVISOR_NAME=ADVISOR_NAME)
    return prompt

def get_ai_initiation_prompt():
    prompt = langsmith_client.pull_prompt(LANGSMITH_AI_INITIATION_PROMPT_IDENTIFIER)
    prompt = prompt.messages[0].prompt.format(ADVISOR_NAME=ADVISOR_NAME)
    return prompt


def get_email_from_cwid(cwid):
    """
    Retrieve a student's email address using their Campus-wide ID (CWID).

    Args:
        cwid (str): The unique identifier for the student.

    Returns:
        str: The student's email address.

    """

    try:
        student_email_id = dummy_database["students"][cwid]["email"]
    except KeyError:
        return "I'm not sure if I have the correct CWID as I could not pull up records for that CWID. Could you please confirm if you've mentioned the correct CWID?"

    return student_email_id


def get_student_summary(cwid):
    """
    Retrieve an academic summary for the student associated with the given CWID.

    Args:
        cwid (str): The Campus-wide ID of the student.

    Returns:
        str: A summary including the student's major, current semester, courses taken, and CGPA.

    """
    try:
        student_summary = dummy_database["students"][cwid]["summary"]
    except KeyError:
        return "I couldn't pull up your records in the database, could you confirm if you've mentioned the correct CWID?"

    return student_summary


def extract_arguments(response):
    try:
        output = response.get("response", {}).get("output", [])
        for item in output:
            arguments = item.get("arguments")
            if arguments:
                return json.loads(arguments)
    except Exception as e:
        print("Error extracting arguments:", e)
    return None


def get_docs(query: str):
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX)
    df = pd.read_csv(COURSES_DATA_PATH)
    embedding = embedding_model.embed_query(query)

    try:
        res = index.query(
            vector=embedding,
            include_metadata=True,
            include_values=False,
            namespace="courses",
            top_k=4,
        )
    except Exception as e:
        print("ERROR!")
        print(str(e))

    ids = [int(i["id"]) for i in res["matches"]]
    summaries = "\n\n".join(df.loc[df["bp_id"].isin(ids)]["summary"].tolist())
    return summaries


def send_email(subject: str, body: str, cc: str) -> str:
    try:
        message = {
            "senderAddress": AZURE_EMAIL,
            "recipients": {
                "to": [{"address": HUMAN_ADVISOR_EMAIL}],
                "cc": [{"address": cc}],
            },
            "content": {
                "subject": subject,
                "plainText": body,
            },
        }

        poller = client.begin_send(message)
        result = poller.result()
        return result

    except Exception as ex:
        print("Failed to send email:", ex)
        return None


def get_deadlines():
    """
    Retrieve and format a list of upcoming academic deadlines.

    Returns:
        str: A formatted string listing each deadline with its corresponding date (in words)
             and description, sorted by date in ascending order.
    """
    deadlines = dummy_database["deadlines"]
    sorted_items = sorted(deadlines.items())  # Sort by ISO date strings (YYYY-MM-DD)

    return (
        "\n\n\t"
        + "\n\t".join(
            f"{i+1}. {datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')}: {desc}"
            for i, (date, desc) in enumerate(sorted_items)
        )
        + "\n".strip()
    )
