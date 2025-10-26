# main.py
import os
import asyncio
import inspect
import logging
from dotenv import load_dotenv

# --- LOGGING STUFF ---
# okay so this just makes the logs look all fancy in the terminal :3
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("monika-assistant")

# load da .env file (super secret stuff lives here)
load_dotenv()

# print if our envs are alive or dead (TRUE/FALSE vibes)
logger.info("LIVEKIT_URL present: %s", bool(os.getenv("LIVEKIT_URL")))
logger.info("OPENAI_API_KEY present: %s", bool(os.getenv("OPENAI_API_KEY")))

# --- IMPORTING STUFF (pls don’t break) ---
try:
    from livekit.agents import JobContext, WorkerOptions, cli
    from livekit.plugins import openai, silero
    from livekit.agents import llm as _llm_module
except Exception as e:
    logger.exception("uh oh, livekit packages exploded: %s", e)
    raise

# now importing my own api.py (like my secret sauce file)
try:
    import api as user_api
except Exception as e:
    logger.exception("my api.py just went kaboom: %s", e)
    raise

# --- helper fn that knows if smth is async or not ---
def _maybe_await(fn, *args, **kwargs):
    """call the fn, and if it’s async then await, else just run it raw"""
    res = fn(*args, **kwargs)
    if inspect.isawaitable(res):
        return asyncio.ensure_future(res)
    return res

