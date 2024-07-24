import threading
import time
from openai import OpenAI
from client import ChatClient
openai_key = ""
lines_prompt = (
    "You are a part of a chat. You don't know which user wrote which message, or how many users are in the chat."
    "you would need to deduce those."
    "Make absurd assumptions on the conversation and respond casually"
    "Keep your replies one sentence short."
    )
random_prompt = (
    "You are a part of an online chat."
    "You task is to come up with a short remark that someone crazy with no grip on reality would say"
    "Keep your replies one sentence short."
    )


class AIClient(ChatClient):
    def __init__(self, host, port, lines_interval=None, seconds_interval=None):
        super().__init__(host, port)
        self.lines_interval = lines_interval
        self.seconds_interval = seconds_interval
        self.conversation = []
        self.client = OpenAI(api_key=openai_key)
        self.timer = time.time()
        self.connect(host, port)

        if not self.lines_interval and not self.seconds_interval:
            raise ValueError("AI client requires either lines_interval or seconds_interval")

        if self.lines_interval:
            self.respond_thread = threading.Thread(target=self.bot_respond_to_conversation)
        else:
            self.respond_thread = threading.Thread(target=self.bot_respond_randomly)

        self.recv_thread = threading.Thread(target=self.receive_messages)
        self.recv_thread.start()

        self.respond_thread.daemon = False
        self.respond_thread.start()

    def bot_respond_to_conversation(self):
        while True:
            if len(self.conversation) >= self.lines_interval:
                resp = self.make_a_replay(self.conversation)
                self.send_single_message(resp)
                self.conversation = []
            time.sleep(0.1)

    def bot_respond_randomly(self):
        while True:
            if time.time() - self.timer > self.seconds_interval:
                self.timer = time.time()
                self.send_single_message(self.make_a_random_remark())
            time.sleep(0.1)

    def send_messages(self):
        pass

    def extract_message(self, openai_response):
        if not (resp := openai_response.model_dump().get("choices", [{}])[0].get("message", {}).get("content")):
            raise ValueError("Unexpected response from OpenAI")
        return resp

    def make_a_random_remark(self):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": random_prompt}]
        )
        return self.extract_message(completion)

    def make_a_replay(self, raw_conversation):
        conv = [{"role": "user", "content": line} for line in raw_conversation]
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": lines_prompt}] + conv
        )
        return self.extract_message(completion)

    def receive_messages(self):
        while True:
            # Receive message from server
            header = self.socket.recv(4)
            if not header:
                break
            msg_len = int.from_bytes(header, byteorder="big")
            msg = self.socket.recv(msg_len).decode("utf-8")
            print(f"\nReceived message: {msg}\n")
            self.conversation.append(msg)


ai_client = AIClient("localhost", 12345, lines_interval=5)

