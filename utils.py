def get_choices(field, dropdown=False):
    choices = list()
    for x in field.choices:  # In CustomField model choices is a list
        choices.append((x, x))
    if dropdown and choices:
        choices.insert(0, ('', '---'))
    return choices
