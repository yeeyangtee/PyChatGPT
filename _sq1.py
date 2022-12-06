# Builtins
import json
import os
import time

# Local
from Classes import auth as Auth
from Classes import chat as Chat

# Fancy stuff
import colorama
from colorama import Fore

colorama.init(autoreset=True)

# Check if config.json exists
if not os.path.exists("_config.json"):
    print(">> config.json is missing. Please create it.")
    print(f"{Fore.RED}>> Exiting...")
    exit(1)

# Read config.json
with open("_config.json", "r") as f:
    config = json.load(f)
    # Check if email & password are in config.json
    if "email" not in config or "password" not in config:
        print(">> config.json is missing email or password. Please add them.")
        print(f"{Fore.RED}>> Exiting...")
        exit(1)

    # Get email & password
    email = config["email"]
    password = config["password"]

# Open blog title list
with open("data/sq1_blog_list.txt", "r") as f:
    blog_titles = f.read().splitlines()

if __name__ == "__main__":
    expired_creds = Auth.expired_creds()
    print(f"{Fore.GREEN}>> Checking if credentials are expired...")
    if expired_creds:
        print(f"{Fore.RED}>> Your credentials are expired." + f" {Fore.GREEN}Attempting to refresh them...")
        open_ai_auth = Auth.OpenAIAuth(email_address=email, password=password)

        print(f"{Fore.GREEN}>> Credentials have been refreshed.")
        open_ai_auth.begin()
        time.sleep(3)
        is_still_expired = Auth.expired_creds()
        if is_still_expired:
            print(f"{Fore.RED}>> Failed to refresh credentials. Please try again.")
            exit(1)
        else:
            print(f"{Fore.GREEN}>> Successfully refreshed credentials.")
    else:
        print(f"{Fore.GREEN}>> Your credentials are valid.")

    print(f"{Fore.GREEN}>> Starting chat..." + Fore.RESET)
    previous_convo_id = None
    conversation_id = None
    access_token = Auth.get_access_token()
    for i, title in enumerate(blog_titles):
        time.sleep(10)
        try:
            if access_token == "":
                print(f"{Fore.RED}>> Access token is missing in /Classes/auth.json.")
                exit(1)

            # user_input = input("You: ")
            user_input = (
                f"Can you write a 1000 word article that is well structured with headings and sections. Each section should have 2 or more paragraphs if possible."
                f"Please use section headings in markdown style with no numbers. Please include a conclusion section."
                f"Please only include the article text and no explanations. It should have the title: {title}"
            )
            print('You:', user_input)
            answer, previous_convo, conversation = Chat.ask(auth_token=access_token,
                                              prompt=user_input,
                                              conversation_id=conversation_id,
                                              previous_convo_id=previous_convo_id)
            blog_post = answer       

            if answer == "400" or answer == "401":
                print(f"{Fore.RED}>> Your token is invalid. Attempting to refresh..")
                open_ai_auth = Auth.OpenAIAuth(email_address=email, password=password)
                open_ai_auth.begin()
                time.sleep(3)
                access_token = Auth.get_access_token()
            else:
                # print(blog_post)
                if previous_convo is not None:
                    previous_convo_id = previous_convo
                if conversation is not None:
                    conversation_id = conversation
                while 'conclusion' not in blog_post and 'Conclusion' not in blog_post:
                    user_input = 'Please continue'
                    time.sleep(10)
                    print('You:', user_input)
                    answer, previous_convo, conversation = Chat.ask(auth_token=access_token,
                                              prompt=user_input,
                                              conversation_id=conversation_id,
                                              previous_convo_id=previous_convo_id)
                    previous_convo_id = previous_convo
                    blog_post += answer
                print(blog_post)
                # # Write blog post to file under '/output' with file name as the blog title
                with open("output/" + title.strip('"') + ".txt", "w") as f:
                    f.write(blog_post)
                print(f"Blog post written to file: {title}.txt")
                # print(f"Chat GPT: {answer}")
                # if i > 5:
                #     break
        except KeyboardInterrupt:
            print(f"{Fore.RED}>> Exiting...")
            exit(1)







