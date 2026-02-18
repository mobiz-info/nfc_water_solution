import firebase_admin

from firebase_admin import messaging
from accounts.models import *
from firebase_admin import messaging, credentials





def notification(user_id,title,body,project_name):
   
    app = firebase_admin.get_app(name=project_name)
    token = Send_Notification.objects.filter(user=user_id).values('device_token').get()['device_token']
  
    # Notification message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token = token
    )
 
    # Send the message
    response = messaging.send(message,app=app)
    # print("jjjj",response)
    Notification.objects.create(user=CustomUser.objects.get(id=user_id),device_token=token,title=title,body=body)

    # def notification_customer(user_ids,title,body,project_name):
    
#     app = firebase_admin.get_app(name=project_name)
 
#     # token_value = Send_Notification.objects.filter(user=user_ids).last()
#     # token = token_value.device_token
#     token = Send_Notification.objects.filter(user=user_ids).values('device_token').get()['device_token']

  
 
#     # Notification message
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body
#         ),
#         token = token
#     )

#     # Send the message
#     response = messaging.send(message,app=app)
    
#     Notification.objects.create(user=CustomUser.objects.get(id=user_ids),device_token=token,title=title,body=body)

def notification_customer(user_ids, title, body, project_name):
    try:
        app = firebase_admin.get_app(name=project_name)
    except ValueError:
        # If the app is not already initialized, initialize it
        cred = credentials.Certificate("nationalwater-customer-app-firebase-adminsdk-zcimc-f19c21ec83.json")
        app = firebase_admin.initialize_app(cred, name=project_name)

    try:
        # Get the latest device token for the user
        token_value = Send_Notification.objects.filter(user=user_ids).last()
        if not token_value:
            raise Send_Notification.DoesNotExist(f"No device token found for user ID {user_ids}")

        token = token_value.device_token

        # Notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )

        # Send the message
        response = messaging.send(message, app=app)

        # Save the notification
        Notification.objects.create(user=CustomUser.objects.get(id=user_ids), device_token=token, title=title, body=body)
    except Send_Notification.DoesNotExist as e:
        print(e)
    except CustomUser.DoesNotExist:
        print(f"CustomUser matching query does not exist for user ID {user_ids}")
    except Exception as e:
        print(f"An error occurred in notification_customer: {e}")


def notification_supervisor(user_idds,title,body,project_name):
    
    app = firebase_admin.get_app(name=project_name)
 
    token_value = Send_Notification.objects.filter(user=user_idds).last()
    token = token_value.device_token
  
 
    # Notification message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token = token
    )

    # Send the message
    response = messaging.send(message,app=app)
    
    Notification.objects.create(user=CustomUser.objects.get(id=user_idds),device_token=token,title=title,body=body)