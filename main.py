import pymysql
from neo4j import GraphDatabase, exceptions
import os
from dotenv import load_dotenv


load_dotenv()


conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST"), 
    user=os.getenv("MYSQL_USER"), 
    password=os.getenv("MYSQL_PASSWORD"), 
    database=os.getenv("MYSQL_DB"), 
    cursorclass=pymysql.cursors.DictCursor, 
    port=3306
    )


def print_menu():
    print("""
Conference Management
--------------------------
MENU
====
1 - View Speakers & Sessions
2 - View Attendees by Company
3 - Add New Attendee
4 - View Connected Attendees
5 - Add Attendee Connection
6 - View Rooms
x - Exit application""")
    choice = input("Choice: ")
    return choice


neo4jdriver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))  
    )


def get_names(tx, attendeeID):
    query = """
        MATCH (a:Attendee {AttendeeID: $ID})-[:CONNECTED_TO]-(b:Attendee)
        RETURN b.AttendeeID AS AttendeeID
    """
    results = tx.run(query, ID=attendeeID)
    IDs = []
    for result in results:
        IDs.append(result["AttendeeID"])
    return IDs


def connect_attendees(tx, attendee_one_ID, attendee_two_ID):
    with conn.cursor() as cursor:
        cursor.execute("""SELECT AttendeeID 
        FROM attendee
        WHERE AttendeeID IN %s
        """, ((attendee_one_ID, attendee_two_ID),)
        )
        attendees = cursor.fetchall()


        if len(list(attendees)) != 2:
            print("One or both of the attendee IDs does not exist")


        elif attendees:

            query = """
                    MATCH (a:Attendee {AttendeeID: $ID1})-[:CONNECTED_TO]-(b:Attendee {AttendeeID: $ID2})
                    RETURN a
                    """
            attendees_connected = tx.run(query, ID1=attendee_one_ID, ID2=attendee_two_ID).single()


            if not attendees_connected:
                tx.run("""
                    MATCH (a:Attendee {AttendeeID: $ID1}), (b:Attendee {AttendeeID: $ID2})
                    MERGE (a)-[:CONNECTED_TO]->(b)
                """, ID1=attendee_one_ID, ID2=attendee_two_ID)
                print(f"Attendee {attendee_one_ID} is now connected to attendee {attendee_two_ID}")


            else:
                print(f"Attendee {attendee_one_ID} were already connected to attendee {attendee_two_ID}")


