from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
    path('', views.character_list, name='list'),
    path('create/', views.character_create, name='create'),
    path('generate/', views.npc_generator, name='npc_generator'),

    # Character creation wizard steps
    path('create/step1/', views.character_create_step1, name='create_step1'),
    path('create/step2/', views.character_create_step2, name='create_step2'),
    path('create/step3/', views.character_create_step3, name='create_step3'),
    path('create/step4/', views.character_create_step4, name='create_step4'),
    path('create/step5/', views.character_create_step5, name='create_step5'),
    path('create/step6/', views.character_create_step6, name='create_step6'),
    path('create/step7/', views.character_create_step7, name='create_step7'),
    path('create/step8/', views.character_create_step8, name='create_step8'),

    # Character management
    path('<int:pk>/', views.character_detail, name='detail'),
    path('<int:pk>/advanced/', views.character_advanced_sheet, name='advanced_sheet'),
    path('<int:pk>/edit/', views.character_edit, name='edit'),
    path('<int:pk>/delete/', views.character_delete, name='delete'),

    # Skill management
    path('<int:pk>/skills/', views.character_skills_manage, name='skills_manage'),
    path('<int:pk>/skills/add/', views.character_skill_add, name='skill_add'),
    path('<int:pk>/skills/<int:skill_pk>/edit/', views.character_skill_edit, name='skill_edit'),
    path('<int:pk>/skills/<int:skill_pk>/delete/', views.character_skill_delete, name='skill_delete'),

    # Spell management
    path('<int:pk>/spells/', views.character_spells_manage, name='spells_manage'),
    path('<int:pk>/spells/add/', views.character_spell_add, name='spell_add'),
    path('<int:pk>/spells/<int:spell_pk>/edit/', views.character_spell_edit, name='spell_edit'),
    path('<int:pk>/spells/<int:spell_pk>/delete/', views.character_spell_delete, name='spell_delete'),

    # Adept power management
    path('<int:pk>/adept-powers/', views.character_adept_powers_manage, name='adept_powers_manage'),
    path('<int:pk>/adept-powers/add/', views.character_adept_power_add, name='adept_power_add'),
    path('<int:pk>/adept-powers/<int:power_pk>/edit/', views.character_adept_power_edit, name='adept_power_edit'),
    path('<int:pk>/adept-powers/<int:power_pk>/delete/', views.character_adept_power_delete, name='adept_power_delete'),

    # Complex form management
    path('<int:pk>/complex-forms/', views.character_complex_forms_manage, name='complex_forms_manage'),
    path('<int:pk>/complex-forms/add/', views.character_complex_form_add, name='complex_form_add'),
    path('<int:pk>/complex-forms/<int:form_pk>/edit/', views.character_complex_form_edit, name='complex_form_edit'),
    path('<int:pk>/complex-forms/<int:form_pk>/delete/', views.character_complex_form_delete, name='complex_form_delete'),

    # Contact management
    path('<int:pk>/contacts/', views.character_contacts_manage, name='contacts_manage'),
    path('<int:pk>/contacts/add/', views.character_contact_add, name='contact_add'),
    path('<int:pk>/contacts/<int:contact_pk>/edit/', views.character_contact_edit, name='contact_edit'),
    path('<int:pk>/contacts/<int:contact_pk>/delete/', views.character_contact_delete, name='contact_delete'),

    # Language management
    path('<int:pk>/languages/', views.character_languages_manage, name='languages_manage'),
    path('<int:pk>/languages/add/', views.character_language_add, name='language_add'),
    path('<int:pk>/languages/<int:language_pk>/edit/', views.character_language_edit, name='language_edit'),
    path('<int:pk>/languages/<int:language_pk>/delete/', views.character_language_delete, name='language_delete'),
]
