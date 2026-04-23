// modules/users/users.controller.js

import { UserService } from './users.services.js';
import { UserUi } from './users.ui.js';

export const UserController = {
  async init() {
    await this.loadUsers();
    this.bindEvents();
  },

  // ─── Chargement des utilisateurs ────────────────────────────────────────

  async loadUsers(params = {}) {
    try {
      $('#table-loader').removeClass('d-none');
      const res = await UserService.fetchAll(params);
      console.log('Utilisateurs chargés:', res);
      UserUi.renderTable(res);
    } catch (err) {
      console.error('Erreur:', err);
      UserUi.showError(err.data?.message || 'Erreur serveur');
    } finally {
      $('#table-loader').addClass('d-none');
    }
  },

  // ─── Événements ─────────────────────────────────────────────────────────

  bindEvents() {
    // Recherche & filtres
    let searchTimer;
    $('#utilisateur-search-form').on('input change', 'input, select', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => this.handleSearch(), 300);
    });

    // Clear recherche
    $('#clearSearch').on('click', () => {
      $('#search').val('');
      this.loadUsers();
    });

    // Refresh
    $('#refresh-button').on('click', () => this.loadUsers());

    // Ajouter
    $('#add-button').on('click', () => UserUi.renderForm(null));

    // Éditer
    $(document).on('click', '[data-action="edit"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        const res = await UserService.fetchOne(id);
        UserUi.renderForm(res.data);
        new bootstrap.Modal(document.getElementById('create-utilisateur-modal')).show();
      } catch (err) {
        UserUi.showError('Erreur chargement utilisateur');
      }
    });

    // Basculer statut
    $(document).on('click', '[data-action="toggle-status"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      try {
        await UserService.toggleStatus(id);
        UserUi.showSuccess('Statut mis à jour');
        await this.loadUsers(this.getCurrentParams());
      } catch (err) {
        UserUi.showError(err.data?.message || 'Erreur');
      }
    });

    // Supprimer
    $(document).on('click', '[data-action="delete"]', async e => {
      e.preventDefault();
      const id = $(e.currentTarget).data('id');
      if (!confirm('Confirmer la suppression ?')) return;
      try {
        await UserService.remove(id);
        UserUi.showSuccess('Utilisateur supprimé');
        await this.loadUsers(this.getCurrentParams());
      } catch (err) {
        UserUi.showError(err.data?.message || 'Erreur');
      }
    });

    // Soumettre formulaire
    $('#utilisateurForm').on('submit', async e => {
      e.preventDefault();
      const id = $('#update-id').val();
      const data = Object.fromEntries(
        $('#utilisateurForm')
          .serializeArray()
          .map(({ name, value }) => [name, value])
      );

      await UserService.validate(data);

      try {
        if (id) {
          const rest = await UserService.update(id, data);
          UserUi.showSuccess('Utilisateur mis à jour avec succès', '#form-success');
        } else {
          const res = await UserService.create(data);
          if (!res.data?.success) {
            const errors = res.data?.errors;
            const message = errors ? Object.values(errors).flat().join(' | ') : res.data?.message;
            UserUi.showError(message, '#form-error');
            return;
          }
          UserUi.showSuccess('Utilisateur créé avec succès', '#form-success');
        }
        bootstrap.Modal.getInstance(document.getElementById('create-utilisateur-modal')).hide();
        await this.loadUsers(this.getCurrentParams());
      } catch (err) {
        const errors = err.data?.errors;
        const message = errors ? Object.values(errors).flat().join(' | ') : err.data?.message || 'Erreur serveur';
        UserUi.showError(message, '#form-error');
      }
    });
  },

  // ─── Utilitaires ────────────────────────────────────────────────────────
  handleSearch() {
    const params = Object.fromEntries(
      $('#utilisateur-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
    this.loadUsers(params);
  },

  getCurrentParams() {
    return Object.fromEntries(
      $('#utilisateur-search-form')
        .serializeArray()
        .filter(({ value }) => value)
        .map(({ name, value }) => [name, value])
    );
  }
};
