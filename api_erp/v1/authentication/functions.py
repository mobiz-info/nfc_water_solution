import requests

def generate_serializer_errors(args):
    message = ""
    # print (args)
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_user_token(request,user_name,password):
    headers = {
        'Content-Type': 'application/json',
    }
    data = '{"username": "' + user_name + '", "password":"' + password + '"}'
    protocol = "http://"
    if request.is_secure():
        protocol = "https://"

    web_host = request.get_host()
    request_url = protocol + web_host + "/api/auth/token/"

    response = requests.post(request_url, headers=headers, data=data)
    # print(response)
    return(response)



