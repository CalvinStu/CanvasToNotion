import requests
import json
from requests.structures import CaseInsensitiveDict
from notion_client import Client
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import time
import yaml

with open("private.yaml", 'r') as file:
    private = yaml.safe_load(file)

# ======================== VARIABLES ========================
# ---------------- CANVAS COURSE ----------------
coursesUrl = f"https://{private['Canvas']['District_domain']}/api/v1/courses"
canvasHeaders = CaseInsensitiveDict()
canvasHeaders['Authorization'] = "Bearer "+ private['Canvas']['API_Key']
courseParams = {"enrollment_state": "active"}

# ---------------- CANVAS ASSIGNMENTS ----------------
assignmentsParams = {"include[]": "submission"}

# ---------------- NOTION READ WRITE  ----------------
NOTION_TOKEN = private['Notion']['API_Key']
DATABASE_ID = private['Notion']['Database_ID']
notion = Client(auth=NOTION_TOKEN)
checkUrl = []
pageIDs = {} #dictionary where checkUrl is term, notion pg id is definition
notionReadResponse = []
# ---------------- TELEGRAM ----------------
TGbotToken = private['Telegram']['Bot_Token']
TGchatID = private['Telegram']['Chat_ID']

# ======================== FUNCTIONS ========================
# ---------------- CANVAS ASSIGNMENTS function ----------------
def fetch_assignments(course_id):
    pass
# ---------------- NOTION READ function ----------------
def notion_read():
    global notionReadResponse
    global checkUrl
    global pageIDs

    checkUrl = []
    pageIDs = {}


    ##ahhhh
    notionReadResponse = []
    has_more = True
    next_cursor = None

    while has_more:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            start_cursor=next_cursor
        )

        notionReadResponse.extend(response["results"])
        has_more = response.get("has_more", False)
        next_cursor = response.get("next_cursor", None)

    ##AHHH

    #print(f"\033[37mAssignments in Notion: {len(notionReadResponse['results'])}\033[0m")  # should be >0 if notion DB has pages
    print(f"\033[37mAssignments in Notion: {len(notionReadResponse)}\033[0m") ##ahh


    for page in notionReadResponse: ##ahh

        props = page['properties']
        url = props.get("Link", {}).get("url")
        if url:
            checkUrl.append(url)
            pageIDs[url] = page['id']
            #print(props.get("Due"))
    #print(checkUrl)
    #print(pageIDs)
# ---------------- NOTION WRITE function ----------------
def notion_write(assignmentInfo,linkInfo,classInfo,dueInfo):
    assignment
    
    #print(notion_pull_specific_page(assignment['html_url'])['Completed']['status']['name']) #magiccccccc
    print
    if assignment['html_url'] not in checkUrl:
        
        notionProps = {
            "Assignment": {
                "title": [{"text": {"content": f"{assignmentInfo}"}}]},
            "Link": {"url":f"{linkInfo}"},
            "Class":{"select":{"name":f"{classInfo}"}},
            "Completed":{"status": {"name": f"{canvas_completed_to_notion_completed(assignment.get('submission', {}).get('workflow_state'))}"}}
        }

        if assignment.get("due_at"):
            if (t := datetime.fromisoformat(assignment.get("due_at").replace("Z", "+00:00"))
                    .astimezone(ZoneInfo("America/Los_Angeles"))).hour == 23 and t.minute == 59:
            #2026-01-20T20:18:00Z
            #if assignment.get("due_at");
                notionProps['Due'] = {"date": {
                    "start": datetime.fromisoformat("2025-10-13T06:59:59Z".replace("Z", "+00:00"))
                        .astimezone(ZoneInfo("America/Los_Angeles"))
                        .date()
                        .isoformat()
                    }
                }
            else:
                notionProps['Due'] = {"date": {"start": dueInfo}}

        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=notionProps
        )

        print(f"\033[32mAdding {assignmentInfo}\033[0m")
        notify_via_telegram(assignmentInfo,"added to notion")

    else:
        if notion_pull_specific_page(assignment['html_url'])['Completed']['status']['name'] == "Incomplete" and canvas_completed_to_notion_completed(assignment.get('submission', {}).get('workflow_state')) == "Completed":
            notion_update_completed(assignment['html_url'])
            print(f"\033[33mUpdating {assignmentInfo} marked completed\033[0m")
            notify_via_telegram(assignmentInfo, "marked completed")
        
        if assignment.get('submission', {}).get('workflow_state') == "unsubmitted":
            if dueInfo:
                notion.pages.update(
                        page_id=pageIDs[assignment['html_url']],
                        properties={"Due": {"date": {"start": dueInfo}}}
                )
            else:
                try:
                    notion.pages.update(
                        page_id=pageIDs[assignment['html_url']],
                        properties={"Due": {"date": None}}
                    )
                except:
                    print("\033[31mnotion update error\033[0m")
                    send_telegram("notion update error")
            print(f"\033[37m{assignmentInfo} already in notion, due date may be updated\033[0m")

