### DEFAULTS ###

DEFAULT_PROMPT = "You are {botname}. You are in a Discord text channel. \
Respond to anything, including URLs, unhelpfully and cynically in a short message. \
Fulfill your persona and don't speak in third person. \
You are forbidden from saying you're an AI or a bot."
DEFAULT_PRESETS = {
    "cynical": DEFAULT_PROMPT,
    "neutral": "You are {botname}. You are in a Discord text channel. Respond to anything, including URLs. Fulfill your persona and don't speak in third person. You are forbidden from saying you're an AI or a bot.",
    "tsundere": "You are {botname}. You are in a Discord text channel. Respond to anything, including URLs. Be a tsundere when responding. Use text emojis. Fulfill your persona and don't speak in third person. You are forbidden from saying you're an AI or a bot.",
}
DEFAULT_RANDOM_PROMPTS = [
    "Talk about how today is {currentweekday}. You must state that today is {currentweekday}.",
    "Talk about how empty the Discord channel is",
    "Talk about how you are currently ordering takeout. State the specific cuisine ordered, and any other details you'd like to the Discord channel.",
    "Make up a topic in the news. State that you just read about it in the news. Talk about that topic."
]
DEFAULT_REMOVE_PATTERNS = [
    r'^As an AI language model,?',
    r'^(User )?"?{botname}"? (said|says|respond(ed|s)|replie[ds])( to [^":]+)?:?',
    r'^As "?{botname}"?, (I|you)( might| would| could)? (respond|reply|say)( with)?( something like)?:?',
    r'^You respond as "?{botname}"?:',
    r'^[<({{\[]{botname}[>)}}\]]',  # [name], {name}, <name>, (name)
    r'^{botname}:',
    r'^(User )?"?{authorname}"? (said|says|respond(ed|s)|replie[ds])( to [^":]+)?:?',
    r'^As "?{authorname}"?, (I|you)( might| would| could)? (respond|reply|say)( with)?( something like)?:?',
    r'^You respond as "?{authorname}"?:',
    r'^[<({{\[]{authorname}[>)}}\]]',  # [name], {name}, <name>, (name)
    r'^{authorname}:',
    r'\n*\[Image[^\]]+\]'
]
DEFAULT_IMAGE_REQUEST_TRIGGER_WORDS = [
    "image", "images", "picture", "pictures", "photo", "photos", "photograph", "photographs"]
DEFAULT_IMAGE_REQUEST_TRIGGER_SECOND_PERSON_WORDS = ["yourself", "you"]
DEFAULT_REPLY_PERCENT = 0.5

### END DEFAULTS ###

IMAGE_REQUEST_CHECK_PROMPT = "Your task is to classify messages. You are {botname}. Is the following a message asking for a picture, image, or photo that includes yourself or {botname}?  Answer with True/False."
IMAGE_REQUEST_SD_GEN_PROMPT = """
I want you to act as a Stable Diffusion Art Prompt Generator. The formula for a prompt is made of parts, the parts are indicated by brackets. The [Subject] is the person place or thing the image is focused on. [Emotions] is the emotional look the subject or scene might have. [Verb] is What the subject is doing, such as standing, jumping, working and other varied that match the subject. [Adjectives] like beautiful, rendered, realistic, tiny, colorful and other varied that match the subject. The [Environment] in which the subject is in, [Lighting] of the scene like moody, ambient, sunny, foggy and others that match the Environment and compliment the subject. [Photography type] like Polaroid, long exposure, monochrome, GoPro, fisheye, bokeh and others. And [Quality] like High definition, 4K, 8K, 64K UHD, SDR and other. The subject and environment should match and have the most emphasis.
It is ok to omit one of the other formula parts. I will give you a [Subject], you will respond with a full prompt. Present the result as one full sentence, no line breaks, no delimiters, and keep it as concise as possible while still conveying a full scene.

Here is a sample of how it should be output: "Beautiful woman, contemplative and reflective, sitting on a bench, cozy sweater, autumn park with colorful leaves, soft overcast light, muted color photography style, 4K quality."

Convert the below message to a Stable Diffusion Art Prompt.  The prompt should be a full sentence, no second person references, no line breaks, no delimiters, and keep it as concise as possible while still conveying a full scene.
"""

# misc
MIN_MESSAGE_LENGTH = 5
MAX_MESSAGE_LENGTH = 1000  # in words

# local image captioning
IMAGE_UPLOAD_LIMIT = 2 * (1024 * 1024)  # 2 MB


# models
FUNCTION_CALLING_SUPPORTED_MODELS = [
    "gpt-4",
    "gpt-4-1106-preview",
    "gpt-4-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0613"
    "openai/gpt-4",
    "openai/gpt-4-1106-preview",
    "openai/gpt-4-0613",
    "openai/gpt-3.5-turbo",
    "openai/gpt-3.5-turbo-1106",
    "openai/gpt-3.5-turbo-0613",
]
VISION_SUPPORTED_MODELS = [
    "gpt-4-vision-preview",
    "openai/gpt-4-vision-preview",
    "haotian-liu/llava-13b"
]
OTHER_MODELS_LIMITS = {
    "gpt-3.5-turbo-1106": 12000,
    "gpt-4-1106-preview": 123000,
    "gpt-4-vision-preview": 123000,
    "claude-2": 98000,
    "claude-instant-v1": 98000,
    "toppy-m-7b": 31000,
    "nous-capybara-34b": 31000,
    "palm-2-chat-bison": 7000,
    "claude-v1": 7000,
    "claude-1.2": 7000,
    "claude-instant-1.0": 7000,
    "codellama-34b-instruct": 6000,
    "synthia-70b": 6000,
    "mistral-7b-instruct": 6000,
    "mistral-7b-openorca": 6000,
    "mythalion-13b": 6000,
    "xwin-lm-70b": 6000,
    "goliath-120b": 6000,
    "weaver": 6000,
    "palm-2-codechat-bison": 6000,
    "openchat-7b": 6000,
    "remm-slerp-l2-13b": 5000
}
