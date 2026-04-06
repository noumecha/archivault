import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from apps.documents.services.document_service import DocumentService
from apps.documents.forms import UploadMultipleForm

class DocumentUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        form = UploadMultipleForm(request.data, request.FILES, user=request.user)

        if not form.is_valid():
            return Response({
                "success": False,
                "errors": form.errors
            }, status=400)

        files = request.FILES.getlist('files[]')
        actions_json = request.data.getlist("actions[]")

        actions = {
            json.loads(a)['name']: json.loads(a)
            for a in actions_json
        }

        result = DocumentService.process_upload(
            user=request.user,
            files=files,
            actions=actions,
            data=form.cleaned_data
        )

        return Response({
            "success": True,
            "documents": len(result["documents"]),
            "versions": len(result["versions"])
        })
