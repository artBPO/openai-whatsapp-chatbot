from datetime import datetime
from functools import partial
import json
import logging
import os
import re
import threading

# from openai_agent import OpenAIAgent
import openai

from .chat import Sender, OpenAIChatManager

logger = logging.getLogger("WP-APP")


def verify_phone_number(phone_number: str) -> dict:
    """Make sure that the phone number is allowed to use the chatbot."""
    contacts_json = os.environ.get("CONTACTS_JSON")
    if not contacts_json:
        return True
    allowed_contacts = json.load(open(contacts_json, "r"))
    allowed_phone_numbers = [p["phone_number"] for p in allowed_contacts]
    if phone_number not in [allowed_phone_numbers] + [
        "whatsapp:" + p for p in allowed_phone_numbers
    ]:
        return False
    contact = [
        p
        for p in allowed_contacts
        if p["phone_number"] == phone_number
        or "whatsapp:" + p["phone_number"] == phone_number
    ][0]
    return contact


def ensure_image_generation(reply: str, chat: OpenAIChatManager, sender: Sender, twilio_client: object) -> str:
    """
    Checks if the reply contains an image generation prompt and generate the image in a separate thread if so.
    Returns the reply without the image generation prompt if the image is generated successfully, otherwise returns the reply as is.
    """
    if "[img:" not in reply.lower():
        return reply
    # check if the sender has reached the maximum number of images generated
    if chat.num_images_generated > sender.max_image_generations:
        chat.add_message(
            f"- This user can't generate images anymore due to limits reached. Image not sent - \n",
            role='system'
        )
        logger.warning(
            f"Image not sent: User {sender.name} ({sender.phone_number}) has reached the maximum number of images generated"
        )
        return "Sorry, you have reached the maximum number of images you can generate. Try again later."
    # get the prompt and real reply from the message '{reply}[image generation: "{prompt}"]'
    img_generation_prompt = re.search(
        r"\[img:\"(.*)\"\]", reply, flags=re.IGNORECASE
    ).group(1)
    reply = re.sub(r"\[img:\"(.*)\"\]", "", reply, flags=re.IGNORECASE)
    print(f"Image generation prompt: '{img_generation_prompt}'")
    # send the image in a separate thread
    send_image_with_threading(img_generation_prompt, chat, sender, twilio_client)
    # add to the number of images generated
    chat.num_images_generated += 1
    # check if it surpassed the max number of images
    if chat.num_images_generated > sender.max_image_generations:
        logger.warning(
            f"User {sender.name} ({sender.phone_number}) has reached the maximum number of images generated"
        )
        chat.add_message(
            f"- limit of image generations reached. This user can't do any more generations.  -\n",
            role='system'
        )

    return reply

def ensure_captioning(msg, chat):
    """Check if the message contains a captioning command and set the chat's image captioning option accordingly"""
    if (captioning:=re.search(r'\[captioning:\s*(\w+)\]',msg,re.IGNORECASE)):
        captioning = captioning.group(1)
        if captioning == 'on':
            chat.image_captioning = True
            reply = "Image captioning is now on"
        elif captioning == 'off':
            chat.image_captioning = False
            reply = "Image captioning is now off"
        else:
            reply = "Sorry, I didn't understand that."
        return reply
    return None


def send_image_with_threading(
    prompt: str, chat: OpenAIChatManager, sender: Sender, twilio_client
):
    """Generate an image with the agent and send it in a separate thread given the prompt"""
    from_number = os.environ.get("FROM_WHATSAPP_NUMBER")
    # create a partial function to send the image with the given parameters
    send_current_image = partial(
        send_image,
        prompt,
        chat,
        twilio_client,
        from_phone=from_number,
        to_phone=sender.phone_number,
        caption=prompt if chat.image_captioning else None,
    )
    # start the thread
    threading.Thread(target=send_current_image, daemon=True).start()


def send_image(
    prompt: str,
    chat: OpenAIChatManager,
    twilio_client: object,
    from_phone: str,
    to_phone: str,
    caption: str = None,
):
    """Send a generated image to the given phone number via WhatsApp"""
    print(f"Generating image for prompt: {prompt}")
    img_url = generate_image(prompt)
    print(f"Image generated: {img_url}")
    print(f'"whatsapp:{to_phone}" ' + f'"whatsapp:{from_phone}" ' + img_url)
    message = twilio_client.messages.create(
        from_=f"whatsapp:{from_phone}", 
        to=to_phone, 
        media_url=img_url,
        body=caption)
    print(f"Image sent: {message.sid}")


def save_to_contactbook(reqvals):
    """Saves the phone number and name of the sender to the contact book"""
    contactbook_path = os.environ.get("CONTACTBOOK_PATH", "data/contactbook.json")
    contactbook = json.load(open(contactbook_path, "r"))
    phone_number = reqvals.get("From")
    name = reqvals.get("ProfileName")
    if phone_number:
        contactbook[phone_number] = {
            "name": name,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        json.dump(contactbook, open(contactbook_path, "w"))

def generate_image(prompt: str):
    """
    Generates a new image using the prompt given
    with the image generation API (OpenAI's DALL-E)
    and returns the response.
    """
    # from clients.openai import OpenAIClient

    logging.debug(
        f"Querying OpenAI's Image API 'DALL-E' with prompt '{prompt}'"
    )
    # openai_cl = OpenAIClient()
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    img = response["data"][0]
    img_url = img["url"]
    return img_url