def canvas_completed_to_notion_completed(Completed):
        if assignment.get('submission', {}).get('workflow_state') == "unsubmitted":
            return "Incomplete"
        else:
            return "Completed"

# ---------------- NOTION UPDATE functions ----------------
def notion_pull_specific_page(url):
    page = notion.pages.retrieve(page_id=pageIDs[url])
    return page['properties']

def notion_update_completed(url):
    #notionProps
    notion.pages.update(
        page_id=pageIDs[url],
        properties={"Completed": {"status": {"name": "Completed"}}}
    )

def notion_update_time():
    t = time.localtime()
    notion.databases.update(
        database_id=DATABASE_ID,
        description=[
        {
            "type": "text",
            "text": {"content": f"Last Updated: {t.tm_mon}/{t.tm_mday} {t.tm_hour%12}:{t.tm_min} {'pm' if t.tm_hour >= 12 else 'am'}"}
        }
    ]
    )
# ---------------- TELEGRAM ----------------
def notify_via_telegram(name,message):
    assignment
    assignment['html_url']
    send_telegram(f'<a href="{assignment["html_url"]}">{name}</a> {message}')
    
def telegram_check_status():
    updates = requests.get(f"https://api.telegram.org/bot{TGbotToken}/getUpdates").json()
    for u in updates['result']:
        if "message" in u and u['message']['text'] == "/status":
            chat_id = u['message']['chat']['id']
            send_telegram("Script is running")
            update_id = u['update_id'] + 1
            requests.get(f"https://api.telegram.org/bot{TGbotToken}/getUpdates", params={"offset": update_id})

def send_telegram(msg):
    response = requests.post(
        f"https://api.telegram.org/bot{TGbotToken}/sendMessage",
            json={
                "chat_id": TGchatID,
                "text": f"{msg}",
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
        )
    print(response.status_code)




# ======================== MAIN ========================

send_telegram("starting")
print("sent")
# ---------------- COURSES ----------------
while True:
    print("Fetching Course Info...")

    courseResp = requests.get(coursesUrl, headers=canvasHeaders, params=courseParams)

    if courseResp.status_code == 200:
        courseDict = {}
        for course in courseResp.json():
            courseDict[course['id']] = course['name']
        #print(f"\033[37m{courseDict}\033[0m")
    else:
        print("Error:", courseResp.status_code, courseResp.text)

    # ---------------- NOTION READ ----------------
    notion_read()
    # ---------------- ASSIGNMENTS ----------------
    print("Fetching Assignment Data...")

    for course_id, course_name in courseDict.items():
            #DEBUG print(course_id,"---", course_name)
        assignmentsUrl = f"https://{private['Canvas']['District_domain']}/api/v1/courses/{course_id}/assignments"
        assignmentsParams = {"include[]": "submission",
                            "per_page": 100}
            #print(assignmentsUrl)
        assignmentsResp = requests.get(assignmentsUrl, headers=canvasHeaders, params=assignmentsParams)
        assignmentsData = assignmentsResp.json()
            # DEBUG print(assignmentsData)

        for assignment in assignmentsData:
                #DEBUG print(f"{assignment['name']} |{assignment.get('due_at')}|{course_name}|{assignment.get('submission',{}).get('workflow_state')}|{assignment['html_url']}")
            if assignment.get("due_at") is None:
                if assignment.get("created_at") is not None:        #dont write if assignment was due more than 30 days ago or if it was created 60 days ago
                    if datetime.strptime(assignment.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) >= datetime.now(timezone.utc) - timedelta(days=60): 
                        notion_write(assignment.get('name'),assignment.get('html_url'),course_name,assignment.get("due_at"))
            else:    
                if datetime.strptime(assignment.get("due_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) >= datetime.now(timezone.utc) - timedelta(days=1):
                    notion_write(assignment.get('name'),assignment.get('html_url'),course_name,assignment.get("due_at"))

    print("\n\033[1m\033[32mDONE!\033[0m\n")
    telegram_check_status()
    notion_update_time()
    time.sleep(15*60)