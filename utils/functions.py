GET_SUMMARY = {
    "type": "function",
    "name": "get_summary",
    "description": "Get a summary of the conversation so far. This happens before you or the student hangs up the call ",
    "parameters": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A summary of the conversation",
            }
        },
        "required": ["summary"],
        "strict": True,
    },
}

GET_STUDENT_ID = {
    "type": "function",
    "name": "get_student_id",
    "description": "Get the student's CWID",
    "parameters": {
        "type": "object",
        "properties": {
            "cwid": {
                "type": "string",
                "description": "The student's CWID",
            }
        },
        "required": ["cwid"],
        "strict": True,
    },
}

RECOMMEND_COURSES = {
    "type": "function",
    "name": "recommend_courses",
    "description": "Use a natural language query to search for relevant course recommendations from the catalog.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A natural language query about what the student is looking for in a course",
            }
        },
        "required": ["query"],
        "strict": True,
    },
}

SEND_EMAIL = {
    "type": "function",
    "name": "send_email",
    "description": "Use this when a situation requires escalation to a Human Academic Advisor",
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "Brief subject line with issue type and CWID",
            },
            "body": {
                "type": "string",
                "description": "Short email with Student info (name, CWID, major, year), Issue description, Specific request.",
            },
        },
        "required": ["subject", "body"],
        "strict": True,
    },
}

ANNOUNCE_DEADLINES = {
    "type": "function",
    "name": "announce_deadlines",
    "description": "Inform the student about the deadlines approaching during end of the call",
    "parameters": {
        "type": "object",
        "properties": {
            "is_right_time": {
                "type": "boolean",
                "description": "Whether it's the right time to announce the deadlines",
            }
        },
        "required": ["is_right_time"],
        "strict": True,
    },
}
