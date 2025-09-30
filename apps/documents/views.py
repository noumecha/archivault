from django.views.generic import ListView
from django.views.generic import CreateView, TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Document, TypeDocument, Theme, SousTypeDocument
from .serializers import SousTypeDocumentSerializer
from .forms import DocumentsForm, TypeDocumentsForm
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

#generic view for basic operation 
class BaseCRUDView(TemplateView):
    model = None
    form_class = None
    list_template = None
    list_route = None
    partial_template = None
    form_template = 'layouts/form.html'
    context_object_name = 'objects'
    search_fields = []
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_object_name] = self.model.objects.all()
        context["form"] = self.form_class
        return context
    
    def get_queryset(self, search_query=None):
        queryset = self.model.objects.all().order_by('-Date_creation')
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects).order_by('-Date_creation')
        return queryset[:100]
    
    def get_form_view(self, request, pk=None):
        instance = get_object_or_404(self.model, pk=pk) if pk else None
        form = self.form_class(instance=instance)
        html = render_to_string(self.form_template, {'form': form}, request=request)
        return JsonResponse({'success': True, 'html':html})
    
    def get_list_data(self, request):
        search_query = request.GET.get('search', '').strip()
        queryset = self.get_queryset(search_query)
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        
        html = render_to_string(
            self.partial_template, 
            {
                self.context_object_name: page_obj,
                'page_obj': page_obj,
                'paginator': paginator
            }, 
            request=request
        )
        return JsonResponse({
            'success': True, 
            'html': html,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            if self.form_class == self.model:
                recensement = form.save(commit=False)
                immeuble = recensement.Immeuble
                last_number = self.model.objects.filter(Immeuble=immeuble).count()
                recensement.Numero = last_number + 1
                obj = form.save()
            else:
                obj = form.save()
            return JsonResponse({
                'success': True,
                'message': f'{self.model._meta.verbose_name} enregistré avec succès',
                'data': {
                    'id' : obj.id,
                    'text': str(obj)
                }
            })
        html = render_to_string(self.form_template, {'form': form}, request=request)
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'enregistrement',
            'html' : html
        })
    
    def update(self, request, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return JsonResponse({'success': False, 'message': 'Objet non trouvé'}, status=404)
        instance = get_object_or_404(self.model, pk=pk)
        form = self.form_class(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            return JsonResponse({
                'success' : True,
                'message': f'{self.model._meta.verbose_name} mis à jour avec succès'
            })
        html = render_to_string(self.form_template, {'form' : form}, request=request)
        return JsonResponse({
            'success' : False,
            'messages': f"Erreur lors de la mise à jour",
            'html' : html
        })
    
    def delete(self, request, pk):
        try:
            obj = get_object_or_404(self.model, pk=pk)
            obj.delete()
            messages.success(request, f"{self.model._meta.verbose_name} supprimé avec succès!")
            return redirect(f'{self.list_route}')
        except self.model.DoesNotExist:
            messages.success(request, f"{self.model._meta.verbose_name} non trouvé !")
            return redirect(f'{self.list_route}')

    def dispatch(self, request, *args, **kwargs):
        action = kwargs.pop('action', None)
        if action == 'list':
            return self.get_list_data(request)
        elif action == 'form':
            return self.get_form_view(request, kwargs.get('pk'))
        elif action == 'update':
            return self.update(request, **kwargs)
        elif action == 'delete':
            return self.delete(request, kwargs.get('pk'))
        elif action == 'partial_form':
            return self.partial_form_view(request)
        return super().dispatch(request, *args, **kwargs)

#occupant view
class TypeDocumentView(BaseCRUDView):
    model = TypeDocument
    form_class = TypeDocumentsForm
    list_route = 'typedocuments_list'
    list_template = 'typedocuments_list.html'
    partial_template = 'partials/typedocuments_partial.html'
    context_object_name = 'typedocuments'
    search_fields = ["libelle"]

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