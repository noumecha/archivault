from django.views.generic import ListView
from django.views.generic import CreateView, TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import *
from .serializers import SousTypeDocumentSerializer
from .forms import *
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from config.views import BaseCRUDView

#occupant view
class RegleClassementView(BaseCRUDView):
    model = RegleClassement
    form_class = RegleClassementsForm
    list_route = 'regleclassement_list'
    list_template = 'reglesclassements_list.html'
    partial_template = 'partials/reglesclassements_partial.html'
    context_object_name = 'reglesclassements'
    search_fields = ["nom","description_regleclassement"]

class NiveauAccesDocumentView(BaseCRUDView):
    model = NiveauAccesDocument
    form_class = NiveauAccesDocumentsForm
    list_route = 'niveauaccess_list'
    list_template = 'niveauaccesss_list.html'
    partial_template = 'partials/niveauaccesss_partial.html'
    context_object_name = 'niveauaccesss'
    search_fields = ["niveau","description_niveauaccess"]

class SousTypeDocumentView(BaseCRUDView):
    model = SousTypeDocument
    form_class = SousTypeDocumentsForm
    list_route = 'soustypedocument_list'
    list_template = 'soustypedocument_list.html'
    partial_template = 'partials/soustypedocument_partial.html'
    context_object_name = 'soustypedocuments'
    search_fields = ["libelle","description_soustypedocument"]

class ThemeListView(BaseCRUDView):
    model = Theme
    form_class = ThemesForm
    list_route = 'themes_list'
    list_template = 'themes_list.html'
    partial_template = 'partials/themes_partial.html'
    context_object_name = 'themes'
    search_fields = ["libelle","description_theme"]

class TypeDocumentView(BaseCRUDView):
    model = TypeDocument
    form_class = TypeDocumentsForm
    list_route = 'typedocument_list'
    list_template = 'typedocuments_list.html'
    partial_template = 'partials/typedocuments_partial.html'
    context_object_name = 'typedocuments'
    search_fields = ["libelle","description_typedocument"]

class DocumentView(BaseCRUDView):
    model = Document
    form_class = DocumentsForm
    list_route = 'documents_list'
    list_template = 'documents_list.html'
    partial_template = 'partials/documents_partial.html'
    context_object_name = 'documents'
    search_fields = [
        "titre",
        "fichier",
        "type_document",
        "sous_type",
        "theme",
        "cellule",
        "etat",
        "niveau_acces",
        "profil_document",
        "regles_classement",
        "metadonnees",
        "cree_par",
    ]

# documents view
class DocumentListView(ListView):
    model = Document
    template_name = "documents/list.html"
    context_object_name = 'documents'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = Document.objects.all()
        context["form"] = DocumentsForm()
        return context

    def post(self, request, *args, **kwargs):
        document_form = DocumentsForm(request.POST)
        if document_form.is_valid():
            document_form.save()
            return JsonResponse({
                'success': True,
                'message' : 'Document enregistré avec succès'
            })
        else:
            return JsonResponse({
                'success': False,
                'message' : f"Erreur lors de l\'enregistrement du document : {str(document_form.errors)}",
            })

# getting documents
def get_documents(request, **kwargs):
    if request.method == 'GET':
        #query = request.GET.get('searchFilter', '').strip()
        documents = Document.objects.get_queryset()
        #documents = Document.objects.filter()
        # applying filters
        if request.GET.get('type'):
            documents = documents.filter(type_document_id=request.GET.get('type'))
        if request.GET.get('theme'):
            documents = documents.filter(theme_id=request.GET.get('theme'))
        if request.GET.get('statut'):
            documents = documents.filter(etat=request.GET.get('statut'))
        if request.GET.get('searchFilter'):
            documents = documents.filter(titre__contains=request.GET.get('searchFilter'))
        datas = render_to_string(
            'partials/documents_partial.html',
            {'documents': documents},
            request=request
        )
        return JsonResponse({'success': True, 'html': datas})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

# update documents
def update_documents(request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            document = get_object_or_404(Document, pk=pk)
            document_form = DocumentsForm(request.POST, instance=document)
            if document_form.is_valid():
                document = document_form.save()
                return JsonResponse({
                    'success': True,
                    'message' : 'Document mis à jour avec succès'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message' : f"Erreur lors de la mise à jour du document : {str(document_form.errors)}",
                })
        else:
            return JsonResponse({'success': False, 'message': 'Document non trouvé'}, status=404)

# manage document deletion
def document_delete_view(request, pk):
    try:
        document = get_object_or_404(Document, pk=pk)
        document.delete()
        messages.success(request, "Document supprimé avec succès!")
        return redirect('documents:documents')
    except Document.DoesNotExist:
        messages.success(request, "Document non trouvé !")
        return redirect('documents:documents')

def document_form_view(request, pk=None):
    if pk:
        document = get_object_or_404(Document, pk=pk) if pk else None
        form = DocumentsForm(instance=document)
    else:
        form = DocumentsForm()
    html = render_to_string('layouts/form.html', {'form': form}, request=request)
    return JsonResponse({'success': True, 'html': html})

class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentsForm
    template_name = 'layouts/form.html'
    success_url = reverse_lazy('documents:list')

    def form_valid(self, form):
        form.instance.cree_par = self.request.user
        return super().form_valid(form)

class DocumentUploadAPI(APIView):
    def post(self, request):
        form = DocumentsForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.cree_par = request.user
            document.save()
            return Response({
                'status' : 'success',
                'id': document.id
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status' : 'error',
            'errors' : form.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class SousTypesAPIView(APIView):
    def get(self, request, type_id):
        sous_types = SousTypeDocument.objects.filter(type_document_id=type_id)
        serializer = SousTypeDocumentSerializer(sous_types, many=True)
        return Response(serializer.data)
