# apps/documents/api/views.py
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from apps.documents.services.document_service import DocumentService
from apps.documents.forms import UploadMultipleForm

class DocumentUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = UploadMultipleForm(request.data, request.FILES, user=request.user)

        if not form.is_valid():
            return Response({
                "success": False,
                "errors": form.errors
            }, status=400)

        # ✅ Nom cohérent avec le champ HTML 'fichiers'
        files = request.FILES.getlist('fichiers')

        if not files:
            return Response({
                "success": False,
                "errors": {"fichiers": ["Aucun fichier reçu."]}
            }, status=400)

        actions_json = request.data.getlist("actions[]")
        actions = {}
        for a in actions_json:
            try:
                parsed = json.loads(a)
                actions[parsed['name']] = parsed
            except (json.JSONDecodeError, KeyError):
                continue

        result = DocumentService.process_upload(
            user=request.user,
            files=files,
            actions=actions,
            data=form.cleaned_data
        )

        return Response({
            "success": True,
            "documents": len(result["documents"]),
            "versions": len(result["versions"]),
            "skipped": len(result["skipped"]),
            "message": (
                f"{len(result['documents'])} document(s) enregistré(s), "
                f"{len(result['versions'])} version(s) créée(s)."
            )
        }, status=201)