def sql_queries():
    choice_six_selected = False


    while True:
        choice = print_menu()


        if choice == "1":
            speaker_name = input("Enter speaker name: ")
            query = """SELECT a.attendeeName AS Name, s.sessionTitle AS session, rm.roomName AS room 
                    FROM attendee AS a 
                    RIGHT JOIN registration AS r ON a.attendeeID = r.attendeeID 
                    RIGHT JOIN session AS s ON r.sessionID = s.sessionID 
                    RIGHT JOIN room AS rm ON s.roomID = rm.roomID
                    WHERE a.attendeeName LIKE %s"""
            

            with conn.cursor() as cursor:
                cursor.execute(query, (f"%{speaker_name}%",))
                subjects = cursor.fetchall()
                if not subjects:
                    print("No speaker found of that name")
                else:
                    print("""
-----------------------------------------------""")
                    for s in subjects:
                        print(f"{s['Name']}  |  {s['session']}  |  {s['room']}")
                    print("""-----------------------------------------------
                          """)
        

        if choice == "2":
            with conn.cursor() as cursor:
                

                while True:
                    companyID = input("Enter company ID: ")

                    cursor.execute("SELECT companyName FROM company WHERE companyID = %s", (companyID,))
                    company = cursor.fetchone()
                    
                    
                    if not company:
                        print(f"Company with ID {companyID} does not exist")
                        continue

                    cursor.execute("SELECT * FROM attendee WHERE attendeeCompanyID = %s", (companyID,))
                    attendees = cursor.fetchall()


                    if not attendees:
                        print(f"No attendees found for {company["companyName"]}")
                        continue
                    
                    query = """SELECT a.attendeeName AS Name, a.attendeeDOB AS DOB, s.sessionTitle AS sessionTitle, 
                    s.speakerName AS sessionSpeaker, rm.roomName AS roomName
                    FROM attendee AS a 
                    RIGHT JOIN registration AS r ON a.attendeeID = r.attendeeID 
                    RIGHT JOIN session AS s ON r.sessionID = s.sessionID 
                    RIGHT JOIN room AS rm ON s.roomID = rm.roomID
                    RIGHT JOIN company AS c ON a.attendeeCompanyID = c.companyID
                    WHERE c.companyID = %s"""

                    cursor.execute(query, (companyID,))
                    subjects = cursor.fetchall()
                    print()
                    print("-----------------------------------------------")
                    print(company["companyName"])
                    for s in subjects:
                        print(f"{s['Name']}  |  {s['DOB']}  |  {s['sessionTitle']}  |  {s['sessionSpeaker']}  |  {s['roomName']}")
                    print("-----------------------------------------------")
                    print()
                    break


        if choice == "3":
            print("""
Add New Attendee
----------------""")
            attendeeID = input("Enter attendee ID: ")
            attendee_name = input("Enter attendee's first name and surname: ")
            attendeeDOB = input("Enter the date of birth of attendee (YYYY-MM-DD): ")
            attendee_gender = input("Enter the gender of the attendee: ")
            attendee_company = input("Enter the ID of the attendee's company: ")


            with conn.cursor() as cursor:
                cursor.execute("SELECT attendeeID FROM attendee WHERE attendeeID = %s", (attendeeID,))
                attendee = cursor.fetchone()


                if attendee:
                    print(f"*** ERROR *** Attendee ID: {attendeeID} already exist")
                gender_correct = attendee_gender != "Male" or attendee_gender != "Female"


                if gender_correct:
                    print("*** ERROR *** Gender must be Male/Female")
                cursor.execute("SELECT companyName FROM company WHERE companyID = %s", (attendee_company,))
                company = cursor.fetchone()
                    

                if not company:
                    print(f"*** ERROR *** Company ID: {attendee_company} does not exist")
                

                if not attendee and company and gender_correct:
                    try:
                        query = "INSERT INTO attendee VALUES (%s, %s, %s, %s, %s)"


                        cursor.execute(query, (attendeeID, attendee_name, attendeeDOB, attendee_gender, attendee_company))
                        conn.commit()  
                        print(f"Attendee {attendee_name} successfully added.")

                        cursor.execute("SELECT * FROM attendee WHERE attendeeID = %s", (attendeeID,))
                        new_attendee = cursor.fetchone()


                        print("-----------------------------------------------")
                        print(f"ID: {new_attendee['attendeeID']}  |  Name: {new_attendee['attendeeName']}  |  DOB: {new_attendee['attendeeDOB']}  |  Gender: {new_attendee['attendeeGender']}  |  Company ID: {new_attendee['attendeeCompanyID']}")
                        print("-----------------------------------------------")
                        print()

                    except pymysql.Error as e:
                        print(f"*** Error *** {e}")
                        conn.rollback()


        if choice == "4":
            while True:
                attendeeID = input("Enter attendee ID: ")
                if attendeeID.isdigit():
                    attendeeID = int(attendeeID)
                    break
                else:
                    print("*** ERROR *** Invalid attendee ID")


            with neo4jdriver.session(database="appdbprojneo4j") as session:
                
                connected_attendees = session.execute_read(get_names, attendeeID)


            query = """SELECT attendeeID AS ID, attendeeName AS Name 
                FROM attendee 
                WHERE attendeeID IN %s"""


            with conn.cursor() as cursor:
                cursor.execute("""SELECT attendeeName AS Name 
                FROM attendee 
                WHERE attendeeID = %s""", attendeeID,)
                attendee = cursor.fetchone()


                if not connected_attendees and attendee:
                    print("No connections")

                elif not connected_attendees and not attendee:
                    print("*** ERROR *** Attendee does not exist")

                else:
                    cursor.execute(query, (tuple(connected_attendees),))
                    connected_attendees = cursor.fetchall()
                    print(f"""
-----------------------------------------------
Attendee Name: {attendee["Name"]}
-----------------------------------------------
These attendees are connected:""")
                    for attendee in connected_attendees:
                        print(f"{attendee['ID']}  |  {attendee['Name']}")
                    print("-----------------------------------------------")
                    print()


        if choice == "5":
            count = 0
            while True and not count == 2:
                attendee_one_ID = input("Enter attendee 1 ID: ")
                attendee_two_ID = input("Enter attendee 2 ID: ")

                if attendee_one_ID == attendee_two_ID:
                    print("*** ERROR *** An attendee cannot connect to himself/herself")
                    count += 1
                    continue

                elif not attendee_one_ID.isdigit() or not attendee_two_ID.isdigit():
                    print("*** ERROR *** The IDs of attendees must be numbers")
                    count += 1
                    continue

                else:
                    with neo4jdriver.session(database="appdbprojneo4j") as session:
                        
                        connected_attendees = session.execute_write(connect_attendees, int(attendee_one_ID), int(attendee_two_ID))
                    break
            
            if count == 2:
                print("You entered incorrect attendees IDs two times")


        if choice == "6" and not choice_six_selected:
            choice_six_selected = True
            with conn.cursor() as cursor:
                cursor.execute("""SELECT roomID, roomName, capacity 
                FROM room 
                """,)
                rooms = cursor.fetchall()

                cursor.execute("""SELECT MAX(LENGTH(roomName)) AS max_len
                FROM room 
                """,)
                result = cursor.fetchone()
                room_length = result["max_len"]

                print()
                print("-----------------------------------------------")
                print(f"{'RoomID':<10} | {'RoomName':<{room_length}} | Capacity")
                print("-----------------------------------------------")
                for room in rooms:
                   print(f"{room['roomID']:<10} | {room['roomName']:<{room_length}} | {room['capacity']}")
                print("-----------------------------------------------")
                print()

        else:
            print()
            print("-----------------------------------------------")
            print(f"{'RoomID':<10} | {'RoomName':<{room_length}} | Capacity")
            print("-----------------------------------------------")
            for room in rooms:
                print(f"{room['roomID']:<10} | {room['roomName']:<{room_length}} | {room['capacity']}")
            print("-----------------------------------------------")
            print()


        if choice == "x":
            print("Exiting...")
            break


sql_queries()