# --- main magic function ---
async def entrypoint(ctx: JobContext):
    """
    this is the big boy function that livekit calls first!!
    it tries like 3 different ways to boot up the anime AI helper lol
    """
    try:
        # making like a "memory" for chat system
        chat_ctx = None
        try:
            # checking if LLM got ChatContext or not
            if hasattr(_llm_module, "ChatContext"):
                chat_ctx = _llm_module.ChatContext().append(
                    role="system",
                    text=("You are an anime-style voice assistant. Keep replies short, friendly, and natural.")
                )
        except Exception:
            chat_ctx = None

        # now we make like the little AI organs (voice, listen, brain, speak)
        vad = None
        try:
            vad = silero.VAD.load()  # detects when ppl talk 👂
        except Exception:
            logger.warning("VAD didn’t wanna load, whatever")

        stt = None  # speech to text
        tts = None  # text to speech
        llm_client = None  # big brain model
        try:
            stt = openai.STT()
            tts = openai.TTS()
            llm_client = openai.LLM()
        except Exception as e:
            logger.warning("OpenAI plugins said nope: %s", e)

        # --- connecting the user's api.py tools ---
        fnc_ctx = getattr(user_api, "AssistantFnc", None)
        tools = getattr(user_api, "tools", None)
        fnc_ctx_obj = None
        if fnc_ctx:
            try:
                fnc_ctx_obj = fnc_ctx()
                logger.info("yay using AssistantFnc from api.py 😎")
            except Exception as e:
                logger.warning("AssistantFnc said nah: %s", e)
                fnc_ctx_obj = None

        # --- Pattern 1: trying the VoiceAssistant thingy first ---
        try:
            from livekit.agents.voice_assistant import VoiceAssistant  # type: ignore
            logger.info("found VoiceAssistant, let’s roll!!")

            # make a big bundle of kwargs for da constructor
            kw = {}
            if vad is not None:
                kw["vad"] = vad
            if stt is not None:
                kw["stt"] = stt
            if llm_client is not None:
                kw["llm"] = llm_client
            if tts is not None:
                kw["tts"] = tts
            if chat_ctx is not None:
                kw["chat_ctx"] = chat_ctx
            if fnc_ctx_obj is not None:
                kw["fnc_ctx"] = fnc_ctx_obj
            if tools is not None:
                try:
                    sig = inspect.signature(VoiceAssistant.__init__)
                    if "tools" in sig.parameters:
                        kw["tools"] = tools
                except Exception:
                    pass

            assistant = VoiceAssistant(**kw)

            # starting the assistant (pls work)
            start = getattr(assistant, "start", None)
            if start is None:
                logger.error("umm... no start()?? bruh")
                raise RuntimeError("VoiceAssistant missing start()")

            logger.info("calling assistant.start(...), cross ur fingers")
            res = start(ctx.room) if start.__code__.co_argcount > 1 else start()
            if inspect.isawaitable(res):
                await res

            # greet like a nice anime bot uwu
            say = getattr(assistant, "say", None)
            if say:
                r = say("Hey! I'm ready to help you.", allow_interruptions=True)
                if inspect.isawaitable(r):
                    await r

            # now let the assistant do its infinite loop magic
            run_fn = getattr(assistant, "run", None)
            if run_fn:
                if inspect.iscoroutinefunction(run_fn):
                    await run_fn()
                else:
                    run_fn()
            else:
                # fallback sleepy loop if it’s a lazy assistant
                while True:
                    await asyncio.sleep(60)
            return

        except Exception as e1:
            logger.info("VoiceAssistant didn’t vibe: %s", e1)

        # --- Pattern 2: the AutoAgent backup plan 😤 ---
        try:
            AutoAgent = None
            try:
                from livekit.agents.auto_agent import AutoAgent  # type: ignore
                AutoAgent = AutoAgent
                logger.info("found AutoAgent!!!")
            except Exception:
                AutoAgent = None

            if AutoAgent is not None:
                logger.info("using AutoAgent path like a pro")
                kwargs = dict(job=ctx)
                if llm_client is not None:
                    kwargs["llm"] = llm_client
                if vad is not None:
                    kwargs["vad"] = vad
                if stt is not None:
                    kwargs["stt"] = stt
                if tts is not None:
                    kwargs["tts"] = tts
                if chat_ctx is not None:
                    kwargs["chat_ctx"] = chat_ctx
                if fnc_ctx_obj is not None:
                    kwargs["fnc_ctx"] = fnc_ctx_obj

                session = AutoAgent(**kwargs)
                if hasattr(session, "say"):
                    maybe = session.say("Hey! I'm ready to help you.", allow_interruptions=True)
                    if inspect.isawaitable(maybe):
                        await maybe
                if hasattr(session, "run"):
                    runfn = session.run
                    if inspect.iscoroutinefunction(runfn):
                        await runfn()
                    else:
                        runfn()
                return
        except Exception as e2:
            logger.info("AutoAgent was too shy: %s", e2)

        # --- Pattern 3: THE FINAL BOSS (AgentSession) 💀 ---
        try:
            from livekit.agents import AgentSession  # type: ignore
            logger.info("ok fine, using AgentSession last try")
            kwargs = {}
            if vad is not None:
                kwargs["vad"] = vad
            if stt is not None:
                kwargs["stt"] = stt
            if llm_client is not None:
                kwargs["llm"] = llm_client
            if tts is not None:
                kwargs["tts"] = tts
            if chat_ctx is not None:
                kwargs["chat_ctx"] = chat_ctx
            if fnc_ctx_obj is not None:
                kwargs["fnc_ctx"] = fnc_ctx_obj
            session = AgentSession(**kwargs)

            # build a smol Agent if needed
            Agent = None
            try:
                from livekit.agents import Agent  # type: ignore
                Agent = Agent
            except Exception:
                Agent = None

            class _SimpleAgent(Agent if Agent is not None else object):
                def __init__(self):
                    if Agent is not None:
                        super().__init__(instructions="You are a friendly assistant :)")

            if Agent is not None and hasattr(session, "start"):
                maybe = session.start(agent=_SimpleAgent(), room=ctx.room)
                if inspect.isawaitable(maybe):
                    await maybe

            if hasattr(session, "generate_reply"):
                gen = session.generate_reply(instructions="Hey! I'm ready to help you.")
                if inspect.isawaitable(gen):
                    await gen

            if hasattr(session, "run"):
                runfn = session.run
                if inspect.iscoroutinefunction(runfn):
                    await runfn()
                else:
                    runfn()

            return

        except Exception as e3:
            logger.info("AgentSession also gave up: %s", e3)

        # if literally everything broke
        raise RuntimeError("bro... no assistant version worked 😭")

    except Exception as e:
        logger.exception("main entrypoint just died: %s", e)
        raise

# --- RUNNING THE WORKER ---
if __name__ == "__main__":
    # this launches the LiveKit worker thingy (like hitting the 'GO' button 🚀)
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
