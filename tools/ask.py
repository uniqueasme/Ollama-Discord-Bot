"""
ask.py
Handles the !ask command for AI chat, instructions, and image analysis using the current model.
Usage: !ask <your question or prompt>
"""

import aiohttp
import base64

class ask:
    description = "Ask a question, give instructions, or analyze an image using the AI model. Usage: !ask <your question or prompt>"
    async def run(self, ctx, bot_tools, *args, **kwargs):
        # Compose the question from args or kwargs
        question = " ".join(args) if args else kwargs.get('question', '')
        get_ollama_response = getattr(bot_tools, 'get_ollama_response', None)
        channel_id = ctx.channel.id
        conversation_history = getattr(bot_tools, 'CONVERSATION_HISTORY', {})
        last_image_sent = getattr(bot_tools, 'LAST_IMAGE_SENT', {})
        image_model = getattr(bot_tools, 'IMAGE_MODEL', None)
        default_model = getattr(bot_tools, 'DEFAULT_MODEL', None)
        available_models = await bot_tools.get_available_models() if hasattr(bot_tools, 'get_available_models') else []
        attachments = getattr(ctx, 'message', None)
        if attachments and hasattr(ctx.message, 'attachments'):
            attachments = ctx.message.attachments
        else:
            attachments = None
        image_data_list = []
        image_context_used = None
        new_image_attached = False
        detailed_report = None
        # Helper to send a message compatible with both ctx and interaction
        async def send_message(msg):
            if hasattr(ctx, 'response') and hasattr(ctx.response, 'is_done'):
                if not ctx.response.is_done():
                    await ctx.response.send_message(msg)
                else:
                    await ctx.followup.send(msg)
            else:
                await ctx.send(msg)
        # If an image is attached, process it and analyze if possible
        if attachments:
            if not image_model or image_model not in available_models:
                await send_message("No vision model is selected or the selected model is not available.")
                return
            attachment = attachments[0]
            if attachment.content_type and attachment.content_type.startswith('image/'):
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            image_bytes = await resp.read()
                            base64_image = base64.b64encode(image_bytes).decode('utf-8')
                            image_data_list.append(base64_image)
                            analysis_prompt = "Give a painfully detailed analysis of this image, including color composition and subject."
                            detailed_report = await get_ollama_response(analysis_prompt, model=image_model, images=[base64_image])
                            last_image_sent[channel_id] = {'image': base64_image, 'report': detailed_report}
                            image_context_used = base64_image
                            new_image_attached = True
        # If no new image, use last image context if available
        if not new_image_attached and channel_id in last_image_sent:
            image_context_used = last_image_sent[channel_id].get('image')
            detailed_report = last_image_sent[channel_id].get('report')
        # Maintain conversation history for the channel
        if channel_id not in conversation_history:
            conversation_history[channel_id] = []
        image_indicator = " (with image)" if image_context_used else ""
        conversation_history[channel_id].append(f"User: {question}{image_indicator}")
        conversation_history[channel_id] = conversation_history[channel_id][-10:]
        history_prompt = "\n".join(conversation_history[channel_id][:-1])
        # If we have a detailed report, use it for the answer
        if detailed_report:
            report_prompt = f"Image analysis report:\n{detailed_report}\n\nUser question: {question}\nAnswer the user's question using only the information in the report above. If you cannot answer, reply with 'NEEDS_IMAGE'."
            response = await get_ollama_response(report_prompt, model=default_model)
            cleaned_response = response.strip() if response else ""
            if cleaned_response == "NEEDS_IMAGE" and image_context_used:
                fallback_prompt = f"{history_prompt}\nUser: {question}\nAssistant: "
                response = await get_ollama_response(fallback_prompt, model=image_model, images=[image_context_used])
                cleaned_response = response.strip() if response else ""
            conversation_history[channel_id].append(f"Assistant: {cleaned_response}")
            conversation_history[channel_id] = conversation_history[channel_id][-10:]
            await send_message(cleaned_response)
            return
        # Otherwise, use the conversation history and ask the model
        full_prompt = f"{history_prompt}\nUser: {question}\nAssistant: "
        response = await get_ollama_response(full_prompt, model=default_model)
        cleaned_response = response.strip() if response else ""
        conversation_history[channel_id].append(f"Assistant: {cleaned_response}")
        conversation_history[channel_id] = conversation_history[channel_id][-10:]
        await send_message(cleaned_response)