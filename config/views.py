from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from config.utils.utils import generates_filters
from web_project import TemplateLayout
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import models
from django.core.paginator import Paginator

#generic view for basic operation
class BaseCRUDView(TemplateView):
    # model and form
    model = None
    form_class = None
    formset_class = None
    # query and routes
    search_fields = []
    paginate_by = 20
    list_route = None
    fields = []
    filters = []
    # templates
    headers = []
    partial_template = 'layout/partials/crud_table.html'
    list_template = None
    form_template = 'layout/form_template.html'
    manage_template = 'layout/layout_manage.html'
    # names and objects
    context_object_name = 'objects'
    object_name = None
    object_label = None
    # manage vars
    delete_url = ""
    manage_url = ""
    manage_menu = []

    def get(self, request, *args, **kwargs):
        # Si une section est présente dans les kwargs -> page de management
        if "section" in kwargs:
            return self.dynamic_manage_view(request, **kwargs)

        # Sinon comportement CRUD normal
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["form"] = self.form_class
        context['filters'] = generates_filters(self.filters)
        return context

    def get_queryset(self, search_query=None):
        queryset = self.model.objects.all().order_by('-Date_creation')
        request = getattr(self, 'request', None)
        if not request:
            return queryset
        # 🔍 1. Appliquer les filtres dynamiques (ex: cellule, role, statut, etc.)
        filters = {}
        for key, value in request.GET.items():
            if key in ['search', 'page']:  # on ignore la recherche et la pagination
                continue
            if value:  # ignorer les valeurs vides
                filters[key] = value
        if filters:
            queryset = queryset.filter(**filters)
        # 🔎 2. Appliquer la recherche textuelle si elle existe
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
        return queryset.order_by('-Date_creation')[:100]

    def get_form_kwargs(self, request, **kwargs):
        return {}

    def get_form_view(self, request, pk=None, **kwargs):
        instance = get_object_or_404(self.model, pk=pk) if pk else None
        form = self.form_class(
            instance=instance,
            **self.get_form_kwargs(request, **kwargs)
        )
        formsets = {
            name: formset_class(instance=instance)
            for name, formset_class in getattr(self, "formsets_classes", {}).items()
        }
        html = render_to_string(self.form_template, {
            'form': form,
            "formsets": formsets
        }, request=request)
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
                'objects' : page_obj,
                'page_obj': page_obj,
                'paginator': paginator,
                'headers': self.headers,
                'fields': self.fields,
                'delete_url': self.delete_url,
                'manage_url': self.manage_url,
                'object_name': self.object_name or self.model._meta.verbose_name.title(),
                'object_label': self.object_label or self.model._meta.verbose_name.title(),
            },
            request=request
        )
        return JsonResponse({
            'success': True,
            'html': html,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            # Use commit=False to get the object without saving it to the DB yet
            obj = form.save(commit=False)
            # Set the creator if the attribute exists on the model
            if hasattr(obj, 'cree_par'):
                obj.cree_par = request.user
            obj.save() # Now save the object to the database
            formsets_valid = True
            for name, formset_class in getattr(self, "formsets_classes", {}).items():
                formset = formset_class(request.POST, instance=obj)
                if formset.is_valid():
                    formset.save()
                else:
                    formsets_valid = False
            form.save_m2m() # Save many-to-many relationships
            if formsets_valid:
                return JsonResponse({
                    'success': True,
                    'message': f'{self.model._meta.verbose_name} enregistré avec succès',
                    'data': {'id': obj.id, 'text': str(obj)}
                })
            return JsonResponse({
                'success': True,
                'message': f'{self.model._meta.verbose_name} enregistré avec succès',
                'data': { 'id' : obj.id, 'text': str(obj) }
            })
        # error case
        html = render_to_string(self.form_template, {'form': form}, request=request)
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'enregistrement',
            'errors' : form.errors,
            'html' : html
        })

    def update(self, request, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return JsonResponse({'success': False, 'message': 'Objet non trouvé'}, status=404)
        instance = get_object_or_404(self.model, pk=pk)
        form = self.form_class(request.POST, instance=instance)
        if form.is_valid():
            # Use commit=False to get the object without saving it to the DB yet
            obj = form.save(commit=False)
            # Set the modifier if the attribute exists on the model
            if hasattr(obj, 'modifier_par'):
                obj.modifier_par = request.user
            obj.save() # Now save the object to the database
            formsets_valid = True
            for name, formset_class in getattr(self, "formsets_classes", {}).items():
                formset = formset_class(request.POST, instance=obj)
                if formset.is_valid():
                    formset.save()
                else:
                    formsets_valid = False
            form.save_m2m() # Save many-to-many relationships
            if formsets_valid:
                return JsonResponse({
                    'success': True,
                    'message': f'{self.model._meta.verbose_name} enregistré avec succès',
                    'data': {'id': obj.id, 'text': str(obj)}
                })
            return JsonResponse({
                'success' : True,
                'message': f'{self.model._meta.verbose_name} mis à jour avec succès'
            })
        # error case
        html = render_to_string(self.form_template, {'form' : form}, request=request)#, "formset": formset
        return JsonResponse({
            'success' : False,
            'messages': f"Erreur lors de la mise à jour",
            'html' : html
        })

    def delete(self, request, pk):
        text = self.object_label or self.model._meta.verbose_name
        try:
            obj = get_object_or_404(self.model, pk=pk)
            obj.delete()
            messages.success(request, f"{text} supprimé avec succès!")
            return redirect(self.list_route)
        except obj.DoesNotExist:
            messages.success(request, f"{text} non trouvé !")
            return redirect(self.list_route)

    def partial_form_view(self, request):
        if request.method == 'POST':
            form = self.form_class(request.POST)
            if form.is_valid():
                obj = form.save()
                return JsonResponse({
                    'success' : True,
                    'id' : obj.id,
                    'text': str(obj)
                })
            html = render_to_string(self.form_template, {'form': form}, request=request)
            return JsonResponse({
                'success': False,
                'html': html
            })
        else:
            form = self.form_class()
            html = render_to_string(self.form_template, {'form': form}, request=request)
            return JsonResponse({'html': html})

    # management of model
    def get_manage_view(self, request, **kwargs):
        pk = kwargs.get("pk")
        obj = get_object_or_404(self.model, pk=pk)
        context = {
            "page_title": f"Gestion de : {obj}",
            "object": obj,
        }
        context = TemplateLayout().init(context)
        context["manage_menu"] = self.get_manage_menu(obj)
        return render(request, self.manage_template, context)

    def get_manage_menu(self, obj):
        return getattr(self, "manage_menu", [])

    def get_manage_template(self, section):
        model_name = self.model.__name__.lower()
        return f"{model_name}s/{section}.html"

    def dynamic_manage_view(self, request, **kwargs):
        pk = kwargs.get("pk")
        section = kwargs.get("section")
        obj = get_object_or_404(self.model, pk=pk)
        context = {
            "object": obj,
            "section": section,
            "page_title": f"{obj} – {section.capitalize()}",
        }
        context = TemplateLayout().init(context)
        context["manage_menu"] = self.get_manage_menu(obj)
        handler_name = f"manage_{section}"
        if hasattr(self, handler_name):
            return getattr(self, handler_name)(request, context, obj)
        template = self.get_manage_template(section)
        return render(request, template, context)

    def dispatch(self, request, *args, **kwargs):
        action = kwargs.pop('action', None)

        # 🔹 Actions CRUD standards
        if action == 'list':
            return self.get_list_data(request)
        elif action == 'form':
            return self.get_form_view(request, kwargs.get('pk'))
        elif action == 'manage':
            return self.get_manage_view(request, **kwargs)
        elif action == 'update':
            return self.update(request, **kwargs)
        elif action == 'delete':
            return self.delete(request, kwargs.get('pk'))
        elif action == 'partial_form':
            return self.partial_form_view(request)

        # 🔹 Actions personnalisées (ex: toggle_status)
        custom_actions = getattr(self, 'custom_actions', {})
        if action in custom_actions:
            method_name = custom_actions[action]
            method = getattr(self, method_name, None)
            if callable(method):
                return method(request, **kwargs)
            return JsonResponse({
                'success': False,
                'message': f"Action personnalisée '{action}' non trouvée."
            }, status=400)

        # 🔹 Action non reconnue → comportement par défaut
        return super().dispatch(request, *args, **kwargs)

# manage error : from django.shortcuts import render
def custom_permission_denied_view(request, exception):
    """
    Vue 403 personnalisée avec TemplateLayout
    """
    context = TemplateLayout.init(request, {})
    context["exception"] = "accès refusé"
    return render(request, "403.html", context=context, status=403)

def custom_page_not_found_view(request, exception):
    """
    Vue 404 personnalisée avec TemplateLayout
    """
    context = TemplateLayout.init(request, {})
    context["exception"] = "page introuvable"
    return render(request, "404.html", context=context, status=404)

def custom_server_error_view(request):
    """
    Vue 500 personnalisée avec TemplateLayout
    """
    context = TemplateLayout.init(request, {})
    return render(request, "500.html", context=context, status=500)
