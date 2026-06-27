import json
import logging
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .agent import chat, chat_stream

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """非流式对话（保留兼容）"""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response({"error": "消息不能为空"}, status=400)

        thread_id = request.data.get(
            "thread_id",
            str(request.user.id) if request.user.is_authenticated else "anonymous",
        )

        try:
            reply = chat(user_message, thread_id=thread_id)
            return Response({"reply": reply, "thread_id": thread_id})
        except Exception as e:
            logger.exception(f"AI 助手出错: {e}")
            return Response({"error": str(e)}, status=500)


class ChatStreamView(APIView):
    """流式对话 — SSE (Server-Sent Events)"""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response({"error": "消息不能为空"}, status=400)

        thread_id = request.data.get(
            "thread_id",
            str(request.user.id) if request.user.is_authenticated else "anonymous",
        )

        def generate():
            try:
                for token in chat_stream(user_message, thread_id=thread_id):
                    payload = json.dumps({"token": token}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.exception(f"流式输出异常: {e}")
                payload = json.dumps(
                    {"token": f"抱歉，AI 助手暂时无法响应: {e}"},
                    ensure_ascii=False,
                )
                yield f"data: {payload}\n\n"

        response = StreamingHttpResponse(
            generate(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
