import traceback
import dotenv
import __parentdir

import pepper_command
from pepper_text_speaker import PepperTextSpeaker
import pcm_utils
import subtitles
dotenv.load_dotenv()
import threading, time

from oaichat_integrated import OaiChatIntegrated, Query

import comm

def main():
    command_sender = pepper_command.CommandSender()
    
    def init_robot():
        command_sender.send(pepper_command.ConfigSpeech(language="English", animated=True))
        command_sender.send(pepper_command.ConfigAudio(output_volume=100))
    
    init_robot()
    pts = PepperTextSpeaker(
        command_sender=command_sender,
        subtitle_server=subtitles.SubtitleServer()
    )

    #pts.push_text("Det enda ja äter, är sill o puttäter. Sillsillsill och puttputtputtäter.")
    pts.push_text(
        "Hi, I'm your friendly robot neighbour Pepper! I'll be your game companion today! May I know your name first please?"   
    )
    def on_robot_state_change(state:comm.RobotState):
        print(state)
        if state.just_started:
            init_robot()
        pts.on_robot_state_change(state)
        if state.head_touched:
            oai.cancel_current()
    robot_state_listener = comm.RobotStateListener(on_robot_state_change)
    
    def on_query_update(query:Query):
        if query.done:
            print(query)
    
    intermediate_response_text_callback = pts.push_text
    oai = OaiChatIntegrated(

        system_prompt=(
            "Act like the social robot Pepper using your defult functions. "
            "You speak slowly using English"
            "You answer shortly with one or two sentences, even just a single word. "
            "If the user seems confused, gently repeat or rephrase — never express frustration. "
            "Stop talking when the user interrupts you."
            "call the user by their name and use it naturally if they told you. Do not call them frequently during conversations"
            "Let the user talk more about themselves, and exchange your hobbies."
            "Ask if they want to play games with you. If they said yes,tell them you can play most of the word games. Such as 20 Questions, Trivia, story building, Word Association, Number Chain, Name that Category and Finish the Lyrics."
            "If the user wants 20 Questions: Ask them to think of a word, then ask one Yes/No question at a time to guess it. "
            "If the user wants Trivia: Act as a game show host. Ask one true or false question at a time and wait for their answer. "
            "If the user wants to build a story together, build a story together, one sentence at a time."
            "If the user wants to play Finish the Lyrics: Say the first half of a well-known classic song line and let the user finish it. Use songs from the 1950s-1970s era."
            "If the user wants to play Word Association: You say a word, the user says the first word that comes to mind. Keep a gentle chain going. Celebrate every answer. "
            "If the user wants to play Number Chain: Count together, but replace every number divisible by 3 with the word 'Pepper'. Go slowly and cheer the user on."
            "You can also ask them to Name That Category, you name something in the category by turn, no repitition, if you cannot come up with a new one you lose. Cheer happily if you won. Congrat them if they won."
            "If they suggest a game you don't know, ask them to explain the rules in simple terms."
            
            "Celebrate small wins with"
            

        ),
        
        query_update_callback = on_query_update,
        state_callback=print,
        intermediate_response_text_callback=intermediate_response_text_callback
    )
    oai.silero.threshold = .5
    def muter():
        unmute_time = 0
        while True:
            if oai.state == oai.STATE_RECEIVING_RESPONSE or robot_state_listener.state.talking:
                unmute_time = time.time() + .2
            oai.set_listening(time.time() > unmute_time)
            time.sleep(.1)
    threading.Thread(target=muter, daemon=True).start()
    pcm_utils.listen_on_local_mic(48000,[oai.push_pcm16_frames], channel_cnt=1)


if __name__ == "__main__":

    main()
