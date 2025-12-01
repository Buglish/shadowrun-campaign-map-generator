from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import logging
from .models import (
    Character, Quality, CharacterQuality, Gear, CharacterGear, CharacterSkill,
    CharacterSpell, CharacterAdeptPower, CharacterComplexForm, Contact, Language
)
from .forms import (
    CharacterBasicInfoForm, CharacterRoleHistoryForm, CharacterPrioritiesForm,
    CharacterQualitySelectionForm, CharacterAttributesForm, CharacterKarmaForm,
    CharacterGearSelectionForm, CharacterFinishingForm, NPCGeneratorForm, CharacterSkillForm,
    CharacterSpellForm, CharacterAdeptPowerForm, CharacterComplexFormForm, CharacterContactForm,
    CharacterLanguageForm
)
from .npc_generator import generate_npc_data, ARCHETYPE_TEMPLATES, THREAT_LEVELS

logger = logging.getLogger(__name__)


@login_required
def character_list(request):
    """List all characters for the current user, separated into PCs and NPCs"""
    try:
        # Separate player characters and NPCs
        player_characters = Character.objects.filter(user=request.user, is_npc=False)
        npcs = Character.objects.filter(user=request.user, is_npc=True)

        context = {
            'player_characters': player_characters,
            'npcs': npcs,
            'total_characters': player_characters.count() + npcs.count()
        }
        logger.info(f"User {request.user.username} accessed character list")
        return render(request, 'characters/list.html', context)
    except Exception as e:
        logger.error(f"Error in character_list for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred while loading characters.')
        return redirect('home')


@login_required
def character_create(request):
    """Start character creation wizard"""
    try:
        # Clear any existing session data
        request.session['character_creation'] = {}
        request.session['character_id'] = None
        logger.info(f"User {request.user.username} started character creation")
        return redirect('characters:create_step1')
    except Exception as e:
        logger.error(f"Error in character_create for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('characters:list')


@login_required
def character_create_step1(request):
    """Step 1: Basic Info - Name, Race, Archetype"""
    try:
        character_id = request.session.get('character_id')
        character = None
        if character_id:
            character = get_object_or_404(Character, pk=character_id, user=request.user)

        if request.method == 'POST':
            form = CharacterBasicInfoForm(request.POST, instance=character)
            if form.is_valid():
                try:
                    character = form.save(commit=False)
                    character.user = request.user
                    character.creation_step = 1
                    character.save()
                    request.session['character_id'] = character.id
                    logger.info(f"User {request.user.username} completed character creation step 1 for character {character.id}")
                    messages.success(request, 'Basic information saved!')
                    return redirect('characters:create_step2')
                except Exception as e:
                    logger.error(f"Error saving character step 1 for user {request.user.username}: {str(e)}", exc_info=True)
                    messages.error(request, 'Failed to save character. Please try again.')
        else:
            form = CharacterBasicInfoForm(instance=character)

        context = {'form': form, 'step': 1, 'step_name': 'Basic Information'}
        return render(request, 'characters/create_step.html', context)
    except Exception as e:
        logger.error(f"Error in character_create_step1 for user {request.user.username}: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('characters:list')


@login_required
def character_create_step2(request):
    """Step 2: Role and History"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterRoleHistoryForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 2
            character.save()
            messages.success(request, 'Role and history saved!')
            return redirect('characters:create_step3')
    else:
        form = CharacterRoleHistoryForm(instance=character)

    context = {'form': form, 'step': 2, 'step_name': 'Role & History', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step3(request):
    """Step 3: Priorities"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterPrioritiesForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 3
            character.save()
            messages.success(request, 'Priorities set!')
            return redirect('characters:create_step4')
    else:
        form = CharacterPrioritiesForm(instance=character)

    context = {'form': form, 'step': 3, 'step_name': 'Priorities', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step4(request):
    """Step 4: Qualities Selection"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterQualitySelectionForm(request.POST)
        if form.is_valid():
            # Clear existing qualities
            CharacterQuality.objects.filter(character=character).delete()

            # Add selected positive qualities
            for quality in form.cleaned_data['positive_qualities']:
                CharacterQuality.objects.create(character=character, quality=quality)

            # Add selected negative qualities
            for quality in form.cleaned_data['negative_qualities']:
                CharacterQuality.objects.create(character=character, quality=quality)

            character.creation_step = 4
            character.save()
            messages.success(request, 'Qualities selected!')
            return redirect('characters:create_step5')
    else:
        # Pre-populate with existing selections
        existing_qualities = character.qualities.all()
        positive_ids = [cq.quality.id for cq in existing_qualities if cq.quality.quality_type == 'positive']
        negative_ids = [cq.quality.id for cq in existing_qualities if cq.quality.quality_type == 'negative']

        form = CharacterQualitySelectionForm(initial={
            'positive_qualities': positive_ids,
            'negative_qualities': negative_ids,
        })

    context = {'form': form, 'step': 4, 'step_name': 'Qualities', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step5(request):
    """Step 5: Attributes"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterAttributesForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 5
            character.save()
            messages.success(request, 'Attributes allocated!')
            return redirect('characters:create_step6')
    else:
        form = CharacterAttributesForm(instance=character)

    context = {'form': form, 'step': 5, 'step_name': 'Attributes', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step6(request):
    """Step 6: Karma Customization"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterKarmaForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 6
            character.save()
            messages.success(request, 'Karma customized!')
            return redirect('characters:create_step7')
    else:
        form = CharacterKarmaForm(instance=character)

    context = {'form': form, 'step': 6, 'step_name': 'Karma', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step7(request):
    """Step 7: Gear Selection"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterGearSelectionForm(request.POST)
        if form.is_valid():
            # Clear existing gear
            CharacterGear.objects.filter(character=character).delete()

            # Add selected gear
            for gear_item in form.cleaned_data['gear_items']:
                CharacterGear.objects.create(
                    character=character,
                    gear=gear_item,
                    quantity=1
                )

            character.creation_step = 7
            character.save()
            messages.success(request, 'Gear selected!')
            return redirect('characters:create_step8')
    else:
        # Pre-populate with existing gear
        existing_gear = character.equipment.all()
        gear_ids = [cg.gear.id for cg in existing_gear]
        form = CharacterGearSelectionForm(initial={'gear_items': gear_ids})

    context = {'form': form, 'step': 7, 'step_name': 'Gear', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_create_step8(request):
    """Step 8: Finishing Touches"""
    character_id = request.session.get('character_id')
    if not character_id:
        return redirect('characters:create_step1')

    character = get_object_or_404(Character, pk=character_id, user=request.user)

    if request.method == 'POST':
        form = CharacterFinishingForm(request.POST, instance=character)
        if form.is_valid():
            character = form.save(commit=False)
            character.creation_step = 8
            character.is_complete = True
            character.save()
            messages.success(request, f'Character {character.name} created successfully!')

            # Clear session
            request.session.pop('character_id', None)
            request.session.pop('character_creation', None)

            return redirect('characters:detail', pk=character.id)
    else:
        form = CharacterFinishingForm(instance=character)

    context = {'form': form, 'step': 8, 'step_name': 'Finishing Touches', 'character': character}
    return render(request, 'characters/create_step.html', context)


@login_required
def character_detail(request, pk):
    """View character details"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    qualities = character.qualities.select_related('quality').all()
    equipment = character.equipment.select_related('gear').all()

    context = {
        'character': character,
        'qualities': qualities,
        'equipment': equipment,
    }
    return render(request, 'characters/detail.html', context)


@login_required
def character_advanced_sheet(request, pk):
    """View comprehensive advanced character sheet with all calculated stats"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    context = {
        'character': character,
    }
    return render(request, 'characters/advanced_sheet.html', context)


@login_required
def character_edit(request, pk):
    """Edit a character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    # Set up wizard for editing
    request.session['character_id'] = character.id
    return redirect('characters:create_step1')


@login_required
def character_delete(request, pk):
    """Delete a character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        character_name = character.name
        character.delete()
        messages.success(request, f'Character {character_name} deleted successfully.')
        return redirect('characters:list')

    context = {'character': character}
    return render(request, 'characters/delete_confirm.html', context)


@login_required
def npc_generator(request):
    """Generate random NPCs based on parameters"""
    generated_npcs = []

    if request.method == 'POST':
        form = NPCGeneratorForm(request.POST)

        if form.is_valid():
            try:
                # Get form data
                archetype = form.cleaned_data['archetype']
                threat_level = form.cleaned_data['threat_level']
                race = form.cleaned_data.get('race') or None
                use_alias = form.cleaned_data.get('use_alias', True)
                quantity = form.cleaned_data.get('quantity', 1)

                # Generate NPCs
                for i in range(quantity):
                    npc_data = generate_npc_data(
                        archetype_key=archetype,
                        threat_level=threat_level,
                        race=race if race else None,
                        use_alias=use_alias
                    )

                    # Create NPC character
                    with transaction.atomic():
                        # Add is_npc flag to mark this as an NPC
                        npc_data['is_npc'] = True
                        npc = Character.objects.create(
                            user=request.user,
                            **npc_data
                        )
                        generated_npcs.append(npc)

                # Success message
                if quantity == 1:
                    messages.success(
                        request,
                        f'Successfully generated NPC: {generated_npcs[0].name}!'
                    )
                    return redirect('characters:detail', pk=generated_npcs[0].pk)
                else:
                    messages.success(
                        request,
                        f'Successfully generated {quantity} NPCs!'
                    )
                    # Stay on page to show all generated NPCs

            except Exception as e:
                logger.error(f"Error generating NPC: {str(e)}", exc_info=True)
                messages.error(request, f'Error generating NPC: {str(e)}')
                form = NPCGeneratorForm()  # Reset form

    else:
        form = NPCGeneratorForm()

    context = {
        'form': form,
        'generated_npcs': generated_npcs,
        'archetype_templates': ARCHETYPE_TEMPLATES,
        'threat_levels': THREAT_LEVELS,
    }

    return render(request, 'characters/npc_generator.html', context)


@login_required
def character_skills_manage(request, pk):
    """Manage character skills - view all skills with dice pools"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    # Get all skills grouped by category
    skills_by_category = {}
    for skill in character.skills.select_related('skill').all():
        category = skill.skill.get_category_display()
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)

    context = {
        'character': character,
        'skills_by_category': skills_by_category,
    }

    return render(request, 'characters/skills_manage.html', context)


@login_required
def character_skill_add(request, pk):
    """Add a new skill to character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CharacterSkillForm(request.POST, character=character)
        if form.is_valid():
            character_skill = form.save(commit=False)
            character_skill.character = character
            character_skill.save()
            messages.success(request, f'Added skill: {character_skill.skill.name}')
            return redirect('characters:skills_manage', pk=character.pk)
    else:
        form = CharacterSkillForm(character=character)

    context = {
        'character': character,
        'form': form,
        'action': 'Add',
    }

    return render(request, 'characters/skill_form.html', context)


@login_required
def character_skill_edit(request, pk, skill_pk):
    """Edit an existing character skill"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_skill = get_object_or_404(CharacterSkill, pk=skill_pk, character=character)

    if request.method == 'POST':
        form = CharacterSkillForm(request.POST, instance=character_skill, character=character)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated skill: {character_skill.skill.name}')
            return redirect('characters:skills_manage', pk=character.pk)
    else:
        form = CharacterSkillForm(instance=character_skill, character=character)

    context = {
        'character': character,
        'form': form,
        'character_skill': character_skill,
        'action': 'Edit',
    }

    return render(request, 'characters/skill_form.html', context)


@login_required
def character_skill_delete(request, pk, skill_pk):
    """Delete a character skill"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_skill = get_object_or_404(CharacterSkill, pk=skill_pk, character=character)

    if request.method == 'POST':
        skill_name = character_skill.skill.name
        character_skill.delete()
        messages.success(request, f'Removed skill: {skill_name}')
        return redirect('characters:skills_manage', pk=character.pk)

    context = {
        'character': character,
        'character_skill': character_skill,
    }

    return render(request, 'characters/skill_delete_confirm.html', context)


# =========================
# SPELLS MANAGEMENT VIEWS
# =========================

@login_required
def character_spells_manage(request, pk):
    """Manage character spells - view all spells grouped by category"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    # Get all spells grouped by category
    spells_by_category = {}
    for char_spell in character.spells.select_related('spell').all():
        category = char_spell.spell.get_category_display()
        if category not in spells_by_category:
            spells_by_category[category] = []
        spells_by_category[category].append(char_spell)

    context = {
        'character': character,
        'spells_by_category': spells_by_category,
    }

    return render(request, 'characters/spells_manage.html', context)


@login_required
def character_spell_add(request, pk):
    """Add a new spell to character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CharacterSpellForm(request.POST, character=character)
        if form.is_valid():
            character_spell = form.save(commit=False)
            character_spell.character = character
            character_spell.save()
            messages.success(request, f'Added spell: {character_spell.spell.name}')
            return redirect('characters:spells_manage', pk=character.pk)
    else:
        form = CharacterSpellForm(character=character)

    context = {
        'character': character,
        'form': form,
        'action': 'Add',
    }

    return render(request, 'characters/spell_form.html', context)


@login_required
def character_spell_edit(request, pk, spell_pk):
    """Edit an existing character spell"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_spell = get_object_or_404(CharacterSpell, pk=spell_pk, character=character)

    if request.method == 'POST':
        form = CharacterSpellForm(request.POST, instance=character_spell, character=character)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated spell: {character_spell.spell.name}')
            return redirect('characters:spells_manage', pk=character.pk)
    else:
        form = CharacterSpellForm(instance=character_spell, character=character)

    context = {
        'character': character,
        'form': form,
        'character_spell': character_spell,
        'action': 'Edit',
    }

    return render(request, 'characters/spell_form.html', context)


@login_required
def character_spell_delete(request, pk, spell_pk):
    """Delete a character spell"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_spell = get_object_or_404(CharacterSpell, pk=spell_pk, character=character)

    if request.method == 'POST':
        spell_name = character_spell.spell.name
        character_spell.delete()
        messages.success(request, f'Removed spell: {spell_name}')
        return redirect('characters:spells_manage', pk=character.pk)

    context = {
        'character': character,
        'character_spell': character_spell,
    }

    return render(request, 'characters/spell_delete_confirm.html', context)


# =========================
# ADEPT POWERS MANAGEMENT VIEWS
# =========================

@login_required
def character_adept_powers_manage(request, pk):
    """Manage character adept powers - view all powers"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    # Get all adept powers
    adept_powers = character.adept_powers.select_related('power').all()

    context = {
        'character': character,
        'adept_powers': adept_powers,
    }

    return render(request, 'characters/adept_powers_manage.html', context)


@login_required
def character_adept_power_add(request, pk):
    """Add a new adept power to character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CharacterAdeptPowerForm(request.POST, character=character)
        if form.is_valid():
            character_power = form.save(commit=False)
            character_power.character = character
            character_power.save()
            messages.success(request, f'Added adept power: {character_power.power.name}')
            return redirect('characters:adept_powers_manage', pk=character.pk)
    else:
        form = CharacterAdeptPowerForm(character=character)

    context = {
        'character': character,
        'form': form,
        'action': 'Add',
    }

    return render(request, 'characters/adept_power_form.html', context)


@login_required
def character_adept_power_edit(request, pk, power_pk):
    """Edit an existing character adept power"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_power = get_object_or_404(CharacterAdeptPower, pk=power_pk, character=character)

    if request.method == 'POST':
        form = CharacterAdeptPowerForm(request.POST, instance=character_power, character=character)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated adept power: {character_power.power.name}')
            return redirect('characters:adept_powers_manage', pk=character.pk)
    else:
        form = CharacterAdeptPowerForm(instance=character_power, character=character)

    context = {
        'character': character,
        'form': form,
        'character_power': character_power,
        'action': 'Edit',
    }

    return render(request, 'characters/adept_power_form.html', context)


@login_required
def character_adept_power_delete(request, pk, power_pk):
    """Delete a character adept power"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_power = get_object_or_404(CharacterAdeptPower, pk=power_pk, character=character)

    if request.method == 'POST':
        power_name = character_power.power.name
        character_power.delete()
        messages.success(request, f'Removed adept power: {power_name}')
        return redirect('characters:adept_powers_manage', pk=character.pk)

    context = {
        'character': character,
        'character_power': character_power,
    }

    return render(request, 'characters/adept_power_delete_confirm.html', context)


# =========================
# COMPLEX FORMS MANAGEMENT VIEWS
# =========================

@login_required
def character_complex_forms_manage(request, pk):
    """Manage character complex forms - view all forms"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    # Get all complex forms
    complex_forms = character.complex_forms.select_related('form').all()

    context = {
        'character': character,
        'complex_forms': complex_forms,
    }

    return render(request, 'characters/complex_forms_manage.html', context)


@login_required
def character_complex_form_add(request, pk):
    """Add a new complex form to character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CharacterComplexFormForm(request.POST, character=character)
        if form.is_valid():
            character_form = form.save(commit=False)
            character_form.character = character
            character_form.save()
            messages.success(request, f'Added complex form: {character_form.form.name}')
            return redirect('characters:complex_forms_manage', pk=character.pk)
    else:
        form = CharacterComplexFormForm(character=character)

    context = {
        'character': character,
        'form': form,
        'action': 'Add',
    }

    return render(request, 'characters/complex_form_form.html', context)


@login_required
def character_complex_form_edit(request, pk, form_pk):
    """Edit an existing character complex form"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_form = get_object_or_404(CharacterComplexForm, pk=form_pk, character=character)

    if request.method == 'POST':
        form = CharacterComplexFormForm(request.POST, instance=character_form, character=character)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated complex form: {character_form.form.name}')
            return redirect('characters:complex_forms_manage', pk=character.pk)
    else:
        form = CharacterComplexFormForm(instance=character_form, character=character)

    context = {
        'character': character,
        'form': form,
        'character_form': character_form,
        'action': 'Edit',
    }

    return render(request, 'characters/complex_form_form.html', context)


@login_required
def character_complex_form_delete(request, pk, form_pk):
    """Delete a character complex form"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    character_form = get_object_or_404(CharacterComplexForm, pk=form_pk, character=character)

    if request.method == 'POST':
        form_name = character_form.form.name
        character_form.delete()
        messages.success(request, f'Removed complex form: {form_name}')
        return redirect('characters:complex_forms_manage', pk=character.pk)

    context = {
        'character': character,
        'character_form': character_form,
    }

    return render(request, 'characters/complex_form_delete_confirm.html', context)


# =========================
# CONTACTS MANAGEMENT VIEWS
# =========================

@login_required
def character_contacts_manage(request, pk):
    """Manage character contacts - view all contacts"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    contacts = character.contacts.all().order_by('name')

    context = {
        'character': character,
        'contacts': contacts,
    }

    return render(request, 'characters/contacts_manage.html', context)


@login_required
def character_contact_add(request, pk):
    """Add a new contact to character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CharacterContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.character = character
            contact.save()
            messages.success(request, f'Added contact: {contact.name}')
            return redirect('characters:contacts_manage', pk=character.pk)
    else:
        form = CharacterContactForm()

    context = {
        'character': character,
        'form': form,
        'action': 'Add',
    }

    return render(request, 'characters/contact_form.html', context)


@login_required
def character_contact_edit(request, pk, contact_pk):
    """Edit an existing character contact"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    contact = get_object_or_404(Contact, pk=contact_pk, character=character)

    if request.method == 'POST':
        form = CharacterContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated contact: {contact.name}')
            return redirect('characters:contacts_manage', pk=character.pk)
    else:
        form = CharacterContactForm(instance=contact)

    context = {
        'character': character,
        'form': form,
        'contact': contact,
        'action': 'Edit',
    }

    return render(request, 'characters/contact_form.html', context)


@login_required
def character_contact_delete(request, pk, contact_pk):
    """Delete a character contact"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    contact = get_object_or_404(Contact, pk=contact_pk, character=character)

    if request.method == 'POST':
        contact_name = contact.name
        contact.delete()
        messages.success(request, f'Removed contact: {contact_name}')
        return redirect('characters:contacts_manage', pk=character.pk)

    context = {
        'character': character,
        'contact': contact,
    }

    return render(request, 'characters/contact_delete_confirm.html', context)


# ===== Language Management Views =====

@login_required
def character_languages_manage(request, pk):
    """Manage character languages - view all languages"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    languages = character.languages.all().order_by('name')

    context = {
        'character': character,
        'languages': languages,
    }

    return render(request, 'characters/languages_manage.html', context)


@login_required
def character_language_add(request, pk):
    """Add a new language to character"""
    character = get_object_or_404(Character, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CharacterLanguageForm(request.POST)
        if form.is_valid():
            language = form.save(commit=False)
            language.character = character
            language.save()
            messages.success(request, f'Added language: {language.name}')
            return redirect('characters:languages_manage', pk=character.pk)
    else:
        form = CharacterLanguageForm()

    context = {
        'character': character,
        'form': form,
        'action': 'Add',
    }

    return render(request, 'characters/language_form.html', context)


@login_required
def character_language_edit(request, pk, language_pk):
    """Edit an existing character language"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    language = get_object_or_404(Language, pk=language_pk, character=character)

    if request.method == 'POST':
        form = CharacterLanguageForm(request.POST, instance=language)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated language: {language.name}')
            return redirect('characters:languages_manage', pk=character.pk)
    else:
        form = CharacterLanguageForm(instance=language)

    context = {
        'character': character,
        'form': form,
        'language': language,
        'action': 'Edit',
    }

    return render(request, 'characters/language_form.html', context)


@login_required
def character_language_delete(request, pk, language_pk):
    """Delete a character language"""
    character = get_object_or_404(Character, pk=pk, user=request.user)
    language = get_object_or_404(Language, pk=language_pk, character=character)

    if request.method == 'POST':
        language_name = language.name
        language.delete()
        messages.success(request, f'Removed language: {language_name}')
        return redirect('characters:languages_manage', pk=character.pk)

    context = {
        'character': character,
        'language': language,
    }

    return render(request, 'characters/language_delete_confirm.html', context)
