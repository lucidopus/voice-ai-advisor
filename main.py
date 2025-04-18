import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect

from utils.prompts import ADVISOR_PROMPT, AI_INITIATION_PROMPT
from utils.config import AZURE_API_KEY, PORT, WEBSOCKET_URI
from utils.functions import (
    GET_STUDENT_ID,
    SEND_EMAIL,
    ANNOUNCE_DEADLINES,
    RECOMMEND_COURSES,
)
from utils.helper import (
    get_student_summary,
    extract_arguments,
    get_deadlines,
    get_docs,
    send_email,
    get_email_from_cwid,
)


VOICE = "alloy"
LOG_EVENT_TYPES = [
    "error",
    "response.content.done",
    "rate_limits.updated",
    "response.done",
    "input_audio_buffer.committed",
    "input_audio_buffer.speech_stopped",
    "input_audio_buffer.speech_started",
    "session.created",
]
SHOW_TIMING_MATH = False

global client_phone, student_email

app = FastAPI()


@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}


@app.api_route("/incoming_call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()

    # Access all the call configurations here:

    body_bytes = await request.body()

    try:
        body_dict = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        body_dict = dict(await request.form())

    # <Say> punctuation to improve text-to-speech flow
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        uri=WEBSOCKET_URI,
        extra_headers={
            "Authorization": f"Bearer {AZURE_API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        },
    ) as openai_ws:
        await initialize_session(openai_ws)

        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data["event"] == "media" and openai_ws.open:
                        latest_media_timestamp = int(data["media"]["timestamp"])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data["media"]["payload"],
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data["event"] == "start":
                        stream_sid = data["start"]["streamSid"]
                        print(f"Incoming stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data["event"] == "mark":
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response["type"] in LOG_EVENT_TYPES:
                        # print(f"Received event: {response['type']}", response)
                        arguments = extract_arguments(response)

                        if arguments != None:

                            if "cwid" in arguments.keys():
                                print()
                                print()
                                print()
                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print("Preparing to get student Summary...")
                                print()
                                cwid = arguments["cwid"]
                                student_summary = get_student_summary(cwid)
                                student_email = get_email_from_cwid(cwid)
                                print(student_summary)
                                student_summary_event = {
                                    "type": "session.update",
                                    "session": {
                                        "instructions": f"Here's the student's short summary, remember to confirm these details with the student:\n{student_summary}",
                                    },
                                }
                                await openai_ws.send(json.dumps(student_summary_event))

                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print()
                                print()
                                print()

                            if "subject" in arguments.keys():
                                print()
                                print()
                                print()
                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print("Preparing to send email...")
                                print()
                                subject = arguments["subject"]
                                body = arguments["body"]
                                send_email(subject=subject, body=body, cc=student_email)

                                human_advisor_event = {
                                    "type": "session.update",
                                    "session": {
                                        "instructions": "Explain to the student that their request has been forwarded to a human advisor and that they’ve been copied on the email. Let them know they should check their Stevens email account for the message. If they don’t see it, suggest checking the spam or junk folder. Mention that they can reply directly to the email if they have follow-up questions."
                                    },
                                }
                                await openai_ws.send(json.dumps(human_advisor_event))

                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print()
                                print()
                                print()

                            if "query" in arguments.keys():
                                print()
                                print()
                                print()
                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print("Preparing to recommend courses...")
                                print()
                                query = arguments["query"]
                                print(query)
                                recommendations = get_docs(query)
                                print(recommendations)

                                course_recommendations_event = {
                                    "type": "session.update",
                                    "session": {
                                        "instructions": f"Present these course recommendations to the student. For each course, highlight the course code, title, and a brief reason why it matches their interests.\n{recommendations}"
                                    },
                                }
                                await openai_ws.send(
                                    json.dumps(course_recommendations_event)
                                )

                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print()
                                print()
                                print()

                            if "is_right_time" in arguments.keys():
                                print()
                                print()
                                print()
                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print("Preparing to announce deadlines...")
                                print()
                                if arguments["is_right_time"]:
                                    announcements = get_deadlines()
                                print(announcements)

                                deadlines_event = {
                                    "type": "session.update",
                                    "session": {
                                        "instructions": f"Before concluding the conversation, mention these important upcoming deadlines to the student. Present them in chronological order, with the most urgent ones first, and highlight any that are particularly relevant to this student's situation.\n{announcements}"
                                    },
                                }
                                await openai_ws.send(json.dumps(deadlines_event))

                                print(
                                    "+++++++++++++++++++++++++++++++++++++++++++++++++"
                                )
                                print()
                                print()
                                print()

                    if (
                        response.get("type") == "response.audio.delta"
                        and "delta" in response
                    ):
                        audio_payload = base64.b64encode(
                            base64.b64decode(response["delta"])
                        ).decode("utf-8")
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": audio_payload},
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                print(
                                    f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms"
                                )

                        if response.get("item_id"):
                            last_assistant_item = response["item_id"]

                        await send_mark(websocket, stream_sid)

                    # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                    if response.get("type") == "input_audio_buffer.speech_started":
                        print("Speech started detected.")
                        if last_assistant_item:
                            print(
                                f"Interrupting response with id: {last_assistant_item}"
                            )
                            await handle_speech_started_event()
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            print("Handling speech started event.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    print(
                        f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms"
                    )

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        print(
                            f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms"
                        )

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time,
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({"event": "clear", "streamSid": stream_sid})

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"},
                }
                await connection.send_json(mark_event)
                mark_queue.append("responsePart")

        await asyncio.gather(receive_from_twilio(), send_to_twilio())


async def send_initial_conversation_item(openai_ws):
    """Send initial conversation item if AI talks first."""
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": AI_INITIATION_PROMPT,
                }
            ],
        },
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))


async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": ADVISOR_PROMPT,
            "tools": [
                GET_STUDENT_ID,
                SEND_EMAIL,
                ANNOUNCE_DEADLINES,
                RECOMMEND_COURSES,
            ],
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        },
    }
    print("Sending session update:", json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

    # Have the AI speak first
    # await send_initial_conversation_item(openai_ws)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
