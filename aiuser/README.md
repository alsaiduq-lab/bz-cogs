# How to use 🛠️

The bot will generate responses in whitelisted channels. Bot owners can add a channel to a server's whitelist using:
```
[p]aiuser add <CHANNEL>
```

Bot owners can change the percentage of eligible messages (per server) to reply to:
```
[p]aiuser percent <PERCENT>
```

Users will also have to opt-in (bot-wide) into having their messages used:
```
[p]aiuser optin
```

Admins can modify prompt settings in:
```
[p]aiuser prompt
```

Optionally, enable slash (/chat) command using:
```
[p]slash enablecog aiuser
[p]slash sync
```

Some additional settings are restricted to bot owner only.
See other settings using:
```
[p]aiuser
[p]aiuserowner
```

### Have fun. 🎉
![repetition](https://user-images.githubusercontent.com/46238123/227853613-1a524915-ed46-45f7-a154-94e90daf0cd7.jpg)

---

## Image scanning 🖼️

![image_seeing](https://github.com/zhaobenny/bz-cogs/assets/46238123/8b0019f3-8b38-4578-b511-a350e10fce2d)


Bot owners can see settings here:
```
[p]aiuser imagescan
```

### Supported LLM mode

If the chosen LLM model (eg. gpt-4-vision-preview) supports images, it will directly sent the image as a input using this mode. (superior to other modes in performance but not in cost)

### AI Horde Mode
Utilize [AI Horde's](https://stablehorde.net/) Image Alchemy to caption images.

AI Horde is a crowdsourced distributed cluster. Images will be uploaded to a **unknown third party** (a random volunteer worker machine)

Recommended to set a [API key](https://stablehorde.net/register). (or some [kudos](https://dbzer0.com/blog/the-kudos-based-economy-for-the-koboldai-horde/))


### Local Image Mode

Local image scanning mode will be **very CPU intensive**. *(Not recommended for busy servers/channel)*

First, images will be OCR'ed for text to use. If the OCR is not of significant confidence, it will be captioned instead using [BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base).

<details>
  <summary>Instructions on installing the necessary dependencies (x86 only) </summary>

  #### 1. Install Python Dependencies

  ```
  source ~/redenv/bin/activate # or however you activate your virtual environment in your OS
  pip install -U pytesseract transformers[torch]
  ```

  #### 2. Install Tessaract OCR

  See [here](https://tesseract-ocr.github.io/tessdoc/Installation.html) for instructions on installing TessaractOCR, or alternatively just use the phasecorex/red-discordbot:full image.


  First time scans will require some time to download processing models. (~1gb)

</details>

---
## Image requests 🖼️

Bot owners can see settings here:
```
[p]aiuser imagerequest
```

The bot can generate self-portraits images based on user request.

Requests are classified by trigger words / LLM decision. (eg. *"hey @botname, can you show me a picture of a yourself?"*)

A suitable Stable Diffusion endpoint (Automatic1111 in API mode) must be provided and a non-trial OpenAI account is recommended.

For a cost-efficient hosted solution, you can use [modal.com](https://modal.com/) to get a SD endpoint running. I written a modal template, [serverless-img-gen](https://github.com/zhaobenny/serverless-img-gen), that is compatible with this cog.

When using serverless-img-gen, you might need to set an auth token:
```
[p]set api modal-img-gen token,AUTH_TOKEN
```

---

## Random Messages 🎲

Have the bot sent random messages into a channel without external triggers.

Every 33 minutes, a RNG roll will determine if a random message will be sent using a list of topics as a prompt.

Whitelisted channels must have a hour pass without a message sent in it for a random message to be sent, and the last sent message must be sent by a user.

Bot owners enable this setting per server here:
```
[p]aiuser randommessage toggle
```

Admins also manage topics here:
```
[p]aiuser randommessage
```
---

## Prompt/Topics Variables  📝

Prompts and topics can include certain variables by including one of the following placeholders:

- `{botname}` - the bot's current nickname or username
- `{authorname}` - the author of the message the bot is activated on
- `{authortoprole}` - the author's highest role
- `{serveremojis}` - all of the server emojis, in a string format (eg. `<:emoji:12345> <:emoji2:78912>`)
- `{servername}` - the server name
- `{channelname}` - the channel name
- `{currentdate}` - the current date eg. 2023/08/31
- `{currentweekday}` - the current weekday eg. Monday
- `{currenttime}` - the current 24-hour time eg. 21:59


Remove list regex patterns only support `{authorname}` (will use authors of last 10 messages) and `{botname}` placeholders.

---

### OpenRouter

[OpenRouter](https://openrouter.ai) is compatible as a custom OpenAI endpoint.

OpenRouter has unfiltered open source models, Claude, and PaLM available for a cost.
See full details [here](https://openrouter.ai/docs#models).

Bot owners can set this globally using the following:
```
[p]aiuserowner endpoint https://openrouter.ai/api/v1
```

Get an API key from OpenRouter and set it here:
```
[p]set api openrouter api_key,INSERT_API_KEY
```

Models will also need **changing** per server.

Some third party models may have undesirable results.

---

### Custom OpenAI endpoint

⚠️ For advanced users! ⚠️

Other OpenAI-Compatible API endpoints can be used instead of the default OpenAI API. (eg. gpt4all or text-generation-webui)

Compatibility may vary and is not guaranteed.

Bot owners can set this globally using:
```
[p]aiuserowner endpoint <ENDPOINT>
```

Like OpenRouter, similar disclaimers apply:

Models will also need **changing** per server.

Some third party models may have undesirable results.

Bot owners may also want to set custom parameters (per server). See:
```
[p]aiuser response parameters
```

