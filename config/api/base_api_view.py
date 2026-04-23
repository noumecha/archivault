# config/api/base_api_view.py

from rest_framework import status, pagination
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import FieldDoesNotExist


class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class BaseAPIView(GenericAPIView):
    """
    Version API de BaseCRUDView.
    Utilise DRF pour fournir des endpoints JSON robustes.
    """

    model = None
    serializer_class = None
    search_fields = []
    filter_fields = []
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    action_map = {
        'list': 'list_action',
        'retrieve': 'retrieve_action',
        'create': 'create_action',
        'update': 'update_action',
        'delete': 'delete_action',
    }

    # ─────────────────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ─────────────────────────────────────────────────────────────────────────

    def _get_query_params(self):
        """
        Récupère les query params de manière compatible DRF/Django.
        ✅ Fonctionne avec DRF Request ET Django Request
        """
        if hasattr(self.request, 'query_params'):
            # DRF Request
            return self.request.query_params
        else:
            # Django Request (fallback)
            return self.request.GET

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET
    # ─────────────────────────────────────────────────────────────────────────

    def get_queryset(self):
        """
        Retourne le queryset avec filtres et recherche appliqués.
        Compatible DRF et Django.
        """
        if self.model is None:
            return super().get_queryset()

        # Queryset de base, trié par date de création si le champ existe
        queryset = self.model.objects.all()
        try:
            self.model._meta.get_field('Date_creation')
            queryset = queryset.order_by('-Date_creation')
        except FieldDoesNotExist:
            pass

        # ✅ Récupère les query params de manière sécurisée
        query_params = self._get_query_params()

        # 1. Filtres dynamiques exacts (query_params)
        filters = {}
        for field in self.filter_fields:
            value = query_params.get(field)
            if value:
                filters[field] = value

        if filters:
            queryset = queryset.filter(**filters)

        # 2. Recherche textuelle (__icontains)
        search_query = query_params.get('search', '').strip()
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)

        return queryset

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS CRUD
    # ─────────────────────────────────────────────────────────────────────────

    def list_action(self, request, *args, **kwargs):
        """Action pour lister les objets avec pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def retrieve_action(self, request, pk=None, *args, **kwargs):
        """Action pour récupérer un seul objet."""
        instance = get_object_or_404(self.model, pk=pk)
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def create_action(self, request, *args, **kwargs):
        """Action pour créer un objet."""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            save_kwargs = {}
            if hasattr(self.model, 'cree_par'):
                save_kwargs['cree_par'] = request.user

            obj = serializer.save(**save_kwargs)

            return Response({
                'success': True,
                'message': f'{self.model._meta.verbose_name.title()} enregistré avec succès',
                'data': self.get_serializer(obj).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': 'Erreur lors de l\'enregistrement',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update_action(self, request, pk=None, *args, **kwargs):
        """Action pour mettre à jour un objet."""
        instance = get_object_or_404(self.model, pk=pk)
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            save_kwargs = {}
            if hasattr(self.model, 'modifier_par'):
                save_kwargs['modifier_par'] = request.user

            serializer.save(**save_kwargs)
            return Response({
                'success': True,
                'message': f'{self.model._meta.verbose_name.title()} mis à jour avec succès',
                'data': self.get_serializer(instance).data
            })

        return Response({
            'success': False,
            'message': 'Erreur lors de la mise à jour',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Action pour supprimer un objet."""
        instance = get_object_or_404(self.model, pk=pk)
        instance.delete()
        return Response({
            'success': True,
            'message': f'{self.model._meta.verbose_name.title()} supprimé avec succès'
        }, status=status.HTTP_200_OK)

    # ─────────────────────────────────────────────────────────────────────────
    # DISPATCH
    # ─────────────────────────────────────────────────────────────────────────

    def dispatch(self, request, *args, **kwargs):
        """
        Corrigé pour supporter DRF Request (query_params, data, etc.)
        """

        # ✅ IMPORTANT : transformation Django → DRF Request
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request

        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)

            action = kwargs.pop('action', None)

            # 🔹 Actions standards
            if action in self.action_map:
                handler_name = self.action_map[action]
                handler = getattr(self, handler_name)
                response = handler(request, *args, **kwargs)

            # 🔹 Actions custom
            elif action in getattr(self, 'custom_actions', {}):
                method_name = self.custom_actions[action]
                method = getattr(self, method_name, None)

                if not callable(method):
                    return Response({
                        'success': False,
                        'message': f"Méthode '{method_name}' non implémentée."
                    }, status=500)

                response = method(request, *args, **kwargs)

            else:
                response = super().dispatch(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        return self.finalize_response(request, response, *args, **kwargs)
